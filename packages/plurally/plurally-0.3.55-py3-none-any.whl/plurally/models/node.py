import abc
import enum
import types
import uuid
from typing import Any, List, Union, get_args, get_origin

import networkx as nx
from loguru import logger
from pydantic import BaseModel, ConfigDict, EmailStr, Field, create_model

from plurally.json_utils import load_from_json_dict
from plurally.models.auto import Auto
from plurally.models.env_vars import BaseEnvVars

TYPE_ADAPTER = {
    EmailStr: str,
}


class CommitMode(enum.Enum):
    COMMIT = "commit"
    NO_COMMIT = "no_commit"


class Edge(BaseModel):
    src_node_id: str
    tgt_node_id: str
    src_handle: str
    tgt_handle: str


def get_inner_type(field_type):
    # If output_type is a Union, extract all possible types
    # check if field_type is a List
    if hasattr(field_type, "__origin__") and field_type.__origin__ is Union:
        return [get_inner_type(allowed_type) for allowed_type in get_args(field_type)]

    try:
        # Otherwise, simply check if input_type is a subclass of output_type
        if hasattr(field_type, "__origin__") and field_type.__origin__ is list:
            return field_type.__args__[0]
        else:
            return field_type
    except Exception as e:
        raise ValueError(f"Could not get inner type: {field_type=}, {field_type.__args__=}") from e


def is_type_compatible_lists(input_type, output_type):
    input_type = TYPE_ADAPTER.get(input_type, input_type)
    output_type = TYPE_ADAPTER.get(output_type, output_type)

    if (
        hasattr(input_type, "__origin__")
        and input_type.__origin__ is list
        and hasattr(output_type, "__origin__")
        and output_type.__origin__ is list
    ):
        if input_type.__args__[0] is Any:
            return True
        if output_type.__args__[0] is Any:
            return True
        return issubclass(input_type.__args__[0], output_type.__args__[0]) or is_subclass_of_auto(input_type.__args__[0])
    return False


def is_subclass_of_auto(type_):
    if type_ is Any:
        return False
    if type_ is Auto:
        return True
    # Check if type_ is a union (Python 3.10+ UnionType or typing.Union)
    if isinstance(type_, types.UnionType) or (hasattr(type_, "__origin__") and type_.__origin__ is Union):
        return False
    elif get_origin(type_) is list:
        return False
    return issubclass(type_, Auto)


def is_type_compatible(input_field, output_field):
    is_annot_auto = False
    if hasattr(input_field, "annotation"):
        is_annot_auto = (input_field.json_schema_extra or {}).get("is_auto")
        input_field = input_field.annotation

    if output_field.annotation is Any:
        return True

    if get_origin(input_field) is types.UnionType:
        return all(is_type_compatible(it, output_field) for it in get_args(input_field))

    if is_type_compatible_lists(input_field, output_field.annotation):
        # shortcut if they both are list of the same sub types
        return True

    # If output_type is a Union, extract all possible types
    input_type = TYPE_ADAPTER.get(input_field, input_field)
    output_type = get_inner_type(TYPE_ADAPTER.get(output_field.annotation, output_field.annotation))

    # check if output_type is a List
    if isinstance(output_type, list):
        return any(allowed_type is Any or issubclass(input_type, allowed_type) for allowed_type in output_type)

    is_output_auto = is_subclass_of_auto(output_type) or (output_field.json_schema_extra or {}).get("is_auto")
    is_input_auto = is_subclass_of_auto(input_type) or is_annot_auto

    if is_output_auto and is_input_auto:
        logger.debug(f"Both input and output are Auto: {input_field=}, {output_field=}")
        return False

    if is_output_auto or is_input_auto:
        return True

    try:
        if issubclass(input_type, output_type):
            return True
        input_model_fields = getattr(input_type, "model_fields", {})
        output_model_fields = getattr(output_type, "model_fields", {})

        # FIXME: this lacks multiple cases - need to be rewritten sometimes.
        if not input_model_fields:
            # is primitive
            if output_model_fields:
                return is_type_compatible(input_type, output_model_fields.annotation)
            else:
                # if both are primitives

                # check if output primitive is a union
                if get_origin(output_model_fields) is types.UnionType:
                    return any(is_type_compatible(input_model_fields, it) for it in get_args(output_model_fields))
                # more cases here
                return input_model_fields == output_model_fields

        if not input_model_fields or not output_model_fields:
            # if either of them don't have model fields this means they are primitives
            logger.debug(f"Either input or output is primitive: {input_field=}, {output_field=}")
            return False
        return set(input_model_fields) == set(output_model_fields) and all(
            v.annotation == output_model_fields[k].annotation for k, v in input_model_fields.items()
        )  # if they have the same model fields it's compatible
    except Exception as e:
        raise ValueError(f"Error checking type compatibility: {input_type=}, {output_type=}") from e


