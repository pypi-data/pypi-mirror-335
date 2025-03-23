from pydantic import Field, create_model

from plurally.json_utils import replace_refs
from plurally.models.jinja_template import Jinja2Templater
from plurally.models.node import Node


class HtmlCreate(Node):
    ICON = "file-html"

    class InitSchema(Node.InitSchema):
        template: str = Field(
            description="The template to render",
            json_schema_extra={"uiSchema": {"ui:widget": "textarea", "ui:options": {"rows": 10}}},
        )

    class InputSchema(Node.InputSchema):
        data: dict = Field({}, description="The data to fill the template with")

    class OutputSchema(Node.OutputSchema):
        html: str = Field(
            title="HTML",
            description="The HTML content",
            json_schema_extra={
                "type-friendly": "HTML",
            },
        )

    def __init__(self, init_inputs: InitSchema):
        self.template = init_inputs.template
        super().__init__(init_inputs)

    @property
    def template(self):
        return self._template

    @template.setter
    def template(self, value):
        self._template = value
        self._set_schemas()

    def _set_schemas(self):
        schema = Jinja2Templater.get_input_schema("Html Data", self.template)
        kwargs = {}
        if schema.model_fields:
            kwargs["data"] = (schema, ...)
        self.InputSchema = create_model("InputSchema", __base__=HtmlCreate.InputSchema, **kwargs)

    def serialize(self):
        return super().serialize() | {
            "template": self.template,
            "input_schema": replace_refs(self.InputSchema.model_json_schema()),
        }

    def forward(self, node_input: InputSchema):
        html = Jinja2Templater.render_jinja2_template(self.template, node_input.data.model_dump(exclude_none=True))
        self.outputs = {"html": html}
