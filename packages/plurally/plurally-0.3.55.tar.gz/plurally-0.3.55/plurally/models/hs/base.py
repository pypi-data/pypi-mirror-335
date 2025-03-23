import enum
import os
import uuid
from datetime import datetime, timezone
from typing import Any, List, Union

import requests
import tenacity
from hubspot import HubSpot
from hubspot.crm.objects import AssociationSpec, PublicObjectSearchRequest
from loguru import logger
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    create_model,
    field_validator,
    model_validator,
)

from plurally.json_utils import replace_refs
from plurally.models import utils
from plurally.models.hs.assocs import Association
from plurally.models.misc import Table
from plurally.models.node import Node

HUBSPOT_FILTERS_TYPE_FRIENDLY = "Hubspot Filters"
DEFAULT_CONTACT_PROPERTIES = "email, firstname, lastname, phone, company, jobtitle"
DEFAULT_COMPANY_PROPERTIES = "domain, name, industry, description"
DEFAULT_DEAL_PROPERTIES = "dealname, amount, dealstage, closedate"
DEFAULT_CALL_PROPERTIES = "hs_timestamp, hs_call_title, hs_call_body"
DEFAULT_LEAD_PROPERTIES = "leadname, leadstatus, leadsource"
REQUIRED_CONTACT_PROPERTIES = ("email",)
REQUIRED_COMPANY_PROPERTIES = ("domain",)
REQUIRED_DEAL_PROPERTIES = ("dealname",)
REQUIRED_CALL_PROPERTIES = ("hs_call_title", "hs_timestamp")


class HubspotModelBase(BaseModel):
    model_config = ConfigDict(use_enum_values=True)


class HubspotObjectType(enum.Enum):
    CALL = "call"
    CONTACT = "contact"
    COMPANY = "company"
    DEAL = "deal"
    LEAD = "lead"
    TASK = "task"


class HubspotOperator(enum.Enum):
    LT = "LT"
    LTE = "LTE"
    GT = "GT"
    GTE = "GTE"
    EQ = "EQ"
    NEQ = "NEQ"
    BETWEEN = "BETWEEN"
    IN = "IN"
    NOT_IN = "NOT_IN"
    HAS_PROPERTY = "HAS_PROPERTY"
    NOT_HAS_PROPERTY = "NOT_HAS_PROPERTY"
    CONTAINS_TOKEN = "CONTAINS_TOKEN"
    NOT_CONTAINS_TOKEN = "NOT_CONTAINS_TOKEN"


class ContactAssociationProperties(enum.Enum):
    EMAIL = "email"
    LASTNAME = "last name"
    FIRSTNAME = "first name"


class CompanyAssociationProperties(enum.Enum):
    DOMAIN = "domain"
    NAME = "name"


class DealAssociationProperties(enum.Enum):
    DEALNAME = "dealname"


class CallAssociationProperties(enum.Enum):
    HS_CALL_TITLE = "hs_call_title"


class TaskAssociationProperties(enum.Enum):
    TASKNAME = "taskname"


class LeadAssociationProperties(enum.Enum):
    LEADNAME = "leadname"


PROPERTIES = {
    HubspotObjectType.CONTACT: ContactAssociationProperties,
    HubspotObjectType.COMPANY: CompanyAssociationProperties,
    HubspotObjectType.DEAL: DealAssociationProperties,
    HubspotObjectType.CALL: CallAssociationProperties,
    HubspotObjectType.TASK: TaskAssociationProperties,
    HubspotObjectType.LEAD: LeadAssociationProperties,
}


supported_operators = [
    HubspotOperator.EQ,
    HubspotOperator.NEQ,
    HubspotOperator.IN,
    HubspotOperator.NOT_IN,
    HubspotOperator.HAS_PROPERTY,
    HubspotOperator.NOT_HAS_PROPERTY,
    HubspotOperator.CONTAINS_TOKEN,
    HubspotOperator.NOT_CONTAINS_TOKEN,
]


