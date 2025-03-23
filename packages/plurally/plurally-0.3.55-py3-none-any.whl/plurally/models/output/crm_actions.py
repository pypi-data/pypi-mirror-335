from typing import List

from plurally.models.crm.actions import CrmAction
from plurally.models.node import Node
from plurally.models.output.base import BaseOutput, OutputType


class CrmActionsOutput(BaseOutput):
    class InputSchema(Node.InputSchema):
        actions: List[CrmAction] = []

    def _get_output_content(self, node_input):
        return [action.model_dump(mode="json") for action in node_input.actions]

    def _get_output_type(self):
        return OutputType.CRM_ACTIONS
