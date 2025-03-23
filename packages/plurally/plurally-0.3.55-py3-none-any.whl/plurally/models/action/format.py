import csv
import re
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, List
import uuid

from email_validator import EmailNotValidError, validate_email
import jinja2
import jinja2.nodes
from pydantic import ConfigDict, Field, create_model, model_validator

from plurally.json_utils import load_from_json_dict, replace_refs
from plurally.models import adapters as model_adapters
from plurally.models.auto import Auto
from plurally.models.fields import (
    HANDLE_TYPE_FRIENDLY,
    HANDLE_TYPE_MAP,
    HandleType,
    NameableHandle,
    NameableInputFields,
    get_nameable_fields,
)
from plurally.models.html import HtmlCreate
from plurally.models.jinja_template import get_public_env_vars, load_jinja_template
from plurally.models.misc import Table
from plurally.models.node import Node
from plurally.models.utils import create_dynamic_model


class FormatInitSchema(Node.InitSchema):
    model_config = ConfigDict(json_schema_extra={"hide-run": True})


class FormatJinja(Node):
    ICON = "format"

    class InitSchema(FormatInitSchema):
        """Format text using a Jinja template."""

        template: str = Field(
            description="The Jinja template to format the text.",
            json_schema_extra={"uiSchema": {"ui:widget": "textarea", "ui:options": {"rows": 10}}},
        )

    class OutputSchema(Node.OutputSchema):
        formatted_text: str = Field(
            description="The text formatted using the Jinja template.",
        )

    def __init__(self, init_inputs) -> None:  # type: ignore
        self.template = init_inputs.template
        super().__init__(init_inputs)

    def _set_schemas(self) -> None:
        env = jinja2.Environment()
        try:
            parsed_content = env.parse(self.template)
            fields = {}
            for name in parsed_content.find_all(jinja2.nodes.Name):
                if name.ctx == "load":
                    fields[name.name] = (Any | None, Field(None, title=name.name))
            self.InputSchema = create_model("InputSchema", __base__=FormatJinja.InputSchema, **fields)
        except jinja2.exceptions.TemplateSyntaxError as e:
            ...

    def forward(self, node_inputs) -> None:  # type: ignore
        json_dict_kwargs = node_inputs.model_dump(exclude=["run"], mode="json")
        json_dict_kwargs.update(get_public_env_vars())
        template = load_jinja_template(self.template)
        prompt = template.render(**json_dict_kwargs)
        self.outputs["formatted_text"] = prompt

    def serialize(self):
        return super().serialize() | {"template": self.template, "input_schema": replace_refs(self.InputSchema.model_json_schema())}


class FormatText(Node):
    ICON = "format"

    class InitSchema(FormatInitSchema):
        """Format text using a template."""

        template: str = Field(
            pattern=r"\{([^{}]+)\}",
            description="Template to format the input text, example: Hello, {name}! I like {food}. Each named variable inside curly braces will be replaced by the corresponding connected value.",
            examples=["Hello, {name}, I like {food}."],
            json_schema_extra={
                "uiSchema": {
                    "errorMessages": {
                        "pattern": "You must provide at least one named variable inside curly braces, for example: Hi my name is {name}."
                    },
                    "ui:widget": "textarea",
                    "ui:placeholder": "Write template here, for example: Hello, my name is {name}.",
                },
            },
        )

    class InputSchema(Node.InputSchema):
        text: str = Field(
            description="Text to format.",
            examples=["Hello, world!"],
            format="textarea",
        )

    class OutputSchema(Node.OutputSchema):
        formatted_text: str = Field(
            description="The text formatted using the template.",
        )

    DESC = InitSchema.__doc__

    def __init__(self, init_inputs: InitSchema):
        self._template = init_inputs.template
        super().__init__(init_inputs)

    def _set_schemas(self) -> None:
        # create pydantic model from output_fields
        vars = re.findall(r"{(.*?)}", self.template)
        self.InputSchema = create_dynamic_model("InputSchema", vars, base=Node.InputSchema)

    @property
    def template(self):
        return self._template

    @template.setter
    def template(self, value):
        self._template = value
        self._set_schemas()
        self.tgt_handles = self._get_handles(self.InputSchema, None)

    def forward(self, node_input):
        formatted_text = self.template.format(**node_input.model_dump())
        self.outputs["formatted_text"] = formatted_text

    def serialize(self):
        return {
            "template": self.template,
            "input_schema": replace_refs(self.InputSchema.model_json_schema()),
            **super().serialize(),
        }