class SchemaWithPrivate(BaseModel):
    @classmethod
    def model_json_schema(cls, **kwargs):
        schema = super().model_json_schema(**kwargs)
        # Filter out fields ending with "_"
        properties = schema.get("properties", {})
        schema["properties"] = {key: value for key, value in properties.items() if not key.endswith("_")}
        return schema


class Node(abc.ABC):
    class InputSchema(SchemaWithPrivate):
        model_config = ConfigDict(extra="forbid")
        run: bool = Field(
            True,
            title="Run",
            description="Whether to run the block.",
            examples=[True, False],
        )

    class OutputSchema(SchemaWithPrivate):
        model_config = ConfigDict(json_schema_extra={"uiSchema": {"ui:options": {"label": False}}})

    IS_DEPRECATED = False
    EnvVars: BaseEnvVars = None
    SensitiveFields = tuple()
    DESC = ""
    SCOPES: List[str] = None
    IS_TRIGGER = False
    STATES = tuple()
    ICON: str = ""
    PLURALLY_VERSION: int = 0

    class InitSchema(BaseModel):
        name: str = Field(
            title="Block Name",
            description="Name of the block.",
            examples=["Block 1"],
            min_length=1,
            max_length=35,
        )
        is_output_fixable: bool = Field(
            False,
            title="Fixable output",
            description="Whether the output of the block can be fixed.",
        )
        pos_x: float = 0
        pos_y: float = 0
        src_handles: List[str] | None = Field(None)
        tgt_handles: List[str] | None = Field(None)

        @classmethod
        def get_overrideable_fields(cls):
            return []

    def resolve_input_type_self(self):
        """
        Nodes that can resolve input types on their own should override this
        """
        if not self.is_resolved:
            self.is_resolved = True
            self._set_schemas()

    def resolve_output_type_self(self):
        """
        Nodes that can resolve output types on their own should override this
        """
        ...

    def resolve_output_type(self, graph):
        auto_props = {}
        for field_name, field in self.OutputSchema.model_fields.items():
            if is_subclass_of_auto(field.annotation) or (field.json_schema_extra or {}).get("is_auto"):
                # if field.annotation is Auto:
                for _, tgt, key in graph.out_edges(self, data=True):
                    if key["src_handle"] == field_name:
                        tgt_field = tgt.InputSchema.model_fields[key["tgt_handle"]]
                        if tgt_field.annotation is Auto:
                            continue

                        # if resolved field is dynamic (i.e. not primitive), we need to keep track that this might change
                        # in the future. otherwise it won't be resolved again
                        field.json_schema_extra = {
                            **(field.json_schema_extra or {}),
                            "is_auto": True,
                        }
                        auto_props[field_name] = (tgt_field.annotation, field)
                        break
                else:
                    raise ValueError(f"Auto field {field_name} not resolved for {self}")
        if not auto_props:
            return
        props = {k: (v.annotation, v) for k, v in self.OutputSchema.model_fields.items()}
        for field_name, p in auto_props.items():
            props[field_name] = p
        self.OutputSchema = create_model(
            "OutputSchemaResolved",
            **props,
        )

    def resolve_input_type(self, graph):
        auto_props = {}
        for field_name, field in self.InputSchema.model_fields.items():
            if is_subclass_of_auto(field.annotation) or (field.json_schema_extra or {}).get("is_auto"):
                # if field.annotation is Auto:
                for src, _, key in graph.in_edges(self, data=True):
                    if key["tgt_handle"] == field_name:
                        src_field = src.OutputSchema.model_fields[key["src_handle"]]
                        if src_field.annotation is Auto:
                            continue
                        # if resolved field is dynamic (i.e. not primitive), we need to keep track that this might change
                        # in the future. otherwise it won't be resolved again
                        field.json_schema_extra = {
                            **(field.json_schema_extra or {}),
                            "is_auto": True,
                        }
                        auto_props[field_name] = (src_field.annotation, field)
                        break
                else:
                    raise ValueError(f"Auto field {field_name} not resolved for {self}")
        if not auto_props:
            return
        props = {k: (v.annotation, v) for k, v in self.InputSchema.model_fields.items()}

        for field_name, p in auto_props.items():
            props[field_name] = p

        self.InputSchema = create_model(
            "InputSchema",
            **props,
        )

    def _get_handles(self, schema, in_handles):
        out_handles = set(handle for handle in schema.model_fields if not handle.endswith("_"))

        if self.is_trigger:
            out_handles = out_handles - {"run"}
        if in_handles is not None:
            out_handles &= set(in_handles)
        return list(out_handles)

    def __init__(self, init_inputs: InitSchema, outputs=None):
        self._node_id = f"nd-{str(uuid.uuid4())}"
        self.is_output_fixable = init_inputs.is_output_fixable
        self.is_resolved = False
        self.name = init_inputs.name
        self.outputs = outputs or {}
        self._set_schemas()
        self._check_schemas()

        self._pos_x = init_inputs.pos_x
        self._pos_y = init_inputs.pos_y

        self.tgt_handles = self._get_handles(self.InputSchema, init_inputs.tgt_handles)
        self.src_handles = self._get_handles(self.OutputSchema, init_inputs.src_handles)

        self.has_run_successfully = False

    def start_worker(self) -> bool:
        return False

    def early_stop_if_needed(self, graph: nx.MultiDiGraph):
        return False

    @property
    def pos_x(self):
        return self._pos_x

    @property
    def pos_y(self):
        return self._pos_y

    @pos_x.setter
    def pos_x(self, value):
        self._pos_x = value

    @pos_y.setter
    def pos_y(self, value):
        self._pos_y = value

    @property
    def is_trigger(self):
        return self.IS_TRIGGER

    def callback(self):
        self.has_run_successfully = False

    def _check_schemas(self):
        if self.InputSchema is None or not issubclass(self.InputSchema, BaseModel):
            raise ValueError(f"{type(self).__name__} must have an InputSchema")
        if self.OutputSchema is None or not issubclass(self.OutputSchema, BaseModel):
            raise ValueError(f"{type(self).__name__} must have an OutputSchema")

    def _set_schemas(self): ...

    @property
    def adapters(self):
        return {}

    @property
    def node_id(self):
        return self._node_id

    def _get_non_overrideable_data_keys(self):
        return set()

    def _get_overrideable_data_keys(self):
        return None

    def get_overrideable_data(self):
        if not self.is_output_fixable:
            return {}
        od_keys = self._get_overrideable_data_keys()
        if od_keys is None:
            od_keys = set(self.outputs)
        non_od_keys = self._get_non_overrideable_data_keys()

        outputs = self.OutputSchema(**self.outputs).model_dump(mode="json")
        return {k: v for k, v in outputs.items() if k in od_keys and k not in non_od_keys}

    def validate_connection(self, src_node: "Node", output_node_id: str, input_node_id: str):
        output_node_schema = src_node.OutputSchema.model_fields.get(output_node_id)
        input_node_schema = self.InputSchema.model_fields.get(input_node_id)

        if output_node_schema is None or input_node_schema is None:
            return True
        return is_type_compatible(output_node_schema, input_node_schema)

    def validate_inputs(self, **kwargs):
        return self.InputSchema(**kwargs)

    def __call__(self, **kwargs):
        """Override this method in child classes to define logic."""
        node_input = self.validate_inputs(**kwargs)
        self.forward(node_input)
        if self.outputs is not None:
            for k, v in self.outputs.items():
                if v is Auto:
                    raise ValueError(f"Output {k} is not resolved for {self}")
        self.has_run_successfully = True

    def get_necessary_env_vars(self) -> List[str]:
        if self.EnvVars:
            return list(self.EnvVars.model_fields.keys())
        return []

    def forward(self, **kwargs):
        raise NotImplementedError("Subclasses must implement this method")

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Node) and other.node_id == self.node_id

    def __repr__(self) -> str:
        return str(self)

    def __str__(self) -> str:
        return f"{type(self).__name__}(name={self.name})[{self.node_id[3:7]}]"

    def __hash__(self) -> int:
        return hash(self.node_id)

    def _state(self):
        return {}

    def state(self):
        state = self._state()
        assert set(state) == set(self.STATES), f"{state=} not in {self.STATES=}"
        return state

    def update_state(self, state_update):
        if state_update:
            for key, value in state_update.items():
                assert hasattr(self, key), f"Node {self} does not have attribute {key}"
                assert key in self.STATES
                setattr(self, key, value)

    def serialize(self):
        # outputs_to_serialize = None
        # if self.outputs is not None:
        #     outputs_to_serialize = {**self.outputs}
        #     for k, v in outputs_to_serialize.items():
        #         if isinstance(v, datetime):
        #             outputs_to_serialize[k] = v.isoformat()

        return {
            "PLURALLY_VERSION": self.PLURALLY_VERSION,
            "kls": type(self).__name__,
            "name": self.name,
            "_node_id": self._node_id,
            "pos_x": self.pos_x,
            "pos_y": self.pos_y,
            "is_trigger": self.is_trigger,
            # "outputs": outputs_to_serialize,
            "src_handles": self.src_handles,
            "tgt_handles": self.tgt_handles,
            "is_output_fixable": self.is_output_fixable,
        }

    @classmethod
    def _parse(cls, **kwargs):
        kwargs = load_from_json_dict(kwargs)
        return cls(cls.InitSchema(**kwargs))

    def get_issues(self, graph):
        return []

    @classmethod
    def adapt_version(cls, node_ids: List[str], flow_serialization_data: dict):
        raise NotImplementedError(f"Subclasses must implement this method {cls}")

    @classmethod
    def parse(cls, **kwargs):
        _node_id = kwargs.pop("_node_id")
        # outputs = kwargs.pop("outputs")
        try:
            obj = cls._parse(**kwargs)
        except Exception as e:
            logger.exception(e)
            logger.error(f"Error parsing {cls.__name__} with {kwargs=}")
            raise e
        obj._node_id = _node_id
        obj.pos_x = kwargs.get("pos_x", 0)
        obj.pos_y = kwargs.get("pos_y", 0)

        # if outputs is not None:
        #     for k, v in outputs.items():
        #         if isinstance(v, datetime):
        #             outputs[k] = v.fromisoformat(v)

        # obj.outputs = outputs
        return obj

    def get_scopes_and_meta_data(self):
        return [(self.SCOPES, {})]

    def add_target_handle(self, src_handle: str) -> str:
        raise NotImplementedError(f"Subclasses must implement this method {self}")
