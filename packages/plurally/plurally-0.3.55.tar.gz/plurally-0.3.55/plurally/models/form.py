import enum
import re
from typing import List

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    create_model,
    field_validator,
)
from pydantic_extra_types.color import Color

from plurally.json_utils import replace_refs
from plurally.models import utils
from plurally.models.misc import AudioFile, ImageFile, MicAudioFile
from plurally.models.node import Node


class FormEntryType(enum.Enum):
    SHORT_TEXT = "short_text"
    TEXT = "text"
    EMAIL = "email"
    NUMBER = "number"
    BOOLEAN = "true/false"
    AUDIO = "audio file"
    MIC = "audio record"
    IMAGE = "image"


TYPE_CONVERTER = {
    FormEntryType.SHORT_TEXT.value: str,
    FormEntryType.TEXT.value: str,
    FormEntryType.EMAIL.value: EmailStr,
    FormEntryType.NUMBER.value: float,
    FormEntryType.BOOLEAN.value: bool,
    FormEntryType.AUDIO.value: AudioFile,
    FormEntryType.MIC.value: MicAudioFile,
    FormEntryType.IMAGE.value: ImageFile,
}


class FormEntry(BaseModel):
    model_config = ConfigDict(use_enum_values=True)
    name: str = Field(title="Name", min_length=1, max_length=140)
    type: FormEntryType = Field("short_text", title="Type", json_schema_extra={"advanced": True})
    col_span: int = Field(12, title="Column Span", le=12, ge=1, json_schema_extra={"advanced": True})
    is_required: bool = Field(True, title="Required", json_schema_extra={"advanced": True})
    placeholder: str = Field(
        "",
        title="Placeholder",
        json_schema_extra={
            "advanced": True,
            "uiSchema": {"ui:placeholder": "Placeholder"},
        },
    )

    @field_validator("name")
    def validate_name(cls, value):
        value = value.strip()
        if not value.strip():
            raise ValueError("Name cannot be empty")
        return value