def validate_properties_generic(v, req_props):
    v = list(set([s.strip() for s in v.split(",")]))
    issues = []
    for req_prop in req_props:
        if req_prop not in v:
            issues.append(req_prop)
    if issues:
        raise ValueError(f"Properties must contain the following properties: {', '.join(issues)}")
    return ",".join(v)


class HubspotFilter(BaseModel):
    model_config = ConfigDict(use_enum_values=True)
    propertyName: str
    operator: HubspotOperator
    value: Any


class HubspotFilterDict(BaseModel):
    filters: List[HubspotFilter]


_SupportedOperators = enum.Enum("SupportedOperators", [(v.name, v.value) for v in supported_operators])


associations = {
    "associations": (Association, Field(None, title="Associations")),
}


def get_hubspot_association_filter_kls(object_type: HubspotObjectType):
    possible_to_object_types = [v for v in HubspotObjectType if v != object_type]
    _ToObjectType = enum.Enum("ToObjectType", [(v.name, v.value) for v in possible_to_object_types])
    default_object_type = possible_to_object_types[0]
    to_object_type_one_of = []
    for to_object_type in possible_to_object_types:
        property_names = [p.value for p in PROPERTIES[to_object_type]]
        to_object_type_one_of.append(
            {
                "properties": {
                    "to_object_type": {"const": to_object_type.value},
                    f"{to_object_type.value}_property_name": {
                        "enum": property_names,
                        "title": "Property",
                        "description": "The property to use for the association.",
                        "default": property_names[0],
                    },
                },
                "required": ["to_object_type", f"{to_object_type.value}_property_name"],
            }
        )

    class HubspotAssociationFilter(BaseModel):
        to_object_type: _ToObjectType = Field(  # type: ignore
            default_object_type.value,
            title="Type",
            description="The type of the object to associate to.",
        )
        operator: _SupportedOperators = Field(  # type: ignore
            HubspotOperator.EQ,
            title="Operator",
            description="The operator to use for the association.",
        )
        model_config = ConfigDict(
            use_enum_values=True,
            json_schema_extra={"dependencies": {"to_object_type": {"oneOf": to_object_type_one_of}}},
        )

        # we do not want this in UI Form, it's handled with the dependencies
        # but we need it for programmatic instantiation
        # therefore we hide it (computed field won't cut it)
        property_name: str | None = Field(None, format="hidden")

        @field_validator("to_object_type", mode="after")
        def validate_to_object_type(cls, v):
            return HubspotObjectType(v if isinstance(v, str) else v.name).value

        @field_validator("operator", mode="after")
        def validate_operator(cls, v):
            return HubspotOperator(v if isinstance(v, str) else v.name).value

        @model_validator(mode="before")
        @classmethod
        def validate_model(cls, data):
            for obj_type in possible_to_object_types:
                selected_obj_type = HubspotObjectType(data["to_object_type"])
                if obj_type == selected_obj_type:
                    allowed_props = [p.value for p in PROPERTIES[obj_type]]
                    # we must override here - as if the user selects a different to_object_type
                    # the property_name will be set to an invalid value
                    key = f"{obj_type.value}_property_name"
                    if key in data:
                        # override
                        data["property_name"] = data[key]
                    # we keep property_name only if not specific key is present
                    # as this means that it was parsed from serialization (specific keys are not serialized)
                    if "property_name" not in data:
                        raise ValueError(f"Could not find generic or specific key for property_name in {data}")
                    if data["property_name"] not in allowed_props:
                        raise ValueError(f"Property name must be one of {allowed_props}")
                    break
            else:
                raise ValueError(f"Invalid to_object_type {data['to_object_type']}")
            return data

    return HubspotAssociationFilter


