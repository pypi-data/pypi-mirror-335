from plurally.models.misc import Table
from plurally.models.node import Node
from plurally.models.output.base import BaseOutput, OutputType


class TextOutput(BaseOutput):
    class InputSchema(Node.InputSchema):
        content: str

    def _get_output_content(self, node_input):
        return node_input.content

    def _get_output_type(self):
        return OutputType.TEXT


class HtmlOutput(BaseOutput):
    class InputSchema(Node.InputSchema):
        content: str

    def _get_output_content(self, node_input):
        return node_input.content

    def _get_output_type(self):
        return OutputType.HTML


class MarkdownOutput(BaseOutput):
    class InputSchema(Node.InputSchema):
        previous_content: str | None = None
        content: str

    def _get_output_content(self, node_input):
        return {
            "previous_content": node_input.previous_content,
            "content": node_input.content,
            "original": node_input.content,
        }

    def _get_output_type(self):
        return OutputType.MARKDOWN