class FormatTable(Node):
    ICON = "format"

    class InitSchema(FormatInitSchema):
        """Format a table to text using a template."""

        template: str = Field(
            pattern=r"\{([^{}]+)\}",
            description="Template to format each row, example, every variable should be a table column.",
            examples=["Hello, {name}, I like {food}."],
            json_schema_extra={
                "uiSchema": {
                    "errorMessages": {
                        "pattern": "You must provide at least one named variable inside curly braces, for example: Hi my name is {name}."
                    },
                    "ui:widget": "textarea",
                    "ui:placeholder": "Write template here, for example: Hello, my name is {name}.",
                },
            },
        )
        separator: str = Field(
            "\n",
            description="Separator to use between rows. If unsure, use a new line (default).",
            examples=[", "],
            json_schema_extra={
                "uiSchema": {
                    "ui:widget": "textarea",
                    "ui:placeholder": "Write separator here, for example: for example a comma or a new line.",
                },
            },
        )

        prefix: str = Field(
            "",
            description="Prefix to add to the formatted text.",
            examples=["#### This is before the text ####."],
            json_schema_extra={
                "uiSchema": {
                    "ui:widget": "textarea",
                    "ui:placeholder": "Write prefix here, for example: #### This is before the text ####.",
                },
            },
        )
        suffix: str = Field(
            "",
            description="Suffix to add to the formatted text.",
            examples=["#### This is after the text ####"],
            json_schema_extra={
                "uiSchema": {
                    "ui:widget": "textarea",
                    "ui:placeholder": "Write suffix here, for example: #### This is after the text ####.",
                },
            },
        )

    class InputSchema(Node.InputSchema):
        table: Table = Field(
            description="Table to format.",
        )

    class OutputSchema(Node.OutputSchema):
        formatted_text: str = Field(
            description="The table's content formatted to text.",
        )

    DESC = InitSchema.__doc__

    def __init__(self, init_inputs: InitSchema):
        self.template = init_inputs.template.strip()
        self.prefix = init_inputs.prefix
        self.suffix = init_inputs.suffix
        self.separator = init_inputs.separator

        super().__init__(init_inputs)

    @property
    def template(self):
        return self._template

    @template.setter
    def template(self, value):
        self._template = value
        self._set_schemas()
        self.src_handles = self._get_handles(self.OutputSchema, None)

    def forward(self, node_input: InputSchema):
        row_str = []
        for row in node_input.table.data:
            formatted_text = self.template.format(**row)
            row_str.append(formatted_text)
        formatted_text = self.prefix + self.separator + self.separator.join(row_str) + self.separator + self.suffix
        self.outputs["formatted_text"] = formatted_text

    def get_necessary_columns(self):
        return re.findall(r"{(.*?)}", self.template)

    def serialize(self):
        return super().serialize() | {
            "template": self.template,
            "prefix": self.prefix,
            "suffix": self.suffix,
            "separator": self.separator,
        }


