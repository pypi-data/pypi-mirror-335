from pydantic import ConfigDict, Field, field_validator

from plurally.models.node import Node


class ConstantSource(Node):
    class InitSchema(Node.InitSchema):
        """A constant value."""

        model_config = ConfigDict(json_schema_extra={"hide-run": True})

    DESC = InitSchema.__doc__

    class InputSchema(Node.InputSchema): ...

    @property
    def value(self):
        return self.outputs["value"] if self.outputs else None

    @value.setter
    def value(self, value):
        self.outputs["value"] = value

    def __init__(self, init_inputs) -> None:
        super().__init__(init_inputs)
        self.value = init_inputs.value

    def forward(self, _):
        self.outputs = {"value": self.value}

    def serialize(self):
        payload = super().serialize()
        payload["value"] = self.outputs["value"]
        return payload


class Text(ConstantSource):
    ICON = "text"

    class InitSchema(ConstantSource.InitSchema):
        value: str = Field(
            title="Text",
            description="The constant text value.",
            examples=["hello"],
            min_length=1,
            json_schema_extra={
                "uiSchema": {
                    "ui:widget": "textarea",
                    "ui:placeholder": "Write text here",
                },
            },
        )

    class OutputSchema(Node.OutputSchema):
        value: str = Field(json_schema_extra={"constant": True})

        @field_validator("value")
        def strip_value(cls, value):
            return value.strip()


class Integer(ConstantSource):
    ICON = "number"

    class InitSchema(ConstantSource.InitSchema):
        value: int = Field(
            title="Integer",
            description="The constant integer value.",
            examples=[-1, 42],
            json_schema_extra={
                "uiSchema": {
                    "ui:placeholder": "Write integer value here",
                },
            },
        )

    class OutputSchema(Node.OutputSchema):
        value: int = Field(json_schema_extra={"constant": True})


class Number(ConstantSource):
    ICON = "number"

    class InitSchema(ConstantSource.InitSchema):
        value: float = Field(
            title="Number",
            description="The constant number value.",
            examples=[-1.3, 0.3, 42.3],
            json_schema_extra={
                "uiSchema": {
                    "ui:placeholder": "Write number value here",
                },
            },
        )

    class OutputSchema(Node.OutputSchema):
        value: float = Field(json_schema_extra={"constant": True})


class Boolean(ConstantSource):
    ICON = "boolean"

    class InitSchema(ConstantSource.InitSchema):
        value: bool = Field(
            title="True/False",
            description="The constant true or false value.",
        )

    class OutputSchema(Node.OutputSchema):
        value: bool = Field(json_schema_extra={"constant": True})


__all__ = ["Text", "Integer", "Number", "Boolean"]
