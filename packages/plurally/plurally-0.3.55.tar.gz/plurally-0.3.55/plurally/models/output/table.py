from plurally.models.misc import Table
from plurally.models.node import Node
from plurally.models.output.base import BaseOutput, OutputType


class TableOutput(BaseOutput):
    class InputSchema(Node.InputSchema):
        content: Table
        url: str | None = None
        icon: str = ""

    def _get_output_content(self, node_input):
        return {"table": node_input.content.model_dump(mode="json"), "url": node_input.url, "icon": node_input.icon}

    def _get_output_type(self):
        return OutputType.TABLE