class CsvToTable(Node):
    ICON = "format"

    class InitSchema(FormatInitSchema):
        """Convert CSV text to a table."""

        delimiter: str = Field(
            ",",
            description="Delimiter to use between columns.",
            examples=[","],
            min_length=1,
        )

    class InputSchema(Node.InputSchema):
        csv: str = Field(
            description="CSV string to convert to a table.",
            examples=["name,age\nAlice,25\nBob,30"],
            format="textarea",
        )

    class OutputSchema(Node.OutputSchema):
        data: Table = Field(
            description="The table converted from the CSV string.",
        )

    DESC = InitSchema.__doc__

    def __init__(self, init_inputs: InitSchema):
        self.delimiter = init_inputs.delimiter
        super().__init__(init_inputs)

    def forward(self, node_input: InputSchema):
        data = csv.DictReader(
            node_input.csv.strip().splitlines(),
            delimiter=self.delimiter,
        )
        table = Table(data=data)
        self.outputs["data"] = table

    def serialize(self):
        return super().serialize() | {
            "delimiter": self.delimiter,
        }

    @property
    def adapters(self):
        return super().adapters | {"data": {str: model_adapters.table_to_str_adapter}}


class ToTable(Node, NameableInputFields):
    ICON = "format"

    class InputSchemaBase(Node.InputSchema):
        model_config = ConfigDict(json_schema_extra={"can-add-fields": True})

    class InitSchema(FormatInitSchema):
        """Convert inputs to table. For instance, if you have 2 inputs age and name, you can convert them to a table with columns age and name."""

        columns: List[NameableHandle] = get_nameable_fields(
            title="Columns",
            description="The columns of the table.",
            examples=[["name", "age"]],
            placeholder="Add column",
            json_schema_extra_extra={
                "is_input": True,
                "name_singular": "Column",
            },
        )

        @model_validator(mode="after")
        def check_model(cls, values):
            if len(set(field._clean for field in values.columns)) != len(values.columns):
                raise ValueError("Columns fields must be unique")

    class OutputSchema(Node.OutputSchema):
        data: Table = Field(
            description="The table converted from the inputs.",
        )

    DESC = InitSchema.__doc__

    def __init__(self, init_inputs: Node.InitSchema):
        self.renamable_columns = NameableInputFields(init_inputs.columns, ToTable.InputSchemaBase, "columns")
        super().__init__(init_inputs)

    @property
    def adapters(self):
        return super().adapters | {"data": {str: model_adapters.table_to_str_adapter}}

    @property
    def columns(self):
        return self.renamable_columns.values

    @columns.setter
    def columns(self, value):
        self.renamable_columns.values = value

    @property
    def InputSchema(self):
        return self.renamable_columns.InputSchema

    @InputSchema.setter
    def InputSchema(self, value):
        self.renamable_columns.InputSchema = value

    @property
    def tgt_handles(self):
        return self.renamable_columns.tgt_handles

    @tgt_handles.setter
    def tgt_handles(self, value):
        self.renamable_columns.tgt_handles = value

    def _set_schemas(self) -> None:
        self.renamable_columns.set_schemas()

    def forward(self, node_input):
        column_maps = {column._clean: column.free for column in self.columns}
        data = node_input.model_dump(include=list(column_maps))
        data = {column_maps[k]: v for k, v in data.items()}
        table = Table(data=[data])
        self.outputs["data"] = table

    def serialize(self):
        columns_serialized = self.renamable_columns.serialize()
        return super().serialize() | columns_serialized

    @classmethod
    def _parse(cls, **kwargs):
        kwargs = load_from_json_dict(kwargs)
        NameableInputFields.parse(kwargs, ToTable.InputSchemaBase, "columns")
        return cls(cls.InitSchema(**kwargs))

    def add_target_handle(self, src_handle):
        return self.renamable_columns.add_target_handle(src_handle)


class ScheduleUnit(str, Enum):
    MINUTES = "minutes"
    HOURS = "hours"
    DAYS = "days"
    WEEKS = "weeks"