class Form(Node):
    IS_TRIGGER = True
    ICON = "form"

    class InitSchema(Node.InitSchema):
        __doc__ = "Creates a form with the specified inputs. You can embed the form code in your website. Submission of the form will trigger the flow."

        model_config = ConfigDict(
            json_schema_extra={
                "uiSchema": {
                    "preview": "FormPreview",
                    "advanced": {
                        "ui:grid": [
                            (
                                "button_text",
                                {
                                    "base": 10,
                                    "sm": 8,
                                },
                            ),
                            (
                                "button_color",
                                {
                                    "base": 2,
                                    "sm": 4,
                                },
                            ),
                            ("button_on_same_row", {"base": 12, "sm": 6}),
                            ("show_label", {"base": 12, "sm": 6}),
                            ("use_case", {"base": 12, "sm": 6}),
                        ]
                    },
                }
            }
        )
        form: List[FormEntry] = Field(
            [FormEntry(name="Email address", type=FormEntryType.EMAIL, col_span=12)],
            title="Form inputs",
            min_length=1,
            json_schema_extra={
                "name_singular": "Input",
                "uiSchema": {
                    "ui:label": False,
                    "items": {
                        "ui:label": False,
                        "ui:grid": [
                            ("name", {"base": 12, "sm": 8, "xl": 4}),
                            ("type", {"base": 12, "sm": 4, "xl": 2}),
                            ("placeholder", {"base": 12, "sm": 8, "xl": 4}),
                            ("col_span", {"base": 12, "sm": 4, "xl": 2}),
                            ("is_required", {"base": 12}),
                        ],
                    },
                },
            },
        )

        button_text: str = Field("Submit", title="Button text", json_schema_extra={"advanced": True})
        button_color: Color = Field("#007bff", title="Button color", json_schema_extra={"advanced": True})
        button_on_same_row: bool = Field(False, title="Button on same row", json_schema_extra={"advanced": True})
        show_label: bool = Field(True, title="Show label", json_schema_extra={"advanced": True})
        use_case: bool = Field(
            False,
            title="Use case",
            json_schema_extra={"advanced": True},
        )

        @field_validator("form", mode="after")
        def check_form(cls, values):
            if len(set(entry.name for entry in values)) != len(values):
                raise ValueError("Form entries must have unique names")
            return values

    DESC = InitSchema.__doc__

    class InputSchema(Node.InputSchema):
        pass

    class OutputSchema(Node.OutputSchema): ...

    @classmethod
    def compute_output_model(cls, form: List[FormEntry], show_label: bool = True):
        model_fields = {}
        grid = []
        for entry in form:
            name = utils.slugify(entry.name)
            grid.append((name, entry.col_span))

            is_text = entry.type in (
                FormEntryType.SHORT_TEXT.value,
                FormEntryType.TEXT.value,
            )

            field = Field(
                "" if is_text and not entry.is_required else ...,
                title=entry.name.capitalize(),
                json_schema_extra={
                    "uiSchema": {
                        "ui:label": show_label,
                        "ui:placeholder": entry.placeholder,
                    }
                },
            )
            if entry.type == FormEntryType.TEXT.value:
                field.json_schema_extra["uiSchema"]["ui:widget"] = "textarea"

            if is_text and not entry.is_required:
                field.json_schema_extra["uiSchema"]["ui:emptyValue"] = ""

            if entry.type == FormEntryType.AUDIO.value:
                field.json_schema_extra.update({"type-friendly": "Audio"})

            if entry.type == FormEntryType.MIC.value:
                field.json_schema_extra.update({"type-friendly": "Record Audio"})
            if not is_text and not entry.is_required:
                field.default = None

            if entry.type == FormEntryType.IMAGE.value and not entry.is_required:
                field.default = ImageFile(file="", filename="", content=b"")

            if entry.type in (
                FormEntryType.AUDIO.value,
                FormEntryType.MIC.value,
                FormEntryType.IMAGE.value,
            ):
                field.json_schema_extra.update({"file_label_override": entry.name})
            model_fields[name] = (TYPE_CONVERTER[entry.type], field)

        class Base(Node.OutputSchema):
            model_config = ConfigDict(
                json_schema_extra={
                    "uiSchema": {
                        "ui:grid": grid,
                    }
                }
            )

        model = create_model(
            "Form",
            **model_fields,
            __base__=Base,
        )
        return model

    @classmethod
    def compute_schema(cls, init_schema: InitSchema):
        model = cls.compute_output_model(init_schema.form, init_schema.show_label)
        return replace_refs(model.model_json_schema())

    def __init__(self, node_inputs: InputSchema):
        self._form = node_inputs.form
        self.show_label = node_inputs.show_label
        self.button_text = node_inputs.button_text
        self.button_on_same_row = node_inputs.button_on_same_row
        self.button_color = node_inputs.button_color
        self.use_case = node_inputs.use_case
        super().__init__(node_inputs)

    @property
    def button_color(self):
        return self._button_color

    @button_color.setter
    def button_color(self, value):
        self._button_color = Color(value) if isinstance(value, str) else value

    @property
    def form(self):
        return self._form

    @form.setter
    def form(self, value):
        value = [v if isinstance(v, FormEntry) else FormEntry(**v) for v in value]
        self._form = value
        self._set_schemas()
        self.src_handles = self._get_handles(self.OutputSchema, None)

    def _set_schemas(self):
        self.OutputSchema = self.compute_output_model(self.form)

    def serialize(self):
        return super().serialize() | {
            "form": [entry.model_dump() for entry in self.form],
            "show_label": self.show_label,
            "button_text": self.button_text,
            "button_on_same_row": self.button_on_same_row,
            "button_color": self.button_color.as_hex(),
            "output_schema": replace_refs(self.OutputSchema.model_json_schema()),
            "use_case": self.use_case,
        }

    def start_worker(self) -> bool:
        return True
