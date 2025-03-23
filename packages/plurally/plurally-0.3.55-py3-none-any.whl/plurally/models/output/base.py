import enum
from typing import Any, List
from pydantic import Field, create_model

from rq import get_current_job

from plurally.json_utils import replace_refs
from plurally.models.node import Node


class OutputType(str, enum.Enum):
    TEXT = "text"
    HTML = "html"
    CRM_ACTIONS = "crm_actions"
    TABLE = "table"
    MARKDOWN = "markdown"


class BaseOutput(Node):
    class InitSchema(Node.InitSchema):
        key: str = Field("", description="Key to store the output in the job meta")
        is_hidden: bool = Field(False, description="Whether to hide the output in the job meta")

    def _get_output_content(self, node_input):
        raise NotImplementedError

    def _get_output_type(self) -> OutputType:
        raise NotImplementedError

    def build_output(self, node_input) -> dict:
        return {"type": self._get_output_type().value, "content": self._get_output_content(node_input), "is_hidden": self.is_hidden}

    def __init__(self, init_inputs):
        self.key = init_inputs.key or init_inputs.name
        self.is_hidden = init_inputs.is_hidden
        super().__init__(init_inputs)

    def forward(self, node_input) -> None:
        current_job = get_current_job()
        if current_job:
            output = current_job.meta.get("output", {})
            output[self.key] = self.build_output(node_input)
            current_job.meta["output"] = output
            current_job.save_meta()

    def serialize(self):
        return super().serialize() | {"key": self.key, "is_hidden": self.is_hidden}


class StateInput(Node):
    class InitSchema(Node.InitSchema):
        keys: List[str]

    def __init__(self, init_inputs):
        self._keys = init_inputs.keys
        super().__init__(init_inputs)

    @property
    def keys(self):
        return self._keys

    @keys.setter
    def keys(self, value):
        self._keys = value
        self._set_schemas()

    def _set_schemas(self):
        fields = {key: (Any | None, None) for key in self.keys}
        self.OutputSchema = create_model("OutputSchema", **fields, __base__=StateInput.OutputSchema)

    def forward(self, *_, **__) -> None:  # type: ignore
        current_job = get_current_job()
        self.outputs = {}
        if current_job:
            input_map = current_job.meta.get("state", {})
            for key in self.keys:
                self.outputs[key] = input_map.get(key, None)

    def serialize(self):
        return super().serialize() | {"keys": self.keys, "output_schema": replace_refs(self.OutputSchema.model_json_schema())}
