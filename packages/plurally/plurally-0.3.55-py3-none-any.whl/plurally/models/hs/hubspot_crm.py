from datetime import datetime
from enum import Enum
from typing import List

from hubspot.crm.companies.models import (
    PublicObjectSearchRequest as CompanyPublicObjectSearchRequest,
)
from hubspot.crm.companies.models import (
    SimplePublicObjectInputForCreate as CompanySimplePublicObjectInputForCreate,
)
from hubspot.crm.contacts import (
    PublicObjectSearchRequest as ContactPublicObjectSearchRequest,
)
from hubspot.crm.contacts import (
    SimplePublicObjectInputForCreate as ContactSimplePublicObjectInputForCreate,
)
from hubspot.crm.deals.models import (
    PublicObjectSearchRequest as DealPublicObjectSearchRequest,
)
from hubspot.crm.deals.models import (
    SimplePublicObjectInputForCreate as DealSimplePublicObjectInputForCreate,
)
from hubspot.crm.objects import PublicObjectSearchRequest, SimplePublicObjectInput
from loguru import logger
from pydantic import BaseModel, ConfigDict, Field, create_model, field_validator

from plurally.models import hubspot_industries
from plurally.models.crm.actions import CrmAction, render_actions_html
from plurally.models.hs.assocs import (
    Association,
    AssociationTo,
    ContactToCall,
    ContactToCompany,
    DealToCompany,
)
from plurally.models.hs.base import (
    DEFAULT_CALL_PROPERTIES,
    DEFAULT_COMPANY_PROPERTIES,
    DEFAULT_CONTACT_PROPERTIES,
    DEFAULT_DEAL_PROPERTIES,
    REQUIRED_CALL_PROPERTIES,
    REQUIRED_COMPANY_PROPERTIES,
    REQUIRED_CONTACT_PROPERTIES,
    REQUIRED_DEAL_PROPERTIES,
    HubspotBase,
    HubspotEntityCreateBuilder,
    HubspotEntityReadBuilder,
    HubspotModelBase,
    HubspotObjectType,
    associations,
    validate_properties_generic,
)
from plurally.models.hs.task import (
    DEFAULT_TASK_PROPERTIES,
    REQUIRED_TASK_PROPERTIES,
    HubspotTaskCreate,
)
from plurally.models.hs.utils import validate_timestamp
from plurally.models.node import Node
from plurally.models.utils import get_normalized_amount, get_normalized_domain_from_url


class HubspotDealStage(Enum):
    APPOINTMENT_SCHEDULED = "appointmentscheduled"
    QUALIFIED_TO_BUY = "qualifiedtobuy"
    PRESENTATION_SCHEDULED = "presentationscheduled"
    DECISION_MAKER_BOUGHT_IN = "decisionmakerboughtin"
    CONTRACT_SENT = "contractsent"
    CLOSED_WON = "closedwon"
    CLOSED_LOST = "closedlost"


class HubspotCallCreateModel(HubspotModelBase): ...


class HubspotCallReadModel(HubspotModelBase):
    id: str


class HubspotLeadCreateModel(HubspotModelBase): ...


class HubspotLeadReadModel(HubspotModelBase):
    id: str


class HubspotCompanyCreateModel(HubspotModelBase): ...


class HubspotCompanyReadModel(HubspotModelBase):
    id: str


class HubspotContactCreateModel(HubspotModelBase): ...


class HubspotContactReadModel(HubspotModelBase):
    id: str


class HubspotDealCreateModel(HubspotModelBase): ...


class HubspotDealReadModel(HubspotModelBase):
    id: str


