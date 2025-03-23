import io

from pydantic import Field, create_model
from weasyprint import HTML

from plurally.json_utils import replace_refs
from plurally.models.jinja_template import Jinja2Templater
from plurally.models.misc import PdfFile
from plurally.models.node import Node


class PdfCreate(Node):
    ICON = "file-pdf"

    class InitSchema(Node.InitSchema):
        template: str = Field(
            description="The template to render",
            json_schema_extra={"uiSchema": {"ui:widget": "textarea", "ui:options": {"rows": 10}}},
        )

    class InputSchema(Node.InputSchema):
        pdf_data: dict = Field({}, description="The data to fill the template with")
        filename: str = Field(description="The filename of the PDF")

    class OutputSchema(Node.OutputSchema):
        pdf: PdfFile = Field(
            title="PDF",
            description="The PDF file",
            json_schema_extra={
                "type-friendly": "PDF",
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
        pdf_schema = Jinja2Templater.get_input_schema("Pdf Data", self.template)
        kwargs = {}
        if pdf_schema.model_fields:
            kwargs["pdf_data"] = (pdf_schema, ...)
        self.InputSchema = create_model("InputSchema", __base__=PdfCreate.InputSchema, **kwargs)

    def serialize(self):
        return super().serialize() | {
            "template": self.template,
            "input_schema": replace_refs(self.InputSchema.model_json_schema()),
        }

    def forward(self, node_input: InputSchema):
        html = Jinja2Templater.render_jinja2_template(self.template, node_input.pdf_data.model_dump(exclude_none=True))
        pdf_buffer = io.BytesIO()
        HTML(string=html).write_pdf(pdf_buffer)
        self.outputs = {
            "pdf": PdfFile(
                file="UNUSED",
                content=pdf_buffer.getvalue(),
                filename=node_input.filename,
            )
        }