HubspotCompanyAssociationFilter = get_hubspot_association_filter_kls(HubspotObjectType.COMPANY)
HubspotContactAssociationFilter = get_hubspot_association_filter_kls(HubspotObjectType.CONTACT)
HubspotDealAssociationFilter = get_hubspot_association_filter_kls(HubspotObjectType.DEAL)


class HubspotBase(Node):
    SCOPES = [
        "crm.objects.contacts.read",
        "crm.objects.contacts.write",
        "crm.objects.companies.read",
        "crm.objects.companies.write",
        "crm.objects.deals.read",
        "crm.objects.deals.write",
    ]
    ICON = "hubspot"

    def __init__(self, init_inputs: Node.InitSchema):
        super().__init__(init_inputs)
        assert self.SCOPES is not None, "SCOPES must be defined in the subclass"
        self._service = None
        self._token = None
        self._token_expiry = None
        self._user_id = None

    @property
    def user_id(self):
        # unused for now
        if self._user_id is None:
            r = requests.get(f"https://api.hubapi.com/oauth/v1/access-tokens/{self.token()}")
            self._user_id = r.json()["user_id"]
            logger.debug(f"Fetched user ID: {self._user_id}")
        return self._user_id

    def token(self):
        now = datetime.now(tz=timezone.utc).replace(tzinfo=None)
        if self._token is None or self._token_expiry < now:
            self.reset()
            self._token, self._token_expiry = utils.get_access_token(self.SCOPES)
        return self._token

    @property
    def service(self) -> HubSpot:
        if self._service is None:
            self._service = HubSpot(access_token=self.token())
        return self._service

    def reset(self):
        self._token = None
        self._token_expiry = None
        self._service = None