class HubspotContactToCompany(Node):
    IS_DEPRECATED = True
    ICON = "hubspot"

    class InitSchema(Node.InitSchema):
        """
        Create a HubSpot association between a contact and a company.
        """

    DESC = InitSchema.__doc__

    class InputSchema(Node.InputSchema):
        company: HubspotCompanyReadModel = None

    class OutputSchema(Node.OutputSchema):
        association: Association

    def forward(self, node_inputs: InputSchema):
        if not node_inputs.company:
            logger.debug("No company provided, skipping association creation.")
            return {}
        logger.debug(f"Creating association between contact and company with IDs: {node_inputs.company.id}")
        self.outputs["association"] = ContactToCompany(
            to=AssociationTo(id=node_inputs.company.id),
        )


ASSOCS = {
    "HubspotContactToCompany": HubspotContactToCompany,
}


def get_entity_to_assoc(entity_name_title: str):
    def entity_to_assoc(src_node, tgt_node, src_handle):
        kls_name = f"Hubspot{tgt_node.ENTITY_NAME_TITLE}To{entity_name_title}"
        kls = ASSOCS.get(kls_name)
        if not kls:
            raise ValueError(f"Association {kls_name} not found.")
        nodes = [
            kls(
                kls.InitSchema(
                    name=f"Assoc. {tgt_node.ENTITY_NAME_TITLE} To {entity_name_title}",
                    pos_x=(src_node.pos_x + tgt_node.pos_x) / 2,
                    pos_y=(src_node.pos_y + tgt_node.pos_y) / 2,
                )
            )
        ]
        connections = [
            (0, src_handle, 1, src_node.entity_name),
            (1, "association", 2, None),
        ]
        return nodes, connections

    return entity_to_assoc


_HubspotCallsRead = HubspotEntityReadBuilder.build(
    HubspotObjectType.CALL,
    DEFAULT_CALL_PROPERTIES,
    "calls",
)


class HubspotCallsRead(_HubspotCallsRead):
    IS_DEPRECATED = True


_HubspotCompaniesRead = HubspotEntityReadBuilder.build(
    HubspotObjectType.COMPANY,
    DEFAULT_COMPANY_PROPERTIES,
    "companies",
)


class HubspotCompaniesRead(_HubspotCompaniesRead):
    IS_DEPRECATED = True


_HubspotContactsRead = HubspotEntityReadBuilder.build(
    HubspotObjectType.CONTACT,
    DEFAULT_CONTACT_PROPERTIES,
    "contacts",
)


class HubspotContactsRead(_HubspotContactsRead):
    IS_DEPRECATED = True


_HubspotDealsRead = HubspotEntityReadBuilder.build(
    HubspotObjectType.DEAL,
    DEFAULT_DEAL_PROPERTIES,
    "deals",
)


class HubspotDealsRead(_HubspotDealsRead):
    IS_DEPRECATED = True


def get_call_validators(properties):
    validators = {}
    if "hs_timestamp" in properties:
        validators["validate_timestamp"] = field_validator("hs_timestamp")(validate_timestamp)
    return validators


_HubspotCallCreate = HubspotEntityCreateBuilder.build(
    "call",
    "hs_call_title",
    DEFAULT_CALL_PROPERTIES,
    "calls",
    HubspotCallCreateModel,
    HubspotCallReadModel,
    SimplePublicObjectInput,
    PublicObjectSearchRequest,
    associations,
    property_types={"hs_timestamp": datetime},
    property_required=REQUIRED_CALL_PROPERTIES,
    get_validators=get_call_validators,
    # assoc_adapter=get_entity_to_assoc("Call"),
)


class HubspotCallCreate(_HubspotCallCreate):
    IS_DEPRECATED = True


_HubspotContactCreate = HubspotEntityCreateBuilder.build(
    "contact",
    "email",
    DEFAULT_CONTACT_PROPERTIES,
    "contacts",
    HubspotContactCreateModel,
    HubspotContactReadModel,
    ContactSimplePublicObjectInputForCreate,
    ContactPublicObjectSearchRequest,
    associations,
    property_required=REQUIRED_CONTACT_PROPERTIES,
    # assoc_adapter=get_entity_to_assoc("Contact"),
)


