import os
from typing import List

import tenacity
from loguru import logger
from pydantic import BaseModel, ConfigDict, Field, create_model

from plurally.models.node import Node
from plurally.models.ol.base import (
    REQUIRED_DEAL_PROPERTIES,
    REQUIRED_NOTE_PROPERTIES,
    REQUIRED_ORGANIZATION_PROPERTIES,
    REQUIRED_PROSPECT_PROPERTIES,
    OverloopBase,
    OverloopModelBase,
    OverloopObjectType,
    OverloopObjectTypeToRoot,
    create_entity,
    read_entity_by_key_vals,
    update_entity,
)
from plurally.models.ol.deal import get_OverloopDealCreate, get_OverloopDealRead
from plurally.models.ol.note import get_OverloopNoteCreate, get_OverloopNoteRead
from plurally.models.ol.org import (
    get_OverloopOrganizationCreate,
    get_OverloopOrganizationRead,
)
from plurally.models.ol.prospect import (
    get_OverloopProspectCreate,
    get_OverloopProspectRead,
)


class OverloopAutoEntity(OverloopModelBase): ...


OverloopObjectTypeToModel = {
    OverloopObjectType.ORGANIZATION: get_OverloopOrganizationRead(),
    OverloopObjectType.DEAL: get_OverloopDealRead(),
    OverloopObjectType.PROSPECT: get_OverloopProspectRead(),
    OverloopObjectType.NOTE: get_OverloopNoteRead(),
}


