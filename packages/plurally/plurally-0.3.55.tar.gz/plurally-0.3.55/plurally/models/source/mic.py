from pydantic import Field

from plurally.models.misc import AudioFile
from plurally.models.node import Node


class Mic(Node):
    IS_TRIGGER = True
    ICON = "mic"

    class InitSchema(Node.InitSchema): ...

    class InputSchema(Node.InputSchema): ...

    class OutputSchema(Node.OutputSchema):
        audio: AudioFile = Field(
            title="Audio",
            description="The audio file",
            json_schema_extra={
                "type-friendly": "Audio",
            },
        )

    def start_worker(self) -> bool:
        return True

    def forward(self, node_inputs):
        return node_inputs


__all__ = ["Mic"]
