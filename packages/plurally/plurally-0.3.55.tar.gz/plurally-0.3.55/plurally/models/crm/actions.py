from pathlib import Path
from typing import List

from pydantic import BaseModel, ConfigDict, model_validator

from plurally.json_utils import load_from_json_dict
from plurally.localization.template import create_jinja_env
from plurally.models import node
from plurally.models.fields import (
    NameableHandle,
    NameableInputFields,
    get_nameable_fields,
)


class CrmActionType(BaseModel):
    name: str
    label: str


class CrmAction(BaseModel):
    icon: str | None = None
    object_type: str
    identifier: str
    action_type: CrmActionType
    url: str | None = None
    previous_state: dict | None = None
    new_state: dict | None = None
    extra: str | None = None


def render_actions_html(
    actions: List[dict],
    logo: str = None,
) -> str:
    env = create_jinja_env("fr")  # hardcoded locale
    template_path = Path(__file__).parent.parent.parent / "templates" / "crm_actions_report.html"
    assert template_path.exists(), f"Template not found: {template_path}"
    template = env.from_string(template_path.read_text())
    return template.render(
        actions=actions,
        logo=logo,
    )


class RenderActionsHtml(node.Node):
    class InputSchemaBase(node.Node.InputSchema):
        model_config = ConfigDict(json_schema_extra={"can-add-fields": True})

    class InitSchema(node.Node.InitSchema):
        crm_actions_lists: List[NameableHandle] = get_nameable_fields(
            title="Inputs",
            description="The different CRM actions that have been taken",
            default_factory=list,
            json_schema_extra_extra={"is_input": True, "name_singular": "Input"},
        )
        logo: str = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRaAx4OMNKDO78w1GtSY9IKw8zy3RPjRMbWyg&s"

    class OutputSchema(node.Node.OutputSchema):
        html: str

    def __init__(self, init_inputs: node.Node.InitSchema, outputs=None):
        self.renamable_crm_actions_lists = NameableInputFields(
            init_inputs.crm_actions_lists,
            RenderActionsHtml.InputSchemaBase,
            "crm_actions_lists",
        )
        self.logo = init_inputs.logo
        super().__init__(init_inputs, outputs)

    @property
    def crm_actions_lists(self):
        return self.renamable_crm_actions_lists.values

    @crm_actions_lists.setter
    def crm_actions_lists(self, value):
        self.renamable_crm_actions_lists.values = value

    @property
    def InputSchema(self):
        return self.renamable_crm_actions_lists.InputSchema

    @InputSchema.setter
    def InputSchema(self, value):
        self.renamable_crm_actions_lists.InputSchema = value

    @property
    def tgt_handles(self):
        return self.renamable_crm_actions_lists.tgt_handles

    @tgt_handles.setter
    def tgt_handles(self, value):
        self.renamable_crm_actions_lists.tgt_handles = value

    def _set_schemas(self) -> None:
        self.renamable_crm_actions_lists.set_schemas()

    def forward(self, node_input):
        actions = []
        for crm_actions_list in self.crm_actions_lists:
            actions.extend(getattr(node_input, crm_actions_list._clean))
        self.outputs["html"] = render_actions_html(actions, logo=self.logo)

    def serialize(self):
        crm_actions_lists_serialized = self.renamable_crm_actions_lists.serialize()
        return super().serialize() | crm_actions_lists_serialized

    @classmethod
    def _parse(cls, **kwargs):
        kwargs = load_from_json_dict(kwargs)
        NameableInputFields.parse(kwargs, BaseModel, "crm_actions_lists")
        return cls(cls.InitSchema(**kwargs))

    def add_target_handle(self, src_handle):
        return self.renamable_crm_actions_lists.add_target_handle(src_handle)