class HubspotContactCreate(_HubspotContactCreate):
    IS_DEPRECATED = True


def validate_industry(v):
    v = hubspot_industries.to_enum_value_case(v)
    if v not in hubspot_industries.INDUSTRIES:
        return None
    return v


def get_company_validators(properties):
    validators = {}
    if "industry" in properties:
        # make sure it has a different name than the property
        validators["validate_industry"] = field_validator("industry")(validate_industry)
    if "domain" in properties:
        validators["validate_domain"] = field_validator("domain")(lambda url: get_normalized_domain_from_url(url, False))
    return validators


_HubspotCompanyCreate = HubspotEntityCreateBuilder.build(
    "company",
    "domain",
    DEFAULT_COMPANY_PROPERTIES,
    "companies",
    HubspotCompanyCreateModel,
    HubspotCompanyReadModel,
    CompanySimplePublicObjectInputForCreate,
    CompanyPublicObjectSearchRequest,
    associations,
    get_validators=get_company_validators,
    property_required=REQUIRED_COMPANY_PROPERTIES,
    # assoc_adapter=get_entity_to_assoc("Company"),
)


class HubspotCompanyCreate(_HubspotCompanyCreate):
    IS_DEPRECATED = True


def validate_amount(v):
    v = hubspot_industries.to_enum_value_case(v)
    if v not in hubspot_industries.INDUSTRIES:
        return None
    return v


def get_deal_validators(properties):
    validators = {}
    if "amount" in properties:
        validators["validate_amount"] = field_validator("amount")(lambda url: get_normalized_amount(url, False))
    if "hs_timestamp" in properties:
        validators["validate_timestamp"] = field_validator("hs_timestamp")(validate_timestamp)
    return validators


_HubspotDealCreate = HubspotEntityCreateBuilder.build(
    "deal",
    "dealname",
    DEFAULT_DEAL_PROPERTIES,
    "deals",
    HubspotDealCreateModel,
    HubspotDealReadModel,
    DealSimplePublicObjectInputForCreate,
    DealPublicObjectSearchRequest,
    associations,
    property_types={"dealstage": HubspotDealStage, "closedate": datetime},
    property_required=REQUIRED_DEAL_PROPERTIES,
    get_validators=get_deal_validators,
    # assoc_adapter=get_entity_to_assoc("Deal"),
)


class HubspotDealCreate(_HubspotDealCreate):
    IS_DEPRECATED = True


class HubspotContactToCompanyUnique(BaseModel):
    contact_email: str
    company_domain: str


class HubspotDealToCompanyUnique(BaseModel):
    dealname: str
    company_domain: str


class HubspotCallToContactUnique(BaseModel):
    hs_call_title: str
    contact_email: str


class HubSpotAutoEntity(HubspotModelBase):
    companies: List[HubspotCompanyCreateModel]
    contacts: List[HubspotContactCreateModel]
    deals: List[HubspotDealCreateModel]
    contact_to_company_assocs: List[HubspotContactToCompanyUnique] = Field([])
    deal_to_company_assocs: List[HubspotDealToCompanyUnique] = Field([])
    call_to_contact_assocs: List[HubspotCallToContactUnique] = Field([])