class HubspotEntityReadBuilder:
    @classmethod
    def build(
        cls,
        object_type: HubspotObjectType,
        properties_default: str,
        api_name: str,
    ):
        assoc_filter_type = get_hubspot_association_filter_kls(object_type)

        class HubspotEntityRead(HubspotBase):
            class InitSchema(Node.InitSchema):
                __doc__ = f"""Read {object_type.value.title()} from HubSpot. Possibility to filter by properties and associations."""

                properties: str = Field(
                    properties_default,
                    title="Properties",
                    description="The properties to fetch (comma separated).",
                    json_schema_extra={
                        "uiSchema": {
                            "ui:widget": "textarea",
                            "ui:placeholder": f"Comma separated properties, for example: {properties_default}",
                        }
                    },
                )
                associations: List[assoc_filter_type] = Field(  # type: ignore
                    [],
                    json_schema_extra={
                        "name_singular": "Association",
                        "uiSchema": {
                            "ui:label": False,
                            "items": {
                                "ui:label": False,
                                "ui:grid": [
                                    (
                                        "to_object_type",
                                        {
                                            "base": 12,
                                            "sm": 4,
                                        },
                                    ),
                                    *[
                                        (
                                            f"{o.value}_property_name",
                                            {"base": 12, "sm": 4},
                                        )
                                        for o in HubspotObjectType
                                        if o != object_type
                                    ],
                                    ("operator", {"base": 12, "sm": 4}),
                                ],
                            },
                        },
                    },
                )
                limit: int = Field(
                    100,
                    title="Limit",
                    description=f"The number of {object_type.value} to fetch.",
                    json_schema_extra={"advanced": True},
                )

            class OutputSchema(Node.OutputSchema):
                entities: Table = Field(..., title=f"{object_type.value.capitalize()}s")

            class InputSchema(Node.InputSchema):
                filter_groups: List[HubspotFilterDict] = Field(
                    [],
                    title="Filters",
                    description="The filters to apply in the search.",
                    json_schema_extra={"type-friendly": HUBSPOT_FILTERS_TYPE_FRIENDLY},
                )

            def __init__(self, init_inputs: Node.InitSchema):
                self.limit = init_inputs.limit
                self.properties = init_inputs.properties
                self._associations = init_inputs.associations
                super().__init__(init_inputs)

            @property
            def associations(self):
                return self._associations

            @associations.setter
            def associations(self, value):
                value = [v if isinstance(v, assoc_filter_type) else assoc_filter_type(**v) for v in value]
                self._associations = value
                self._set_schemas()
                self.tgt_handles = self._get_handles(self.InputSchema, None)

            def _set_schemas(self):
                extra_inputs = {}
                for assoc in self.associations:
                    op = HubspotOperator(assoc.operator)
                    key = f"{assoc.to_object_type}_{assoc.property_name}"
                    desc = f"Association filter for {assoc.to_object_type.capitalize()} {assoc.property_name}."
                    if op in [
                        HubspotOperator.EQ,
                        HubspotOperator.NEQ,
                        HubspotOperator.CONTAINS_TOKEN,
                        HubspotOperator.NOT_CONTAINS_TOKEN,
                    ]:
                        title = f"{assoc.to_object_type.capitalize()} {assoc.property_name}"
                        extra_inputs[key] = (
                            str,  # ??? could be something else as well i guess
                            Field(
                                title=title,
                                description=desc,
                            ),
                        )
                    elif op in [HubspotOperator.IN, HubspotOperator.NOT_IN]:
                        title = f"{assoc.to_object_type.capitalize()} {assoc.property_name}"
                        extra_inputs[key] = (
                            List[str],
                            Field(
                                title=title,
                                description=desc,
                            ),
                        )
                    elif op in [
                        HubspotOperator.HAS_PROPERTY,
                        HubspotOperator.NOT_HAS_PROPERTY,
                    ]:
                        pass

                self.InputSchema = create_model(
                    f"{object_type.name.capitalize()}Input",
                    **extra_inputs,
                    __base__=HubspotEntityRead.InputSchema,
                )

            def serialize(self):
                return super().serialize() | {
                    "limit": self.limit,
                    "properties": self.properties,
                    "associations": [assoc.model_dump() for assoc in self.associations],
                    "input_schema": replace_refs(self.InputSchema.model_json_schema()),
                }

            def _build_query_for_assoc(self, assoc_filter, prop_val):  # type: ignore
                value_key = "values" if assoc_filter.operator in ["IN", "NOT_IN"] else "value"
                return PublicObjectSearchRequest(
                    filter_groups=[
                        {
                            "filters": [
                                {
                                    "propertyName": assoc_filter.property_name,
                                    "operator": assoc_filter.operator,
                                    value_key: prop_val,
                                }
                            ]
                        }
                    ],
                    limit=100,
                )

            def _search_for_association(self, assoc_filter: HubspotDealAssociationFilter, prop_val):  # type: ignore
                if os.environ.get("VERBOSE"):
                    logger.debug(f"Searching for object_type={assoc_filter=} {prop_val=}")
                q = self._build_query_for_assoc(assoc_filter, prop_val)
                return self.service.crm.objects.search_api.do_search(
                    object_type=assoc_filter.to_object_type,
                    public_object_search_request=q,
                ).results

            def _create_filter_from_assoc_filter(self, assoc_filter: HubspotDealAssociationFilter, prop_val):  # type: ignore
                search_res = self._search_for_association(assoc_filter, prop_val)
                if not search_res:
                    return None
                return {
                    "propertyName": f"associations.{assoc_filter.to_object_type}",
                    "operator": "IN",
                    "values": [entity.id for entity in search_res],
                }

            def _build_query(self, node_inputs) -> PublicObjectSearchRequest:
                filter_groups = node_inputs.model_dump()["filter_groups"]

                if self.associations:
                    assoc_filters = []
                    for assoc in self.associations:
                        key = f"{assoc.to_object_type}_{assoc.property_name}"
                        prop_val = getattr(node_inputs, key, None)

                        assoc_filter = self._create_filter_from_assoc_filter(assoc, prop_val)
                        if assoc_filter is None:
                            logger.debug(
                                f"No results when searching for object_type={assoc.to_object_type} "
                                f"with property_name={assoc.property_name} "
                                f"and op={assoc.operator}"
                            )
                            # this means that the user wants to filter by an association but there was no results.
                            # then this search should return no results
                            return None

                        logger.debug(f"Adding association filter: {assoc_filter}")
                        assoc_filters.append(assoc_filter)

                    filter_groups = filter_groups or [{"filters": []}]
                    for f in filter_groups:
                        f["filters"] = f.get("filters", []) + assoc_filters

                logger.debug(f"Filter groups: {filter_groups}")
                return PublicObjectSearchRequest(
                    properties=[s.strip() for s in self.properties.split(",")],
                    filter_groups=filter_groups,
                    limit=self.limit,
                )

            def forward(self, node_inputs: InputSchema):
                q = self._build_query(node_inputs)
                if q is None:
                    self.outputs = {"entities": Table(data=[])}
                    return

                entities = self.service.crm.objects.search_api.do_search(object_type=api_name, public_object_search_request=q)
                self.outputs = {"entities": Table(data=[entity.properties for entity in entities.results])}

        return HubspotEntityRead