class OverloopAuto(OverloopBase):
    class InitSchema(Node.InitSchema):
        __doc__ = """Will sync all the relevant data to your Overloop account."""
        update_organizations_if_exist: bool = Field(
            False,
            title="Update organizations if exist",
            json_schema_extra={"advanced": True},
        )
        update_prospects_if_exist: bool = Field(
            False,
            title="Update contacts if exist",
            json_schema_extra={"advanced": True},
        )
        update_deals_if_exist: bool = Field(
            True,
            title="Update deals if exist",
            json_schema_extra={"advanced": True},
        )

    DESC = InitSchema.__doc__

    class InputSchema(Node.InputSchema):
        model_config = ConfigDict(use_enum_values=True)
        input: OverloopAutoEntity = Field(
            ...,
            title="Input",
            description="The different Overloop entities to create or update.",
            json_schema_extra={"type-friendly": "Overloop Auto Entity"},
        )

    class OutputSchema(Node.OutputSchema):
        actions_report: str = Field(
            "",
            title="Actions Report",
            description="The actions that were performed.",
            json_schema_extra={"uiSchema": {"ui:widget": "textarea"}},
        )

    def __init__(self, init_inputs: InitSchema):
        self.update_organizations_if_exist = init_inputs.update_organizations_if_exist
        self.update_prospects_if_exist = init_inputs.update_prospects_if_exist
        self.update_deals_if_exist = init_inputs.update_deals_if_exist
        self._api_key = None
        self.is_resolved = False
        super().__init__(init_inputs)

    @property
    def api_key(self):
        if not self._api_key:
            self._api_key = os.environ.get("OVERLOOP_API_KEY")
            assert self._api_key, "OVERLOOP_API_KEY is required"
        return self._api_key

    def serialize(self):
        return super().serialize() | {
            "update_organizations_if_exist": self.update_organizations_if_exist,
            "update_prospects_if_exist": self.update_prospects_if_exist,
            "update_deals_if_exist": self.update_deals_if_exist,
        }

    def associate_call_to_contact(self, assoc, calls, contacts):
        actions = []
        call = calls.get(
            assoc.hs_call_title,
            OverloopCallCreate.get_existing(self.service, assoc.hs_call_title),
        )
        contact = contacts.get(
            assoc.contact_email,
            OverloopContactCreate.get_existing(self.service, assoc.contact_email),
        )
        if contact and call:
            assoc = ContactToCall(to=AssociationTo(id=call.id))
            assoc_entity = OverloopContactCreate.associate(self.service, contact.id, assoc)
            if assoc_entity:
                actions.append(f"Contact {contact.properties['email']} associated with call {call.properties['hs_call_title']}")
                logger.debug(f"Associated contact {contact.id} with call {call.id}")
        else:
            if not contact:
                logger.debug(f"Contact not found for association: {assoc}")
            if not call:
                logger.debug(f"Call not found for association: {assoc}")
        return actions

    def associate_contact_to_organization(self, assoc, contacts, organizations):
        actions = []
        contact = contacts.get(
            assoc.contact_email,
            OverloopContactCreate.get_existing(self.service, assoc.contact_email),
        )
        organization = organizations.get(
            assoc.organization_domain,
            OverloopOrganizationCreate.get_existing(self.service, assoc.organization_domain),
        )

        if contact and organization:
            assoc = ContactToOrganization(to=AssociationTo(id=organization.id))
            assoc_entity = OverloopContactCreate.associate(self.service, contact.id, assoc)
            if assoc_entity:
                actions.append(f"Contact {contact.properties['email']} associated with organization {organization.properties['domain']}")
                logger.debug(f"Associated contact {contact.id} with organization {organization.id}")
        else:
            if not contact:
                logger.debug(f"Contact not found for association: {assoc}")
            if not organization:
                logger.debug(f"Organization not found for association: {assoc}")
        return actions

    def associate_deal_to_organization(self, assoc, deals, organizations):
        actions = []
        deal = deals.get(
            assoc.dealname,
            OverloopContactCreate.get_existing(self.service, assoc.dealname),
        )
        organization = organizations.get(
            assoc.organization_domain,
            OverloopOrganizationCreate.get_existing(self.service, assoc.organization_domain),
        )

        if deal and organization:
            assoc = DealToOrganization(to=AssociationTo(id=organization.id))
            assoc_entity = OverloopDealCreate.associate(self.service, deal.id, assoc)
            if assoc_entity:
                actions.append(f"Deal {deal.properties['dealname']} associated with organization {organization.properties['domain']}")
                logger.debug(f"Associated deal {deal.id} with organization {organization.id}")
        else:
            if not deal:
                logger.debug(f"Deal not found for association: {assoc}")
            if not organization:
                logger.debug(f"Organization not found for association: {assoc}")
        return actions

    def create_or_update(
        self,
        root,
        unique_property_name: str | None,
        unique_property_value,
        model_kls,
        payload: BaseModel,
        required_properties=None,
        update_if_exists=False,
        exclude_fields=None,
    ):
        required_properties = required_properties or []
        for prop in required_properties:
            if not getattr(payload, prop, None):
                logger.debug(f"Entity {payload} missing required property {prop}")
                return None, False

        existing_entity = None
        is_update = False
        if unique_property_name:
            existing_entity = read_entity_by_key_vals(
                root,
                [(unique_property_name, unique_property_value)],
                self.api_key,
                model_kls=model_kls,
            )
        if existing_entity:
            if update_if_exists:
                out_entity = update_entity(
                    root, existing_entity.id, payload, self.api_key, model_kls=model_kls, exclude_fields=exclude_fields
                )
                logger.debug(f"Entity already {root} (id={out_entity.id}) exists - updated")
            else:
                out_entity = existing_entity
                logger.debug(f"Entity already {root} (id={out_entity.id}) exists - skipping")
            is_update = True
        else:
            out_entity = create_entity(root, payload, self.api_key, model_kls=model_kls, exclude_fields=exclude_fields)
            logger.debug(f"Created entity {root} (id={out_entity.id})")
        return out_entity, is_update

    def create_entities(
        self,
        object_type: OverloopObjectType,
        unique_property_name: str | None,
        payloads,
        update_if_exists,
        required_properties=None,
    ):
        logger.debug(f"Creating {len(payloads)} {object_type.value}")
        actions = []
        out_entities = {}
        object_type_title = object_type.value.title()
        root = OverloopObjectTypeToRoot[object_type]
        model_kls = OverloopObjectTypeToModel[object_type]
        exclude_fields = getattr(model_kls, "exclude", [])
        for payload in payloads:
            unique_property_value = None
            if unique_property_name:
                unique_property_value = getattr(payload, unique_property_name)
            out_entity, is_update = self.create_or_update(
                root,
                unique_property_name=unique_property_name,
                unique_property_value=unique_property_value,
                payload=payload,
                required_properties=required_properties,
                update_if_exists=update_if_exists,
                model_kls=model_kls,
                exclude_fields=exclude_fields,
            )
            if not out_entity:
                logger.debug(f"Entity {object_type_title} not created")
                continue
            identifier = unique_property_value or payload.title  # excluded title used internally (see OverloopNoteCreate)
            out_entities[identifier] = out_entity

            url = getattr(out_entity, "url", f"https://app.overloop.com{root}/{out_entity.id}")
            if is_update:
                actions.append(f"{object_type_title} {unique_property_value} updated {url}")
            else:
                actions.append(f"{object_type_title} {unique_property_value} created {url}")

        return actions, out_entities

    def resolve_input_type_self(self):
        if not self.is_resolved:
            logger.debug("Resolving input type")
            self._set_schemas(self.api_key)
            self.is_resolved = True

    @tenacity.retry(
        wait=tenacity.wait_fixed(2),
        stop=tenacity.stop_after_attempt(3),
        retry=tenacity.retry_if_exception_type(Exception),
    )
    def forward(self, node_inputs: InputSchema):
        try:
            actions = []
            organization_actions, organizations = self.create_entities(
                OverloopObjectType.ORGANIZATION,
                "website",
                payloads=node_inputs.input.organizations,
                update_if_exists=self.update_organizations_if_exist,
                required_properties=REQUIRED_ORGANIZATION_PROPERTIES,
            )
            actions.extend(organization_actions)

            prospect_actions, prospects = self.create_entities(
                OverloopObjectType.PROSPECT,
                "email",
                payloads=node_inputs.input.prospects,
                update_if_exists=self.update_prospects_if_exist,
                required_properties=REQUIRED_PROSPECT_PROPERTIES,
            )
            actions.extend(prospect_actions)

            deal_actions, deals = self.create_entities(
                OverloopObjectType.DEAL,
                "title",
                payloads=node_inputs.input.deals,
                update_if_exists=self.update_deals_if_exist,
                required_properties=REQUIRED_DEAL_PROPERTIES,
            )
            actions.extend(deal_actions)

            note_actions, notes = self.create_entities(
                OverloopObjectType.NOTE,
                None,
                payloads=node_inputs.input.notes,
                update_if_exists=False,
                required_properties=REQUIRED_NOTE_PROPERTIES,
            )
            actions.extend(note_actions)

            # task_actions, tasks = self.create_entities(
            #     OverloopObjectType.TASK,
            #     "hs_task_subject",
            #     node_inputs.input.tasks,
            #     update_if_exists="make_unique",
            #     required_properties=REQUIRED_TASK_PROPERTIES,
            # )
            # actions.extend(task_actions)

            # for assoc in node_inputs.input.call_to_contact_assocs:
            #     for hs_call_title in calls:
            #         if (
            #             hs_call_title.startswith(assoc.hs_call_title)
            #             and hs_call_title != assoc.hs_call_title
            #             and assoc.hs_call_title not in calls
            #         ):
            #             logger.debug(
            #                 f"Detected change for call assoc {assoc.hs_call_title=}->{hs_call_title}"
            #             )
            #             assoc.hs_call_title = hs_call_title
            #     actions.extend(self.associate_call_to_contact(assoc, calls, contacts))

            # for assoc in node_inputs.input.contact_to_organization_assocs:
            #     actions.extend(
            #         self.associate_contact_to_organization(assoc, contacts, organizations)
            #     )

            # for assoc in node_inputs.input.deal_to_organization_assocs:
            #     actions.extend(self.associate_deal_to_organization(assoc, deals, organizations))

            if actions:
                self.outputs["actions_report"] = "The following Overloop changes were made:\n" + "\n".join(actions)
            else:
                self.outputs["actions_report"] = "No Overloop changes were made."
        except Exception as e:
            self.is_resolved = False

            # TODO if it is an issue with modified custom field - handle here for this case.
            # next case will be resolved by means of rersolving the input type
            raise e

    def _set_schemas(self, api_key: str = None):
        org_entity = get_OverloopOrganizationCreate()
        prospect_entity = get_OverloopProspectCreate()
        deal_entity = get_OverloopDealCreate(api_key)
        note_entity = get_OverloopNoteCreate()

        entity = create_model(
            "OverloopAutoEntity",
            organizations=(List[org_entity], Field([])),
            prospects=(List[prospect_entity], Field([])),
            deals=(List[deal_entity], Field([])),
            notes=(List[note_entity], Field([])),
            __base__=OverloopAutoEntity,
        )
        self.InputSchema = create_model(
            "OverloopAutoInput",
            input=(entity, Field(...)),
            __base__=Node.InputSchema,
        )


__all__ = ["OverloopAuto"]