class DateTimeManipulate(Node):
    ICON = "format"

    class InitSchema(FormatInitSchema):
        """Manipulate a datetime."""

        to_add_or_subtract: int = Field(
            title="To Add or Subtract",
            description="The number of units to add or subtract (if negative) to the date.",
            examples=[1, -3],
        )
        unit: ScheduleUnit = Field(
            description="The unit of the value to add or subtract to the date.",
            title="Unit",
        )

    class InputSchema(Node.InputSchema):
        date: datetime = Field(
            description="The date to manipulate.",
            format="date-time",
        )

    class OutputSchema(Node.OutputSchema):
        value: datetime = Field(
            description="The date manipulated.",
            format="date-time",
        )

    DESC = InitSchema.__doc__

    def __init__(self, init_inputs: Node.InitSchema):
        self.to_add_or_subtract = init_inputs.to_add_or_subtract
        self.unit = init_inputs.unit
        super().__init__(init_inputs)

    def forward(self, node_input: InputSchema):
        self.outputs["value"] = node_input.date + timedelta(**{self.unit: self.to_add_or_subtract})

    def serialize(self):
        return super().serialize() | {
            "to_add_or_subtract": self.to_add_or_subtract,
            "unit": self.unit,
        }


class FormatDatetimeEnum(str, Enum):
    TIME = "%H:%M:%S"
    TIME_NO_SECONDS = "%H:%M"
    DATE = "%Y-%m-%d"
    DATE_TIME = "%Y-%m-%d %H:%M:%S"
    DATE_TIME_NO_SECONDS = "%Y-%m-%d %H:%M"


DEFAULT_DT = datetime(2024, 12, 31, 23, 59, 59)


class FormatDatetime(Node):
    ICON = "format"

    class InitSchema(FormatInitSchema):
        """Format date & time."""

        format: FormatDatetimeEnum = Field(
            title="Format",
            default=FormatDatetimeEnum.DATE_TIME_NO_SECONDS,
            description="The format to use to format the date.",
            examples=[
                DEFAULT_DT.strftime(FormatDatetimeEnum.DATE_TIME_NO_SECONDS.value),
                DEFAULT_DT.strftime(FormatDatetimeEnum.DATE_TIME.value),
                DEFAULT_DT.strftime(FormatDatetimeEnum.DATE.value),
                DEFAULT_DT.strftime(FormatDatetimeEnum.TIME.value),
                DEFAULT_DT.strftime(FormatDatetimeEnum.TIME_NO_SECONDS.value),
            ],
            json_schema_extra={
                "default-show": DEFAULT_DT.strftime(FormatDatetimeEnum.DATE_TIME_NO_SECONDS.value),
                "uiSchema": {"labels": {e.value: DEFAULT_DT.strftime(e.value) for e in FormatDatetimeEnum}},
            },
        )

    class InputSchema(Node.InputSchema):
        date: datetime = Field(
            description="The date to format.",
            format="date-time",
        )

    class OutputSchema(Node.OutputSchema):
        formatted_date: str = Field(
            description="The date formatted.",
        )

    DESC = InitSchema.__doc__

    def __init__(self, init_inputs: InitSchema):
        self.format = init_inputs.format
        super().__init__(init_inputs)

    def forward(self, node_input: InputSchema):
        self.outputs["formatted_date"] = node_input.date.strftime(self.format)

    def serialize(self):
        return super().serialize() | {
            "format": self.format,
        }


class TableToTextSimple(Node):
    ICON = "format"

    class InitSchema(FormatInitSchema):
        """Convert a table to a text simply."""

    class InputSchema(Node.InputSchema):
        table: Table = Field(
            description="Table to convert to text.",
        )

    class OutputSchema(Node.OutputSchema):
        text: str = Field(
            description="The table converted to text.",
        )

    DESC = InitSchema.__doc__

    def forward(self, node_input: InputSchema):
        # we do not know here if the user properly formatted the table and put headers
        # we assume that if there is more than one column, there is a header
        text = ""
        if not node_input.table.is_empty():
            first_row = node_input.table.data[0]
            if len(first_row) == 1:
                text += f"{list(first_row.keys())[0]}\n"
                for row in node_input.table.data:
                    text += f"{list(row.values())[0]}\n"
            else:
                for row in node_input.table.data:
                    for key, value in row.items():
                        text += f"{key}: {value}\n"
                    text += "\n"
        self.outputs["text"] = text


