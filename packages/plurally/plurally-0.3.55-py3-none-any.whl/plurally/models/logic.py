import uuid
from typing import Any, Dict, List

from pydantic import BaseModel, ConfigDict, Field, model_validator

from plurally.json_utils import load_from_json_dict, replace_refs
from plurally.models.node import Node
from plurally.models.utils import create_dynamic_model


class PossibleValue(BaseModel):
    value: str = Field(min_length=1, max_length=144)
    handle_id: str = Field("", format="hidden")

    @model_validator(mode="after")
    def clean_handle(cls, values):
        if not values.handle_id:
            values.handle_id = uuid.uuid4().hex[:4]
        return values


class Switch(Node):
    ICON = "switch"

    class InitSchema(Node.InitSchema):
        """Creates a conditional branching. The output corresponding to the input's value will be activated, the others won't."""

        model_config = ConfigDict(json_schema_extra={"hide-run": True})
        possible_values: List[PossibleValue] = Field(
            title="Possible Values",
            description="The possible values that the input can take.",
            example=["yes", "no"],
            min_length=1,
            help="For instance, if your input can be 'yes' or 'no', then you should have \"yes\" and \"no\" as possible values. These outputs will then be used to condition the flow.",
            json_schema_extra={
                "name_singular": "Possible value",
                "is_output": True,
                "uniqueItems": True,
                "uiSchema": {
                    "items": {
                        "ui:label": False,
                        "errorMessages": {
                            "pattern": "Outputs can only contain letters, numbers, and underscores, and must start with a letter."
                        },
                    }
                },
            },
        )

    class InputSchema(Node.InputSchema):
        value: str = Field(
            title="Input",
            description="The input to condition on.",
        )

    class OutputSchema(Node.OutputSchema):
        key_vals: Dict[str, str]

    DESC = InitSchema.__doc__

    def __init__(self, init_inputs: InitSchema) -> None:
        self._possible_values = init_inputs.possible_values
        super().__init__(init_inputs)

    @property
    def possible_values(self):
        return self._possible_values

    @possible_values.setter
    def possible_values(self, value):
        value = [v if isinstance(v, PossibleValue) else PossibleValue(**v) for v in value]
        self._possible_values = value
        self._set_schemas()
        self.src_handles = self._get_handles(self.OutputSchema, None)

    def _set_schemas(self) -> None:
        # create pydantic model from fields
        self.OutputSchema = create_dynamic_model(
            "OutputSchema",
            [val.handle_id for val in self.possible_values],
            defaults={val.handle_id: None for val in self.possible_values},
            types={val.handle_id: bool for val in self.possible_values},
            titles={val.handle_id: val.value for val in self.possible_values},
        )

    def forward(self, node_input: InputSchema):
        for val in self.possible_values:
            if node_input.value == val.value:
                self.outputs[val.handle_id] = True
            else:
                self.outputs[val.handle_id] = False

    def serialize(self):
        return {
            **super().serialize(),
            "possible_values": [o.model_dump() for o in self.possible_values],
            "output_schema": replace_refs(self.OutputSchema.model_json_schema()),
        }

    @classmethod
    def _parse(cls, **kwargs):
        kwargs = load_from_json_dict(kwargs)
        kwargs["possible_values"] = [PossibleValue(**o) for o in kwargs["possible_values"]]
        return cls(cls.InitSchema(**kwargs))


class LogicalInputSchema(Node.InputSchema):
    inputs: List[bool] = Field(
        description="The inputs.",
        min_length=1,
        examples=[True, False],
    )


class And(Node):
    ICON = "switch"

    InputSchema = LogicalInputSchema

    class InitSchema(Node.InitSchema):
        __doc__ = "Will return True if all of the inputs are True, else False."
        model_config = ConfigDict(json_schema_extra={"hide-run": True})

    class OutputSchema(Node.OutputSchema):
        output: bool = Field(
            description="The output, will be True if all of the inputs are True, else False.",
            examples=[True, False],
        )

    def forward(self, node_input: InputSchema):
        self.outputs["output"] = all(node_input.inputs)


class Or(Node):
    ICON = "switch"

    InputSchema = LogicalInputSchema

    class InitSchema(Node.InitSchema):
        __doc__ = "Will return True if any of the inputs is True, else False."
        model_config = ConfigDict(json_schema_extra={"hide-run": True})

    class OutputSchema(Node.OutputSchema):
        output: bool = Field(
            description="The output, will be True if any of the inputs is True, else False.",
            examples=[True, False],
        )

    def forward(self, node_input: InputSchema):
        self.outputs["output"] = any(node_input.inputs)


class Not(Node):
    ICON = "switch"

    class InputSchema(Node.InputSchema):
        inputs: Any

    class InitSchema(Node.InitSchema):
        __doc__ = "Will return True if any of the inputs is True, else False."
        model_config = ConfigDict(json_schema_extra={"hide-run": True})

    class OutputSchema(Node.OutputSchema):
        output: bool = Field(
            description="The output, will be True if any of the inputs is True, else False.",
            examples=[True, False],
        )

    def forward(self, node_input: InputSchema):
        self.outputs["output"] = not bool(node_input.inputs)


class Bool(Node):
    ICON = "switch"

    class InputSchema(Node.InputSchema):
        inputs: Any

    class InitSchema(Node.InitSchema):
        __doc__ = "Will return True if any of the inputs is True, else False."
        model_config = ConfigDict(json_schema_extra={"hide-run": True})

    class OutputSchema(Node.OutputSchema):
        output: bool = Field(
            description="The output, will be True if any of the inputs is True, else False.",
            examples=[True, False],
        )

    def forward(self, node_input: InputSchema):
        self.outputs["output"] = bool(node_input.inputs)


__all__ = ["Switch", "And", "Or", "Not", "Bool"]