class HubspotAuto(HubspotBase):
    class InitSchema(Node.InitSchema):
        __doc__ = """Will sync all the relevant data to your HubSpot account."""
        call_properties: str = Field(
            DEFAULT_CALL_PROPERTIES,
            title="Call properties",
            description="The properties to assign to calls (comma separated).",
            json_schema_extra={
                "advanced": True,
                "uiSchema": {
                    "ui:widget": "textarea",
                    "ui:placeholder": f"Comma separated properties, for example: {DEFAULT_CALL_PROPERTIES}",
                },
            },
        )
        company_properties: str = Field(
            DEFAULT_COMPANY_PROPERTIES,
            title="Company properties",
            description="The properties to assign to companies (comma separated).",
            json_schema_extra={
                "advanced": True,
                "uiSchema": {
                    "ui:widget": "textarea",
                    "ui:placeholder": f"Comma separated properties, for example: {DEFAULT_COMPANY_PROPERTIES}",
                },
            },
        )
        contact_properties: str = Field(
            DEFAULT_CONTACT_PROPERTIES,
            title="Contact properties",
            description="The properties to assign to contacts (comma separated).",
            json_schema_extra={
                "advanced": True,
                "uiSchema": {
                    "ui:widget": "textarea",
                    "ui:placeholder": f"Comma separated properties, for example: {DEFAULT_CONTACT_PROPERTIES}",
                },
            },
        )
        task_properties: str = Field(
            DEFAULT_TASK_PROPERTIES,
            title="Task properties",
            description="The properties to assign to tasks (comma separated).",
            json_schema_extra={
                "advanced": True,
                "uiSchema": {
                    "ui:widget": "textarea",
                    "ui:placeholder": f"Comma separated properties, for example: {DEFAULT_TASK_PROPERTIES}",
                },
            },
        )
        deal_properties: str = Field(
            DEFAULT_DEAL_PROPERTIES,
            title="Deal properties",
            description="The properties to assign to deals (comma separated).",
            json_schema_extra={
                "advanced": True,
                "uiSchema": {
                    "ui:widget": "textarea",
                    "ui:placeholder": f"Comma separated properties, for example: {DEFAULT_DEAL_PROPERTIES}",
                },
            },
        )

        update_companies_if_exist: bool = Field(
            True,
            title="Update companies if exist",
            json_schema_extra={"advanced": True},
        )
        update_contacts_if_exist: bool = Field(
            True,
            title="Update contacts if exist",
            json_schema_extra={"advanced": True},
        )
        update_deals_if_exist: bool = Field(
            True,
            title="Update deals if exist",
            json_schema_extra={"advanced": True},
        )

        @field_validator("company_properties")
        def validate_company_properties(cls, v):
            return validate_properties_generic(v, REQUIRED_COMPANY_PROPERTIES)

        @field_validator("contact_properties")
        def validate_contact_properties(cls, v):
            return validate_properties_generic(v, REQUIRED_CONTACT_PROPERTIES)

        @field_validator("deal_properties")
        def validate_deal_properties(cls, v):
            return validate_properties_generic(v, REQUIRED_DEAL_PROPERTIES)

        @field_validator("call_properties")
        def validate_call_properties(cls, v):
            return validate_properties_generic(v, REQUIRED_CALL_PROPERTIES)

        @field_validator("task_properties")
        def validate_task_properties(cls, v):
            return validate_properties_generic(v, REQUIRED_TASK_PROPERTIES)

    DESC = InitSchema.__doc__

    class InputSchema(Node.InputSchema):
        model_config = ConfigDict(use_enum_values=True)
        input: HubSpotAutoEntity = Field(
            ...,
            title="Input",
            description="The different HubSpot entities to create or update.",
            json_schema_extra={"type-friendly": "HubSpot Auto Entity"},
        )

    class OutputSchema(Node.OutputSchema):
        actions_report: str = Field(
            "",
            title="Actions Report",
            description="The actions that were performed.",
            json_schema_extra={"uiSchema": {"ui:widget": "textarea"}},
        )

    def __init__(self, init_inputs: InitSchema):
        self._call_properties = init_inputs.call_properties
        self._company_properties = init_inputs.company_properties
        self._contact_properties = init_inputs.contact_properties
        self._deal_properties = init_inputs.deal_properties
        self._task_properties = init_inputs.task_properties

        self.update_companies_if_exist = init_inputs.update_companies_if_exist
        self.update_contacts_if_exist = init_inputs.update_contacts_if_exist
        self.update_deals_if_exist = init_inputs.update_deals_if_exist
        super().__init__(init_inputs)

    @property
    def task_properties(self):
        return self._task_properties

    @task_properties.setter
    def task_properties(self, value):
        self._task_properties = value
        self._set_schemas()

    @property
    def call_properties(self):
        return self._call_properties

    @call_properties.setter
    def call_properties(self, value):
        self._call_properties = value
        self._set_schemas()

    @property
    def company_properties(self):
        return self._company_properties

    @company_properties.setter
    def company_properties(self, value):
        self._company_properties = value
        self._set_schemas()

    @property
    def contact_properties(self):
        return self._contact_properties

    @contact_properties.setter
    def contact_properties(self, value):
        self._contact_properties = value
        self._set_schemas()

    @property
    def deal_properties(self):
        return self._deal_properties

    @deal_properties.setter
    def deal_properties(self, value):
        self._deal_properties = value
        self._set_schemas()

    def serialize(self):
        return super().serialize() | {
            "call_properties": self.call_properties,
            "task_properties": self.task_properties,
            "company_properties": self.company_properties,
            "contact_properties": self.contact_properties,
            "deal_properties": self.deal_properties,
            "update_companies_if_exist": self.update_companies_if_exist,
            "update_contacts_if_exist": self.update_contacts_if_exist,
            "update_deals_if_exist": self.update_deals_if_exist,
        }

    def associate_call_to_contact(self, assoc, calls, contacts):
        actions = []
        call = calls.get(
            assoc.hs_call_title,
            HubspotCallCreate.get_existing(self.service, assoc.hs_call_title),
        )
        contact = contacts.get(
            assoc.contact_email,
            HubspotContactCreate.get_existing(self.service, assoc.contact_email),
        )
        if contact and call:
            assoc = ContactToCall(to=AssociationTo(id=call.id))
            assoc_entity = HubspotContactCreate.associate(self.service, contact.id, assoc)
            if assoc_entity:
                actions.append(
                    CrmAction(
                        object_type="Contact -> Call",
                        identifier=contact.properties["email"] + " -> " + call.properties["hs_call_title"],
                        action_type="ASSOCIATION",
                        previous_state=None,
                        new_state=None,
                    )
                )
                logger.debug(f"Associated contact {contact.id} with call {call.id}")
        else:
            if not contact:
                logger.debug(f"Contact not found for association: {assoc}")
            if not call:
                logger.debug(f"Call not found for association: {assoc}")
        return actions

    def associate_contact_to_company(self, assoc, contacts, companies):
        actions = []
        contact = contacts.get(
            assoc.contact_email,
            HubspotContactCreate.get_existing(self.service, assoc.contact_email),
        )
        company = companies.get(
            assoc.company_domain,
            HubspotCompanyCreate.get_existing(self.service, assoc.company_domain),
        )

        if contact and company:
            assoc = ContactToCompany(to=AssociationTo(id=company.id))
            assoc_entity = HubspotContactCreate.associate(self.service, contact.id, assoc)
            if assoc_entity:
                actions.append(
                    CrmAction(
                        object_type="Contact -> Company",
                        identifier=contact.properties["email"] + " -> " + company.properties["domain"],
                        action_type="ASSOCIATION",
                        previous_state=None,
                        new_state=None,
                    )
                )
                logger.debug(f"Associated contact {contact.id} with company {company.id}")
        else:
            if not contact:
                logger.debug(f"Contact not found for association: {assoc}")
            if not company:
                logger.debug(f"Company not found for association: {assoc}")
        return actions

    def associate_deal_to_company(self, assoc, deals, companies):
        actions = []
        deal = deals.get(
            assoc.dealname,
            HubspotContactCreate.get_existing(self.service, assoc.dealname),
        )
        company = companies.get(
            assoc.company_domain,
            HubspotCompanyCreate.get_existing(self.service, assoc.company_domain),
        )

        if deal and company:
            assoc = DealToCompany(to=AssociationTo(id=company.id))
            assoc_entity = HubspotDealCreate.associate(self.service, deal.id, assoc)
            if assoc_entity:
                actions.append(
                    CrmAction(
                        object_type="Deal -> Company",
                        identifier=deal.properties["dealname"] + " -> " + company.properties["domain"],
                        action_type="ASSOCIATION",
                        previous_state=None,
                        new_state=None,
                    )
                )
                logger.debug(f"Associated deal {deal.id} with company {company.id}")
        else:
            if not deal:
                logger.debug(f"Deal not found for association: {assoc}")
            if not company:
                logger.debug(f"Company not found for association: {assoc}")
        return actions

    @classmethod
    def get_entity_create_kls(cls, object_type):
        if object_type == HubspotObjectType.CALL:
            return HubspotCallCreate
        if object_type == HubspotObjectType.COMPANY:
            return HubspotCompanyCreate
        if object_type == HubspotObjectType.CONTACT:
            return HubspotContactCreate
        if object_type == HubspotObjectType.DEAL:
            return HubspotDealCreate
        if object_type == HubspotObjectType.TASK:
            return HubspotTaskCreate
        raise ValueError(f"Unknown object type: {object_type}")

    def create_entities(
        self,
        object_type,
        unique_name,
        entities,
        update_if_exists,
        required_properties=None,
    ):
        actions = []
        out_entities = {}
        obj_type_name = object_type.value.title()
        create_kls = self.get_entity_create_kls(object_type)

        for entity in entities:
            out_entity, is_update, previous_state, new_state = create_kls.create_or_update_entity(
                self.service,
                entity,
                # add prefix to make unique
                update_if_exists=update_if_exists,
                required_properties=required_properties,
            )
            if not out_entity:
                logger.debug(f"Entity {obj_type_name} not created")
                continue

            unique_val = out_entity.properties[unique_name]
            if unique_val in out_entities:
                logger.error(f"{obj_type_name} with {unique_name} {unique_val} already exists.")
            out_entities[unique_val] = out_entity

            actions.append(
                CrmAction(
                    object_type=obj_type_name,
                    identifier=unique_val,
                    action_type="UPDATED" if is_update else "CREATED",
                    previous_state=previous_state,
                    new_state=new_state,
                )
            )
        return actions, out_entities

    def forward(self, node_inputs: InputSchema):
        actions = []
        call_actions, calls = self.create_entities(
            HubspotObjectType.CALL,
            "hs_call_title",
            node_inputs.input.calls,
            update_if_exists="make_unique",
            required_properties=REQUIRED_CALL_PROPERTIES,
        )
        actions.extend(call_actions)

        company_actions, companies = self.create_entities(
            HubspotObjectType.COMPANY,
            "domain",
            node_inputs.input.companies,
            update_if_exists=self.update_companies_if_exist,
            required_properties=REQUIRED_COMPANY_PROPERTIES,
        )
        actions.extend(company_actions)

        contact_actions, contacts = self.create_entities(
            HubspotObjectType.CONTACT,
            "email",
            node_inputs.input.contacts,
            update_if_exists=self.update_contacts_if_exist,
            required_properties=REQUIRED_CONTACT_PROPERTIES,
        )
        actions.extend(contact_actions)

        deal_actions, deals = self.create_entities(
            HubspotObjectType.DEAL,
            "dealname",
            node_inputs.input.deals,
            update_if_exists=self.update_deals_if_exist,
            required_properties=REQUIRED_DEAL_PROPERTIES,
        )
        actions.extend(deal_actions)

        task_actions, tasks = self.create_entities(
            HubspotObjectType.TASK,
            "hs_task_subject",
            node_inputs.input.tasks,
            update_if_exists="make_unique",
            required_properties=REQUIRED_TASK_PROPERTIES,
        )
        actions.extend(task_actions)

        for assoc in node_inputs.input.call_to_contact_assocs:
            for hs_call_title in calls:
                if (
                    hs_call_title.startswith(assoc.hs_call_title)
                    and hs_call_title != assoc.hs_call_title
                    and assoc.hs_call_title not in calls
                ):
                    logger.debug(f"Detected change for call assoc {assoc.hs_call_title=}->{hs_call_title}")
                    assoc.hs_call_title = hs_call_title
            actions.extend(self.associate_call_to_contact(assoc, calls, contacts))

        for assoc in node_inputs.input.contact_to_company_assocs:
            actions.extend(self.associate_contact_to_company(assoc, contacts, companies))

        for assoc in node_inputs.input.deal_to_company_assocs:
            actions.extend(self.associate_deal_to_company(assoc, deals, companies))

        self.outputs["actions_report"] = render_actions_html(actions)

    def _set_schemas(self):
        call_entity = HubspotCallCreate.get_entity_model(
            self.call_properties,
            HubspotCallCreate.CREATE_BASE_KLS,
        )
        company_entity = HubspotCompanyCreate.get_entity_model(
            self.company_properties,
            HubspotCompanyCreate.CREATE_BASE_KLS,
        )
        contact_entity = HubspotContactCreate.get_entity_model(
            self.contact_properties,
            HubspotContactCreate.CREATE_BASE_KLS,
        )
        deal_entity = HubspotDealCreate.get_entity_model(
            self.deal_properties,
            HubspotDealCreate.CREATE_BASE_KLS,
        )
        task_entity = HubspotTaskCreate.get_entity_model(
            self.task_properties,
            HubspotTaskCreate.CREATE_BASE_KLS,
        )

        entity = create_model(
            "HubSpotAutoEntity",
            calls=(List[call_entity], Field([])),
            companies=(List[company_entity], Field([])),
            contacts=(List[contact_entity], Field([])),
            deals=(List[deal_entity], Field([])),
            tasks=(List[task_entity], Field([])),
            __base__=HubSpotAutoEntity,
        )
        self.InputSchema = create_model(
            "HubSpotAutoInput",
            input=(entity, Field(...)),
            __base__=Node.InputSchema,
        )