class ValidateEmailAddress(Node):
    ICON = "format"

    class InitSchema(FormatInitSchema):
        __doc__ = "Validate an email address."

    class InputSchema(Node.InputSchema):
        email_address: str = Field(
            description="The email address to validate",
            examples=["hello@tryplurally.com"],
            max_length=320,
            format="email",
        )

    class OutputSchema(Node.OutputSchema):
        is_valid: bool = Field(
            title="Is Email Address Valid",
            description="Whether the email address is valid",
            examples=[True],
        )
        email_address: str = Field(
            description="The email address that was validated",
            examples=["hello@tryplurally.com"],
        )

    def forward(self, node_input: InputSchema) -> bool:
        try:
            emailinfo = validate_email(node_input.email_address, check_deliverability=False)
            self.outputs["email_address"] = emailinfo.normalized
            self.outputs["is_valid"] = True
        except EmailNotValidError:
            self.outputs["email_address"] = node_input.email_address
            self.outputs["is_valid"] = False


class MakeStructure(Node):
    ICON = "format"

    class InitSchema(FormatInitSchema):
        __doc__ = "Make a structure."
        output_fields: List[NameableHandle] = get_nameable_fields(
            title="Outputs",
            description="The different fields of the structure.",
            examples=["Name", "Age"],
            placeholder="Enter field name, example: Name",
            json_schema_extra_extra={"is_output": True, "name_singular": "Output"},
        )

    class InputSchema(Node.InputSchema):
        input: Auto = Field()

    class OutputSchema(Node.OutputSchema):
        model_config = ConfigDict(json_schema_extra={"can-add-fields": True})

    def __init__(self, init_inputs: Node.InitSchema):
        self._output_fields = init_inputs.output_fields
        super().__init__(init_inputs)

    @property
    def output_fields(self):
        return self._output_fields

    @output_fields.setter
    def output_fields(self, value):
        value = [v if isinstance(v, NameableHandle) else NameableHandle(**v) for v in value]
        assert len(set(field._clean for field in value)) == len(value), f"Output fields must be unique {value}"

        self._output_fields = value
        self._set_schemas()
        self.src_handles = self._get_handles(self.OutputSchema, None)

    def _set_schemas(self) -> None:
        # create pydantic model from output_fields
        out_fields_map = {}
        for field in self.output_fields:
            field_type = HANDLE_TYPE_MAP[field.type]
            json_schema_extra = {"handle_id": field.handle_id}

            type_friendly = HANDLE_TYPE_FRIENDLY.get(field.type)
            if type_friendly:
                json_schema_extra["type-friendly"] = type_friendly

            out_fields_map[field._clean] = (
                field_type,
                Field(
                    ...,
                    title=field.free,
                    json_schema_extra=json_schema_extra,
                ),
            )
        self.OutputSchema = create_model("OutputSchema", **out_fields_map, __base__=MakeStructure.OutputSchema)
        input_schema = create_model("Input", **out_fields_map)
        self.InputSchema = create_model("InputSchema", input=(input_schema, Field()), __base__=Node.InputSchema)

    def serialize(self):
        return super().serialize() | {
            "output_fields": [o.model_dump() for o in self.output_fields],
            "output_schema": replace_refs(self.OutputSchema.model_json_schema()),
            "input_schema": replace_refs(self.InputSchema.model_json_schema()),
        }

    @classmethod
    def _parse(cls, **kwargs):
        kwargs = load_from_json_dict(kwargs)
        kwargs["output_fields"] = [NameableHandle(**o) for o in kwargs["output_fields"]]
        return cls(cls.InitSchema(**kwargs))

    def forward(self, node_input: InputSchema):
        self.outputs = self.OutputSchema(**node_input.input.model_dump()).model_dump()

    def add_source_handle(self, tgt_handle):
        """
        tgt_handle is the handle that one wants to connect to the node while adding a src_handle
        """
        handle_type = HandleType.AUTO
        new_src_handle = NameableHandle(free=tgt_handle, type=handle_type)
        ix = 1
        while new_src_handle._clean in [i._clean for i in self.output_fields]:
            new_src_handle = NameableHandle(free=new_src_handle.free + f" {ix}", type=handle_type)
        self.output_fields = [*self.output_fields, new_src_handle]
        return new_src_handle._clean


