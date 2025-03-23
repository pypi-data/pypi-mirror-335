import enum
import re
import uuid
from typing import List

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    PrivateAttr,
    create_model,
    model_validator,
)

from plurally.json_utils import replace_refs
from plurally.models.auto import Auto


class HandleType(enum.Enum):
    TEXT = "Text"
    INTEGER = "Integer"
    NUMBER = "Number"
    AUTO = "Auto"


HANDLE_TYPE_MAP = {
    HandleType.TEXT.value: str,
    HandleType.INTEGER.value: int,
    HandleType.NUMBER.value: float,
    HandleType.AUTO.value: Auto,
}

HANDLE_TYPE_OUTPUT_UISCHEMA = {
    HandleType.TEXT.value: {
        "ui:widget": "textarea",
        "ui:options": {
            "rows": 6,
        },
    },
}

HANDLE_TYPE_FRIENDLY = {
    HandleType.AUTO.value: "Auto (BETA)",
}


class NameableHandle(BaseModel):
    free: str = Field(
        title="Name",
        min_length=1,
        max_length=140,
    )
    handle_id: str = Field("", format="hidden")
    type: HandleType = Field("Auto", title="Type")
    _clean: str = PrivateAttr()

    model_config = ConfigDict(use_enum_values=True)

    @model_validator(mode="after")
    def clean_handle(cls, values):
        # remove special characters, replace spaces by _
        cleaned_string = re.sub(r"\s+", "_", values.free.strip())
        # Remove all special characters except underscores
        values._clean = re.sub(r"[^a-zA-Z0-9_]", "", cleaned_string).lower()
        if not values._clean[0].isalpha():
            raise ValueError("Outputs must start with a letter")
        if not values.handle_id:
            values.handle_id = uuid.uuid4().hex[:4]
        return values


def get_nameable_fields(
    title,
    description,
    min_length=None,
    examples=None,
    placeholder="",
    default_factory=None,
    json_schema_extra_extra=None,
):
    return Field(
        title=title,
        min_length=min_length,
        description=description,
        examples=examples,
        json_schema_extra={
            "uiSchema": {
                "items": {
                    "ui:label": False,
                    "ui:grid": [
                        ("free", 8),
                        ("type", 4),
                    ],
                    "free": {
                        "ui:placeholder": placeholder,
                    },
                },
            },
            **(json_schema_extra_extra or {}),
            "uniqueItems": True,
        },
        default_factory=default_factory,
    )


class NameableInputFields:
    def __init__(
        self,
        values: List[NameableHandle],
        __base__,
        attr_name: str = "input_fields",
    ):
        self.__base__ = __base__
        self._attr_name = attr_name
        setattr(self, self._attr_name, values)
        self.set_schemas()
        self._InputSchema = None

    @property
    def tgt_handles(self):
        return list(self.InputSchema.model_fields)

    @tgt_handles.setter
    def tgt_handles(self, value): ...

    @property
    def values(self):
        return getattr(self, self._attr_name)

    @values.setter
    def values(self, value):
        value = [v if isinstance(v, NameableHandle) else NameableHandle(**v) for v in value]
        assert len(set(field._clean for field in value)) == len(value), f"Input fields must be unique {value}"
        setattr(self, self._attr_name, value)
        self.set_schemas()

    def set_schemas(self) -> None:
        in_fields_map = {}
        for field in self.values:
            in_fields_map[field._clean] = (
                Auto,
                Field(
                    ...,
                    title=field.free,
                    json_schema_extra={"handle_id": field.handle_id},
                ),
            )

        self.InputSchema = create_model(
            "InputSchema",
            **in_fields_map,
            __base__=self.__base__,
        )

    @property
    def InputSchema(self):
        return self._InputSchema

    @InputSchema.setter
    def InputSchema(self, value):
        self._InputSchema = value

    def serialize(self):
        return {
            self._attr_name: [i.model_dump() for i in self.values],
            "input_schema": replace_refs(self.InputSchema.model_json_schema()),
        }

    def add_target_handle(self, src_handle):
        new_tgt_handle = NameableHandle(free=src_handle)
        ix = 1
        while new_tgt_handle._clean in [i._clean for i in self.values]:
            new_tgt_handle = NameableHandle(free=new_tgt_handle.free + f" {ix}")
        new_handle = [*self.values, new_tgt_handle]
        setattr(self, self._attr_name, new_handle)
        self.set_schemas()
        return new_tgt_handle._clean

    @classmethod
    def parse(cls, kwargs, __base__, attr_name):
        kwargs[attr_name] = [NameableHandle(**i) for i in kwargs[attr_name]]


class NameableOutputFieldsMixin:
    def __init__(self, values: List[NameableHandle], attr_name: str = "output_fields"):
        self._attr_name = attr_name
        setattr(self, self._attr_name, values)
        self._set_schemas()

    @property
    def output_fields(self):
        return getattr(self, self._attr_name)

    @output_fields.setter
    def output_fields(self, value):
        value = [v if isinstance(v, NameableHandle) else NameableHandle(**v) for v in value]
        assert len(set(field._clean for field in value)) == len(value), f"Input fields must be unique {value}"
        setattr(self, self._attr_name, value)
        self._set_schemas()
        self.src_handles = self._get_handles(self.OutputSchema, None)

    def _set_schemas(self) -> None:
        in_fields_map = {}
        for field in self.values:
            ui_schema = HANDLE_TYPE_OUTPUT_UISCHEMA.get(field.type.value, {})
            in_fields_map[field._clean] = (
                str,
                Field(
                    ...,
                    title=field.free,
                    json_schema_extra={"handle_id": field.handle_id, "uiSchema": ui_schema},
                ),
            )
        self.OutputSchema = create_model(
            "OutputSchema",
            **in_fields_map,
            __base__=self.__class__.OutputSchema,
        )

    def serialize_columns(self):
        return {
            self._attr_name: [i.model_dump() for i in self.values],
            "input_schema": replace_refs(self.OutputSchema.model_json_schema()),
        }