class HubSpotReadAutoEntity(HubspotModelBase): ...


class HubspotReadAuto(HubspotBase):
    class InitSchema(Node.InitSchema):
        __doc__ = """Will read relevant data from your HubSpot account."""
        contact_properties: str = Field(
            DEFAULT_CONTACT_PROPERTIES,
            title="Contact properties",
            description="The properties to read from contacts (comma separated).",
            json_schema_extra={
                "advanced": True,
                "uiSchema": {
                    "ui:widget": "textarea",
                    "ui:placeholder": f"Comma separated properties, for example: {DEFAULT_CONTACT_PROPERTIES}",
                },
            },
        )
        company_properties: str = Field(
            DEFAULT_COMPANY_PROPERTIES,
            title="Company properties",
            description="The properties to read from companies (comma separated).",
            json_schema_extra={
                "advanced": True,
                "uiSchema": {
                    "ui:widget": "textarea",
                    "ui:placeholder": f"Comma separated properties, for example: {DEFAULT_COMPANY_PROPERTIES}",
                },
            },
        )
        deal_properties: str = Field(
            DEFAULT_DEAL_PROPERTIES,
            title="Deal properties",
            description="The properties to read from deals (comma separated).",
            json_schema_extra={
                "advanced": True,
                "uiSchema": {
                    "ui:widget": "textarea",
                    "ui:placeholder": f"Comma separated properties, for example: {DEFAULT_DEAL_PROPERTIES}",
                },
            },
        )

    class InputSchema(Node.InputSchema):
        model_config = ConfigDict(use_enum_values=True)
        company_domain_names: List[str] = Field([])

        @field_validator("company_domain_names")
        def validate_company_domain_names(cls, v):
            v = [get_normalized_domain_from_url(v, True) for v in v]
            return [d for d in v if d]

    class OutputSchema(Node.OutputSchema):
        model_config = ConfigDict(use_enum_values=True)
        entities: HubSpotReadAutoEntity

    def __init__(self, init_inputs: Node.InitSchema):
        self._contact_properties = init_inputs.contact_properties
        self._company_properties = init_inputs.company_properties
        self._deal_properties = init_inputs.deal_properties
        super().__init__(init_inputs)

    def _set_schemas(self):
        company_entity = HubspotCompanyCreate.get_entity_model(
            self.company_properties,
            HubspotCompanyReadModel,
        )
        contact_entity = HubspotContactCreate.get_entity_model(self.contact_properties, HubspotContactReadModel)
        deal_entity = HubspotDealCreate.get_entity_model(self.deal_properties, HubspotDealReadModel)

        entity = create_model(
            "HubSpotAutoEntity",
            companies=(List[company_entity], Field([])),
            contacts=(List[contact_entity], Field([])),
            deals=(List[deal_entity], Field([])),
            __base__=HubSpotReadAutoEntity,
        )
        self.OutputSchema = create_model(
            "HubSpotReadAutoEntity",
            entities=(entity, Field(...)),
            __base__=Node.OutputSchema,
        )

    @property
    def company_properties(self):
        return self._company_properties

    @company_properties.setter
    def company_properties(self, value):
        self._company_properties = value
        self._set_schemas()

    @property
    def contact_properties(self):
        return self._contact_properties

    @contact_properties.setter
    def contact_properties(self, value):
        self._contact_properties = value
        self._set_schemas()

    @property
    def deal_properties(self):
        return self._deal_properties

    @deal_properties.setter
    def deal_properties(self, value):
        self._deal_properties = value
        self._set_schemas()

    def serialize(self):
        return super().serialize() | {
            "contact_properties": self.contact_properties,
            "company_properties": self.company_properties,
            "deal_properties": self.deal_properties,
            # "output_schema": replace_refs(self.OutputSchema), # there is no need to serialize this
        }

    def forward(self, node_inputs: InputSchema):
        # find companies
        company_domain_names = node_inputs.company_domain_names
        if not company_domain_names:
            self.outputs["entities"] = {}
            logger.debug("No company domain names provided")
            return

        q = PublicObjectSearchRequest(
            properties=self.company_properties.split(","),
            filter_groups=[
                {
                    "filters": [
                        {
                            "propertyName": "domain",
                            "operator": "IN",
                            "values": company_domain_names,
                        }
                    ]
                }
            ],
            limit=100,
        )
        companies = self.service.crm.objects.search_api.do_search(
            object_type="companies",
            public_object_search_request=q,
        ).results
        if not companies:
            self.outputs["entities"] = {}
            logger.debug("No companies found")
            return

        logger.debug(f"Found {len(companies)} companies")

        q = PublicObjectSearchRequest(
            properties=self.contact_properties.split(","),
            filter_groups=[
                {
                    "filters": [
                        {
                            "propertyName": "associations.company",
                            "operator": "IN",
                            "values": [company.id for company in companies],
                        }
                    ]
                }
            ],
            limit=100,
        )
        contacts = self.service.crm.objects.search_api.do_search(
            object_type="contacts",
            public_object_search_request=q,
        ).results

        self.outputs["entities"] = {
            "companies": [{**c.properties, "id": c.id} for c in companies],
            "contacts": [{**c.properties, "id": c.id} for c in contacts],
        }


__all__ = [
    "HubspotAuto",
    "HubspotReadAuto",
    "HubspotCallsRead",
    "HubspotCallCreate",
    "HubspotContactsRead",
    "HubspotContactCreate",
    "HubspotCompaniesRead",
    "HubspotCompanyCreate",
    "HubspotDealsRead",
    "HubspotDealCreate",
    "HubspotContactToCompany",
    # "HubspotTasksRead",
    # "HubspotTaskCreate",
]