class Concat(Node):
    ICON = "format"

    class InitSchema(FormatInitSchema):
        __doc__ = "Make a structure."
        input_fields: List[NameableHandle] = get_nameable_fields(
            title="Inputs",
            description="The different list to concat.",
            json_schema_extra_extra={"is_input": True, "name_singular": "Input"},
        )

    class InputSchema(Node.InputSchema):
        model_config = ConfigDict(json_schema_extra={"can-add-fields": True})

    class OutputSchema(Node.OutputSchema):
        output: List[Auto] = Field()

    def __init__(self, init_inputs: Node.InitSchema):
        self._input_fields = init_inputs.input_fields
        super().__init__(init_inputs)

    @property
    def input_fields(self):
        return self._input_fields

    @input_fields.setter
    def input_fields(self, value):
        value = [v if isinstance(v, NameableHandle) else NameableHandle(**v) for v in value]
        assert len(set(field._clean for field in value)) == len(value), f"Output fields must be unique {value}"

        self._input_fields = value
        self._set_schemas()
        self.tgt_handles = self._get_handles(self.InputSchema, None)

    def _set_schemas(self) -> None:
        # create pydantic model from input_fields
        in_fields_map = {}
        for field in self.input_fields:
            field_type = HANDLE_TYPE_MAP[field.type]
            json_schema_extra = {"handle_id": field.handle_id}

            type_friendly = HANDLE_TYPE_FRIENDLY.get(field.type)
            if type_friendly:
                json_schema_extra["type-friendly"] = type_friendly

            in_fields_map[field._clean] = (
                field_type,
                Field(
                    ...,
                    title=field.free,
                    json_schema_extra=json_schema_extra,
                ),
            )
        # self.OutputSchema = create_model(
        #     "OutputSchema", **in_fields_map, __base__=MakeStructure.OutputSchema
        # )
        self.InputSchema = create_model("InputSchema", **in_fields_map, __base__=Concat.InputSchema)

    def serialize(self):
        return super().serialize() | {
            "input_fields": [o.model_dump() for o in self.input_fields],
            "output_schema": replace_refs(self.OutputSchema.model_json_schema()),
            "input_schema": replace_refs(self.InputSchema.model_json_schema()),
        }

    @classmethod
    def _parse(cls, **kwargs):
        kwargs = load_from_json_dict(kwargs)
        kwargs["input_fields"] = [NameableHandle(**o) for o in kwargs["input_fields"]]
        return cls(cls.InitSchema(**kwargs))

    def forward(self, node_input: InputSchema):
        concat = []
        for field in self.input_fields:
            concat.extend(getattr(node_input, field._clean))
        self.outputs["output"] = concat

    def add_target_handle(self, src_handle):
        handle_type = HandleType.AUTO
        new_src_handle = NameableHandle(free=src_handle, type=handle_type)
        ix = 1
        while new_src_handle._clean in [i._clean for i in self.input_fields]:
            new_src_handle = NameableHandle(free=new_src_handle.free + f" {ix}", type=handle_type)
        self.input_fields = [*self.input_fields, new_src_handle]
        return new_src_handle._clean


__all__ = [
    "FormatText",
    "FormatTable",
    "TableToTextSimple",
    "CsvToTable",
    "ToTable",
    "DateTimeManipulate",
    "FormatDatetime",
    "ValidateEmailAddress",
    "MakeStructure",
    "Concat",
    "HtmlCreate",
    "FormatJinja",
]