class HubspotEntityCreateBuilder:
    @classmethod
    def build(
        cls,
        entity_name: str,
        unique_property_name: str,
        properties_default: str,
        api_name: str,
        create_kls,
        read_kls,
        entity_create_kls,
        entity_search_kls,
        extra_props: dict = None,
        get_validators=None,
        property_types=None,
        property_required=tuple(),
        assoc_adapter=None,
        field_props=None,
    ):
        class HubspotEntityCreate(HubspotBase):
            ENTITY_NAME_TITLE = entity_name.title()
            CREATE_BASE_KLS = create_kls
            READ_BASE_KLS = read_kls
            PROPERTY_TYPES = property_types or {}
            PROPERTY_REQUIRED = property_required
            FIELD_PROPS = field_props or {}

            @classmethod
            def get_validators(cls, properties):
                return get_validators(properties) if get_validators else None

            class InitSchema(Node.InitSchema):
                __doc__ = f"""
Creates a HubSpot {entity_name.title()}.

This block requires you to connect your HubSpot account to Plurally.
                """
                properties: str = Field(
                    properties_default,
                    title="Properties",
                    description="The properties to assign (comma separated).",
                    json_schema_extra={
                        "uiSchema": {
                            "ui:widget": "textarea",
                            "ui:placeholder": f"Comma separated properties, for example: {properties_default}",
                        }
                    },
                )

                update_if_exists: bool = Field(
                    True,
                    title="Update if Exists",
                    description=f"If a {entity_name} with the same {unique_property_name} exists, update it.",
                    json_schema_extra={"advanced": True},
                )

                @field_validator("properties")
                def validate_properties(cls, v):
                    return validate_properties_generic(v, property_required)

            DESC = InitSchema.__doc__

            InputSchema = create_model(
                f"{ENTITY_NAME_TITLE}Input",
                **{
                    entity_name: (
                        CREATE_BASE_KLS,
                        Field(
                            ...,
                            title=f"Hubspot {ENTITY_NAME_TITLE}",
                            description=f"The {entity_name} to create or update.",
                            json_schema_extra={
                                "type-friendly": f"Hubspot {ENTITY_NAME_TITLE}",
                                "jit": True,
                            },
                        ),
                    ),
                    **(extra_props or {}),
                },
                __base__=Node.InputSchema,
            )

            OutputSchema = create_model(
                f"{ENTITY_NAME_TITLE}Input",
                **{
                    entity_name: (
                        READ_BASE_KLS,
                        Field(
                            ...,
                            title=f"Hubspot {ENTITY_NAME_TITLE}",
                            description=f"The {entity_name} that was created or updated.",
                            json_schema_extra={
                                "type-friendly": f"Hubspot {ENTITY_NAME_TITLE}",
                                "jit": True,
                            },
                        ),
                    )
                },
                __base__=Node.OutputSchema,
            )

            def __init__(self, init_inputs: Node.InitSchema):
                self._properties = init_inputs.properties
                self.update_if_exists = init_inputs.update_if_exists
                self.entity_name = entity_name
                super().__init__(init_inputs)

            @property
            def adapters(self):
                return super().adapters | ({entity_name: {Association: assoc_adapter}} if assoc_adapter else {})

            @property
            def properties(self):
                return self._properties

            @properties.setter
            def properties(self, value):
                self._properties = value
                self._set_schemas()

            @classmethod
            def get_property_type(cls, property_annot):
                return Union[property_annot, None]

            @classmethod
            def get_entity_model(cls, properties, __base__, extra_props=None):
                entity = create_model(
                    f"Hubspot{cls.ENTITY_NAME_TITLE}",
                    **{
                        prop: (
                            cls.get_property_type(
                                cls.PROPERTY_TYPES.get(prop, str),
                            ),
                            Field(
                                None,
                                title=cls.FIELD_PROPS.get(prop, {}).get("title", prop),
                                description=cls.FIELD_PROPS.get(prop, {}).get("description"),
                            ),
                        )
                        for prop in [s.strip() for s in properties.split(",")]
                    },
                    **(extra_props or {}),
                    __base__=__base__,
                    __validators__=cls.get_validators(properties),
                )
                return entity

            def _get_input_props(self):
                EntityModel = self.get_entity_model(self.properties, self.CREATE_BASE_KLS)
                return {
                    entity_name: (
                        EntityModel,
                        Field(..., title=f"Hubspot {self.ENTITY_NAME_TITLE}"),
                    ),
                    **(extra_props or {}),
                }

            def _get_output_props(self):
                EntityModel = self.get_entity_model(self.properties, self.READ_BASE_KLS)
                return {
                    self.entity_name: (
                        EntityModel,
                        Field(..., title=f"Hubspot {self.ENTITY_NAME_TITLE}"),
                    )
                }

            def _set_schemas(self):
                self.InputSchema = create_model(
                    f"{self.ENTITY_NAME_TITLE}Input",
                    **self._get_input_props(),
                    __base__=Node.InputSchema,
                )
                self.OutputSchema = create_model(
                    f"{self.ENTITY_NAME_TITLE}Output",
                    **self._get_output_props(),
                    __base__=Node.OutputSchema,
                )

            def serialize(self):
                return super().serialize() | {
                    "properties": self._properties,
                    "update_if_exists": self.update_if_exists,
                }

            @property
            def basic_api(self):
                return self.basic_api_service(self.service)

            @classmethod
            def get_existing(cls, service, unique_property_value):
                q = entity_search_kls(
                    properties=[unique_property_name],
                    filter_groups=[
                        {
                            "filters": [
                                {
                                    "propertyName": unique_property_name,
                                    "operator": "EQ",
                                    "value": unique_property_value,
                                }
                            ]
                        }
                    ],
                    limit=1,
                )
                search_results = service.crm.objects.search_api.do_search(object_type=api_name, public_object_search_request=q)
                if search_results.total > 0:
                    return search_results.results[0]

            @classmethod
            def create_entity(cls, service, create_data):
                entity = service.crm.objects.basic_api.create(
                    object_type=api_name,
                    simple_public_object_input_for_create=create_data,
                )
                logger.debug(f"Created {entity_name} with id={entity.id}")

                return entity

            @classmethod
            def create_or_update_entity(
                cls,
                service,
                input_entity,
                associations=None,
                update_if_exists=False,
                required_properties=None,
            ):
                unique_property_value = getattr(input_entity, unique_property_name)
                if not unique_property_value:
                    logger.debug("No unique property value provided, early returning.")
                    return None, False, None, None
                is_update = False
                entity = cls.get_existing(service, unique_property_value)
                input_entity_data = input_entity.model_dump(exclude_none=True)
                previous_state = new_state = None

                if entity:
                    logger.debug(f"{entity_name} already exists.")
                    if update_if_exists is True:
                        logger.debug(f"Updating {entity_name} with id={entity.id}")
                        create_data = entity_create_kls(properties=input_entity_data)

                        previous_state = {k: entity.properties.get(k) for k in input_entity_data}
                        keys = [k for k in input_entity_data.keys() if previous_state.get(k) != input_entity_data.get(k)]

                        entity = service.crm.objects.basic_api.update(
                            object_id=entity.id,
                            object_type=api_name,
                            simple_public_object_input=create_data,
                        )
                        new_state = {k: entity.properties.get(k) for k in keys}

                        is_update = True
                        if associations:
                            cls.associate(service, int(entity.id), associations)
                            entity = cls.get_existing(service, unique_property_value)
                    elif update_if_exists == "make_unique":
                        logger.debug(f"Making {entity_name} unique.")
                        # make unique property value unique
                        setattr(
                            input_entity,
                            unique_property_name,
                            f"{unique_property_value} {str(uuid.uuid4())[:4]}",
                        )
                        return cls.create_or_update_entity(
                            service,
                            input_entity,
                            associations,
                            update_if_exists,
                        )
                    else:
                        logger.debug("Skipping update.")
                else:
                    for req_prop in required_properties or []:
                        if not input_entity_data.get(req_prop):
                            logger.debug(f"Missing required property {req_prop} - skipping creation.")
                            return None, False, None, None
                    create_data = entity_create_kls(properties=input_entity_data)
                    entity = cls.create_entity(service, create_data)
                    new_state = {k: entity.properties.get(k) for k in input_entity_data}
                    if associations:
                        cls.associate(service, int(entity.id), associations)
                return entity, is_update, previous_state, new_state

            @classmethod
            def create_or_update(
                cls,
                service,
                input_entity,
                associations,
                update_if_exists,
                output_schema_kls,
            ):
                entity, *_ = cls.create_or_update_entity(
                    service,
                    input_entity,
                    associations,
                    update_if_exists,
                )
                return output_schema_kls(**{entity_name: {**{"id": entity.id}, **entity.properties}}).model_dump()

            @tenacity.retry(
                wait=tenacity.wait_fixed(5),
                stop=tenacity.stop_after_attempt(3),
            )
            def forward(self, node_inputs):
                entity = getattr(node_inputs, self.entity_name)
                self.outputs = self.create_or_update(
                    self.service,
                    entity,
                    node_inputs.associations,
                    self.update_if_exists,
                    self.OutputSchema,
                )

            @classmethod
            def associate(cls, service, entity_id, associations):
                # associations is a unique assoc for not
                # later might be a list, need to see
                # then the next line should be changed
                for association in [associations]:
                    # check if assoc exists
                    existing_assocs = service.crm.associations.v4.basic_api.get_page(
                        association.from_oject_type,
                        entity_id,
                        association.to_object_type,
                    )

                    if any(existing_assoc.to_object_id == association.to.id for existing_assoc in existing_assocs.results):
                        # assoc already exists, do nothing
                        logger.debug("Association already exists, skipping.")
                    else:
                        for existing_assoc in existing_assocs.results:
                            service.crm.associations.v4.basic_api.archive(
                                association.from_oject_type,
                                entity_id,
                                association.to_object_type,
                                existing_assoc.to_object_id,
                            )

                        args = [
                            association.from_oject_type,
                            entity_id,
                            association.to_object_type,
                            association.to.id,
                            [
                                AssociationSpec(
                                    association.types[0].associationCategory,
                                    association.types[0].associationTypeId,
                                )
                            ],
                        ]
                        logger.debug(f"Associating with {associations}")
                        return service.crm.associations.v4.basic_api.create(*args)

            def _get_cls_props(self):
                return {}

        return HubspotEntityCreate
