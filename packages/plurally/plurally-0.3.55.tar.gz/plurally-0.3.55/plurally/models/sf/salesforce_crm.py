import enum
import os
import uuid
from collections import defaultdict
from copy import deepcopy
from datetime import datetime, timezone
from typing import Any, List, Literal, Optional, Type

from loguru import logger
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    computed_field,
    create_model,
    field_validator,
    model_validator,
)
from simple_salesforce.exceptions import SalesforceMalformedRequest
from tenacity import RetryError

from plurally.json_utils import replace_refs
from plurally.localization.translations.tl import _
from plurally.models import utils
from plurally.models.auto import Auto
from plurally.models.crm.actions import CrmAction, CrmActionType
from plurally.models.node import CommitMode, Node
from plurally.models.sf import salesforce_industries
from plurally.models.sf import task as sf_task
from plurally.models.sf.base import (
    DEFAULT_ACCOUNT_PROPERTIES,
    DEFAULT_CONTACT_PROPERTIES,
    DEFAULT_EVENT_PROPERTIES,
    DEFAULT_LEAD_PROPERTIES,
    DEFAULT_POULALLIER_PROPERTIES,
    REQUIRED_ACCOUNT_PROPERTIES,
    REQUIRED_CONTACT_PROPERTIES,
    REQUIRED_EVENT_PROPERTIES,
    REQUIRED_LEAD_PROPERTIES,
    ActionType,
    SalesforceAutoEntity,
    SalesforceBase,
    SalesforceEntityCreateBuilder,
    SalesforceModelBase,
    SalesforceObjectType,
    salesforce_json_encode,
)
from plurally.models.sf.opportunity import (
    DEFAULT_OPPORTUNITY_PROPERTIES,
    OPPORTUNITY_PROPERTY_DEFAULTS,
    OPPORTUNITY_PROPERTY_TYPES,
    REQUIRED_OPPORTUNITY_PROPERTIES,
)
from plurally.models.sf.soql import SalesforceSOQLFilter


def get_localization_key(s_object_type, key=None):
    if key is None:
        return f"Salesforce.{s_object_type}"
    return f"Salesforce.{s_object_type}.{key}"


DEFAULT_PROPERTIES = {
    SalesforceObjectType.ACCOUNT: DEFAULT_ACCOUNT_PROPERTIES,
    SalesforceObjectType.CONTACT: DEFAULT_CONTACT_PROPERTIES,
    SalesforceObjectType.EVENT: DEFAULT_EVENT_PROPERTIES,
    SalesforceObjectType.LEAD: DEFAULT_LEAD_PROPERTIES,
    SalesforceObjectType.OPPORTUNITY: DEFAULT_OPPORTUNITY_PROPERTIES,
    SalesforceObjectType.TASK: sf_task.DEFAULT_PROPERTIES,
    SalesforceObjectType.POULALLIER: DEFAULT_POULALLIER_PROPERTIES,
}

SALESFORCE_ICONS = {
    SalesforceObjectType.ACCOUNT.value: "https://tryplurally.com/salesforce/account.png",
    SalesforceObjectType.CONTACT.value: "https://tryplurally.com/salesforce/contact.png",
    SalesforceObjectType.EVENT.value: "https://tryplurally.com/salesforce/event.png",
    SalesforceObjectType.OPPORTUNITY.value: "https://tryplurally.com/salesforce/opportunity.png",
    SalesforceObjectType.TASK.value: "https://tryplurally.com/salesforce/task.png",
    SalesforceObjectType.LEAD.value: "https://tryplurally.com/salesforce/lead.png",
    SalesforceObjectType.EVENT.value: "https://tryplurally.com/salesforce/event.png",
    SalesforceObjectType.EVENT_RELATION.value: "https://tryplurally.com/salesforce/event.png",
    "OpportunityContactRole": "https://tryplurally.com/salesforce/opportunity_contact_role.png",
    "Relationship": "https://tryplurally.com/salesforce/relationship.png",
}


def validate_industry(v):
    v = salesforce_industries.to_enum_value_case(v)
    if v not in salesforce_industries.INDUSTRIES:
        return None
    return v


def validate_website(v):
    return utils.get_normalized_domain_from_url(v)


def validate_account_model(data):
    data["Name"] = data.get("Name", data.get("Website"))
    return data


def get_account_validators(properties):
    validators = {}
    if "Industry" in properties:
        # make sure it has a different name than the property
        validators["validate_industry"] = field_validator("Industry")(validate_industry)
    if "Website" in properties:
        validators["validate_website"] = field_validator("Website")(validate_website)

    validators["model_validator"] = model_validator(mode="before")(validate_account_model)
    return validators


def get_contact_validators(properties):
    validators = {}
    if "FirstName" in properties:
        validators["validate_firstname"] = field_validator("FirstName")(utils.validate_name)
    if "LastName" in properties:
        validators["validate_lastname"] = field_validator("LastName")(utils.validate_name)
    return validators


def get_lead_validators(properties):
    validators = {}
    if "FirstName" in properties:
        validators["validate_firstname"] = field_validator("FirstName")(utils.validate_name)
    if "LastName" in properties:
        validators["validate_lastname"] = field_validator("LastName")(utils.validate_name)
    return validators


class SalesforceEventCreateModel(SalesforceModelBase): ...


class SalesforceEventReadModel(SalesforceModelBase):
    Id: str


class SalesforceContactCreateModel(SalesforceModelBase): ...


class SalesforceContactReadModel(SalesforceModelBase):
    Id: str


class SalesforceOpportunityCreateModel(SalesforceModelBase): ...


class SalesforceOpportunityReadModel(SalesforceModelBase):
    Id: str


class SalesforceAccountCreateModel(SalesforceModelBase): ...


class SalesforceAccountReadModel(SalesforceModelBase):
    Id: str


class SalesforceLeadCreateModel(SalesforceModelBase): ...


class SalesforceLeadReadModel(SalesforceModelBase):
    Id: str


class SalesforceContactToAccountUnique(BaseModel):
    contact_email: str
    account_website: str

    @field_validator("account_website")
    def validate_account_website(cls, v):
        return validate_website(v)


class SalesforceEventToOpportunityUnique(BaseModel):
    opportunity_name: str
    event_subject: str


_SalesforceEventCreate = SalesforceEntityCreateBuilder.build(
    "event",
    "Subject",
    DEFAULT_EVENT_PROPERTIES,
    "Event",
    SalesforceEventCreateModel,
    SalesforceEventReadModel,
    property_required=REQUIRED_EVENT_PROPERTIES,
    property_types={"DurationInMinutes": int},
    property_defaults={
        "DurationInMinutes": lambda: 60,
        "StartDateTime": lambda: datetime.now(timezone.utc),
    },
)


class SalesforceEventCreate(_SalesforceEventCreate):
    pass


_SalesforceContactCreate = SalesforceEntityCreateBuilder.build(
    "contact",
    "Email",
    DEFAULT_CONTACT_PROPERTIES,
    "Contact",
    SalesforceContactCreateModel,
    SalesforceContactReadModel,
    property_required=REQUIRED_CONTACT_PROPERTIES,
    # assoc_adapter=get_entity_to_assoc("Contact"),
)


class SalesforceContactCreate(_SalesforceContactCreate):
    pass


_SalesforceOpportunityCreate = SalesforceEntityCreateBuilder.build(
    "opportunity",
    "Name",
    DEFAULT_OPPORTUNITY_PROPERTIES,
    "Opportunity",
    SalesforceOpportunityCreateModel,
    SalesforceOpportunityReadModel,
    property_required=REQUIRED_OPPORTUNITY_PROPERTIES,
    property_types=OPPORTUNITY_PROPERTY_TYPES,
    property_defaults=OPPORTUNITY_PROPERTY_DEFAULTS,
)


class SalesforceOpportunityCreate(_SalesforceOpportunityCreate):
    pass


_SalesforceAccountCreate = SalesforceEntityCreateBuilder.build(
    "account",
    "Website",
    DEFAULT_ACCOUNT_PROPERTIES,
    "Account",
    SalesforceAccountCreateModel,
    SalesforceAccountReadModel,
    property_required=REQUIRED_ACCOUNT_PROPERTIES,
)


class SalesforceAccountCreate(_SalesforceAccountCreate):
    pass


_SalesforceLeadCreate = SalesforceEntityCreateBuilder.build(
    "lead",
    "Email",
    DEFAULT_LEAD_PROPERTIES,
    "Lead",
    SalesforceLeadCreateModel,
    SalesforceLeadReadModel,
    property_required=REQUIRED_LEAD_PROPERTIES,
)


class SalesforceLeadCreate(_SalesforceLeadCreate):
    pass


def get_dummy_id():
    return uuid.uuid4().hex[:8]


def validate_no_none(entries):
    # hack to make sure that None values are replaced by defaults
    for ix, entry in enumerate(entries):
        entries[ix] = type(entry)(**entry.model_dump(exclude_none=True))
    return entries


class SalesforceUpdateIfExists(enum.Enum):
    MAKE_UNIQUE = "make_unique"
    UPDATE = "update"
    NO_UPDATE = "no_update"


s_object_type_one_of = []
for s_object_type in list(SalesforceObjectType):
    default_properties = DEFAULT_PROPERTIES.get(s_object_type, "")
    s_object_type_one_of.append(
        {
            "properties": {
                "s_object_type": {"const": s_object_type.value},
                f"{s_object_type.value}_properties": {
                    "title": "Fields",
                    "default": default_properties,
                    "type": "string",
                },
            },
            "required": ["s_object_type", f"{s_object_type.value}_properties"],
        }
    )


class SalesforceObjectToRead(BaseModel):
    model_config = ConfigDict(
        use_enum_values=True,
        json_schema_extra={"dependencies": {"s_object_type": {"oneOf": s_object_type_one_of}}},
    )
    record_type: str = Field(
        "",
        title="Record Type",
        json_schema_extra={"uiSchema": {"ui:widget": "text", "ui:emptyValue": ""}},
    )
    s_object_type: SalesforceObjectType = Field(SalesforceObjectType.ACCOUNT.value)

    # we do not want this in UI Form, it's handled with the dependencies
    # but we need it for programmatic instantiation
    # therefore we hide it (computed field won't cut it)
    properties: str | None = Field(
        None,
        title="Properties",
        description="The properties to sync.",
        # min_length=1,
        json_schema_extra={"uiSchema": {"ui:widget": "hidden"}},
    )

    @computed_field(return_type=List[str])
    def properties_list(self):
        return [s.strip() for s in self.properties.strip(",").split(",")]

    @field_validator("properties", mode="after")
    def validate_properties(cls, v):
        assert len(v.split(",")) > 0, "At least one field is required"
        return v

    @model_validator(mode="before")
    @classmethod
    def validate_model(cls, data):
        selected_obj_type = SalesforceObjectType(data["s_object_type"])
        # we must override here - as if the user selects a different to_object_type
        # the properties will be set to an invalid value
        key = f"{selected_obj_type.value}_properties"
        if key in data:
            # override
            data["properties"] = data[key]
        # we keep properties only if not specific key is present
        # as this means that it was parsed from serialization (specific keys are not serialized)
        if "properties" not in data:
            # data["properties"] = ""
            # return data
            raise ValueError(f"Could not find generic or specific key for properties in {data}")
        return data


# start of weird stuff

# this allows to have properties for each possible object type
# like Account_properties, Contact_properties, etc.
# this is necessary for prefilling intial values in the UI (according to the dependences described in the schema)
per_obj_type_props = {}
for s_object_type in list(SalesforceObjectType):

    def create_getter(s_object_type):
        def getter(self):
            return (
                self.properties if SalesforceObjectType(self.s_object_type) == s_object_type else DEFAULT_PROPERTIES.get(s_object_type, "")
            )

        return getter

    per_obj_type_props[f"{s_object_type.value}_properties"] = computed_field(return_type=str)(create_getter(s_object_type))

SalesforceObjectToRead = create_model(SalesforceObjectToRead.__name__, __base__=SalesforceObjectToRead, **per_obj_type_props)

#### end of weird stuff


class SalesforceReadAutoEntity(Node.OutputSchema):
    model_config = ConfigDict(use_enum_values=True, json_schema_extra={"uiSchema": {"ui:field": "SalesforceQuery"}})


class SalesforceReadAuto(SalesforceBase):
    class InitSchema(SalesforceBase.InitSchema):
        __doc__ = """Will read data from your Salesforce account."""
        model_config = ConfigDict(use_enum_values=True)
        objects_to_read: List[SalesforceObjectToRead] = Field(
            [
                SalesforceObjectToRead(
                    s_object_type=SalesforceObjectType.ACCOUNT.value,
                    properties=DEFAULT_ACCOUNT_PROPERTIES,
                ),
            ],
            description="The different Salesforce entites to read.",
            json_schema_extra={
                "name_singular": "Object to Read",
                "uiSchema": {
                    "items": {
                        "ui:label": False,
                        "ui:grid": [
                            ("s_object_type", 6),
                            ("record_type", 6),
                            *[(f"{o.value}_properties", 12) for o in SalesforceObjectType],
                        ],
                    },
                },
                "uniqueItems": True,
            },
        )
        skip_if_no_filter: bool = Field(
            True,
            title="Skip if no filter",
            description="If no filter is provided, skip reading the entity.",
            json_schema_extra={"advanced": True},
        )

    DESC = InitSchema.__doc__

    class InputSchema(Node.InputSchema):
        model_config = ConfigDict(use_enum_values=True)

    class OutputSchema(Node.OutputSchema):
        model_config = ConfigDict(use_enum_values=True)

    def __init__(self, init_inputs: InitSchema):
        self._objects_to_read = init_inputs.objects_to_read
        self.skip_if_no_filter = init_inputs.skip_if_no_filter
        self._read_kls = {}
        super().__init__(init_inputs)

    def serialize(self):
        return super().serialize() | {
            "objects_to_read": [o if isinstance(o, dict) else o.model_dump() for o in self.objects_to_read],
            "input_schema": replace_refs(self.InputSchema.model_json_schema()),
            "output_schema": replace_refs(self.OutputSchema.model_json_schema()),
            "skip_if_no_filter": self.skip_if_no_filter,
        }

    @property
    def objects_to_read(self):
        return self._objects_to_read

    @objects_to_read.setter
    def objects_to_read(self, value):
        value = [SalesforceObjectToRead(**v) if isinstance(v, dict) else v for v in value]
        self._objects_to_read = value
        self._set_schemas()

    def _get_name_for_object_type(self, object_type):
        return object_type.record_type.lower() if object_type.record_type else object_type.s_object_type.lower()

    def _get_key_for_objet_type(self, object_type):
        if object_type.record_type:
            return f"{object_type.record_type.lower()}_records"
        return f"{object_type.s_object_type.lower()}_records"

    def _set_input_schema(self):
        # allow selects for input
        selects = {}
        for object_type in self.objects_to_read:
            key = self._get_key_for_objet_type(object_type)
            desc = f"Selects for {object_type.s_object_type}"
            if object_type.record_type:
                desc += f"(Record type = {object_type.record_type})"
            selects[key] = (SalesforceSOQLFilter | None, Field(None, description=desc))
        self.InputSchema = create_model(
            "SalesforceAutoInput", __base__=Node.InputSchema, __doc__="Selects for the Salesforce entities.", **selects
        )

    def _set_schemas(self):
        self._set_input_schema()

        entities = {}
        for object_type in self.objects_to_read:
            if self.is_resolved:
                read_kls = self.get_record_type_read_kls(
                    object_type.s_object_type,
                    object_type.record_type,
                    object_type.properties_list,
                )
                self._read_kls[(object_type.s_object_type, object_type.record_type)] = read_kls
            else:
                read_kls = Auto
            name = self._get_name_for_object_type(object_type)
            entities[f"{name}_records"] = (List[read_kls], Field([]))

        self.OutputSchema = create_model(
            "OutputSchema",
            **entities,
            __base__=SalesforceReadAutoEntity,
        )

    @classmethod
    def query_all_s(
        cls,
        service,
        s_object_type: str,
        out_model_kls: Type[BaseModel],
        record_type: str | None = None,
        obj_filter: SalesforceSOQLFilter | None = None,
        limit: int = 100,
    ):
        cols = ",".join(out_model_kls.model_fields)
        if record_type:
            rtype_id = cls.get_record_type_id_s(service, s_object_type, record_type)
            where_clause = f"RecordTypeId='{rtype_id}'"
        else:
            where_clause = ""

        if obj_filter:
            if where_clause:
                where_clause += f" AND ({obj_filter})"
            else:
                where_clause = str(obj_filter)

        q = f"SELECT {cols} FROM {s_object_type}{' WHERE ' + where_clause if where_clause else ''} LIMIT {limit}"
        res = service.query_all(q)

        return [out_model_kls(**rec) for rec in res["records"]]

    def get_multi(
        self,
        s_object_type: str,
        record_type: str,
        out_model_kls: Type[BaseModel],
        obj_filter: SalesforceSOQLFilter | None = None,
        limit: int = 100,
    ) -> Optional[dict]:
        return self.query_all_s(self.service, s_object_type, out_model_kls, record_type, obj_filter, limit)

    def forward(self, node_input):
        out_entities = {}
        for obj_to_read in self.objects_to_read:
            obj_filter = getattr(node_input, self._get_key_for_objet_type(obj_to_read), None)

            logger.debug(f"Reading {obj_to_read.s_object_type} ({obj_to_read.record_type})")
            if obj_filter:
                logger.debug(f"Filter: {obj_filter}")
            elif self.skip_if_no_filter:
                logger.debug("No filter: skipping")
                continue

            read_model_kls = self._read_kls.get((obj_to_read.s_object_type, obj_to_read.record_type))
            obj_entities = self.get_multi(
                obj_to_read.s_object_type,
                obj_to_read.record_type,
                out_model_kls=read_model_kls,
                obj_filter=obj_filter,
            )
            name = self._get_name_for_object_type(obj_to_read)
            out_entities[f"{name}_records"] = obj_entities

        self.outputs = self.OutputSchema(**out_entities).model_dump()


class SalesforceObjectToSync(SalesforceObjectToRead):
    update_if_exists: SalesforceUpdateIfExists = SalesforceUpdateIfExists.NO_UPDATE.value


class SalesforceAuto(SalesforceBase):
    class InitSchema(SalesforceBase.InitSchema):
        __doc__ = """Will sync all the relevant data to your Salesforce account."""
        model_config = ConfigDict(use_enum_values=True)
        objects_to_sync: List[SalesforceObjectToSync] = Field(
            [
                SalesforceObjectToSync(
                    s_object_type=SalesforceObjectType.ACCOUNT.value,
                    update_if_exists=SalesforceUpdateIfExists.NO_UPDATE,
                    properties=DEFAULT_ACCOUNT_PROPERTIES,
                ),
                SalesforceObjectToSync(
                    s_object_type=SalesforceObjectType.CONTACT.value,
                    update_if_exists=SalesforceUpdateIfExists.NO_UPDATE,
                    properties=DEFAULT_CONTACT_PROPERTIES,
                ),
            ],
            title="Salesforce Records to sync",
            json_schema_extra={
                "name_singular": "Object to Sync",
                "uiSchema": {
                    "items": {
                        "ui:label": False,
                        "ui:grid": [
                            ("s_object_type", 4),
                            ("record_type", 4),
                            ("update_if_exists", 4),
                            *[(f"{o.value}_properties", 12) for o in SalesforceObjectType],
                        ],
                    },
                },
                "uniqueItems": True,
            },
        )

    DESC = InitSchema.__doc__

    class InputSchema(Node.InputSchema):
        model_config = ConfigDict(use_enum_values=True)
        input: SalesforceAutoEntity = Field(
            ...,
            title="Input",
            description="The different Salesforce entities to create or update.",
            json_schema_extra={"type-friendly": "Salesforce Auto Entity"},
        )

    class OutputSchemaBase(Node.OutputSchema):
        actions: List[CrmAction] = Field([])

    class OutputSchema(OutputSchemaBase): ...

    def __init__(self, init_inputs: InitSchema):
        self._objects_to_sync = init_inputs.objects_to_sync
        self._read_kls = {}
        super().__init__(init_inputs)

    @property
    def objects_to_sync(self):
        return self._objects_to_sync

    @objects_to_sync.setter
    def objects_to_sync(self, value):
        value = [SalesforceObjectToSync(**v) if isinstance(v, dict) else v for v in value]
        self._objects_to_sync = value
        self._set_schemas()

    def serialize(self):
        serialized = super().serialize() | {
            "objects_to_sync": [o if isinstance(o, dict) else o.model_dump() for o in self.objects_to_sync],
            "input_schema": replace_refs(self.InputSchema.model_json_schema()),
            "output_schema": replace_refs(self.OutputSchema.model_json_schema()),
        }

        return serialized

    @classmethod
    def get_entity_create_kls(cls, object_type):
        if object_type == SalesforceObjectType.LEAD:
            return SalesforceLeadCreate
        if object_type == SalesforceObjectType.ACCOUNT:
            return SalesforceAccountCreate
        if object_type == SalesforceObjectType.CONTACT:
            return SalesforceContactCreate
        if object_type == SalesforceObjectType.EVENT:
            return SalesforceEventCreate
        if object_type == SalesforceObjectType.OPPORTUNITY:
            return SalesforceOpportunityCreate
        raise ValueError(f"Unknown object type: {object_type}")

    def get_object_url(self, s_object_type: str, object_id: str):
        return f"https://{self.service.sf_instance}/lightning/r/{s_object_type}/{object_id}/view"

    def query_one_from_cols(
        self,
        s_object_type: str,
        unique_property_name,
        unique_property_value,
        cols: List[str] | str,
    ) -> Optional[dict]:
        if not isinstance(cols, str):
            cols = ",".join(cols)
        q = f"SELECT {cols} FROM {s_object_type} WHERE {unique_property_name}='{unique_property_value}' LIMIT 1"
        res = self.service.query_all(q)
        if res["totalSize"] > 0:
            return res["records"][0]
        return None

    def get_existing(
        self,
        s_object_type: str,
        unique_property_name,
        unique_property_value,
        model_kls,
    ):
        cols = ",".join(model_kls.model_fields)  # FIXME
        res = self.query_one_from_cols(s_object_type, unique_property_name, unique_property_value, cols)
        if res:
            return model_kls(**res)
        return None

    def create_entity(self, s_object_type: str, record_type: str | None, create_data, out_model_kls):
        create_data = deepcopy(create_data)
        if record_type:
            create_data["RecordTypeId"] = self.get_record_type_id_s(self.service, s_object_type, record_type)
        if self.is_commit:
            create_api = getattr(self.service, s_object_type)
            created_entity = create_api.create(salesforce_json_encode(create_data))
            return self.get_existing(s_object_type, "Id", created_entity["id"], out_model_kls)
        else:
            name_field = out_model_kls.model_config["json_schema_extra"].get("name_field")
            if name_field and not create_data.get(name_field):
                create_data[name_field] = ""
            return out_model_kls(**create_data, Id=get_dummy_id())

    def update_entity(self, s_object_type: str, entity_id, update_data, out_model_kls):
        existing = self.get_existing(s_object_type, "Id", entity_id, out_model_kls)
        previous_state = {k: getattr(existing, k) for k in update_data}

        if self.is_commit:
            update_api = getattr(self.service, s_object_type)
            update_api.update(entity_id, salesforce_json_encode(update_data))
            out_entity = self.get_existing(s_object_type, "Id", entity_id, out_model_kls)
        else:
            out_entity = out_model_kls(**update_data, Id=entity_id)

        # keys where they are different
        keys = [k for k in update_data if getattr(out_entity, k, None) != previous_state.get(k, None)]
        keys_locale = {k: (out_model_kls.model_fields[k].title if k in out_model_kls.model_fields else k) for k in keys}
        if keys:
            previous_state = {keys_locale[k]: previous_state[k] for k in keys}
            new_state = {keys_locale[k]: getattr(out_entity, k) for k in keys}
            action_type = ActionType.UPDATE
        else:
            out_entity = existing
            action_type = ActionType.NONE
            previous_state = None
            new_state = None

        logger.debug(f"Updated {s_object_type} with id={entity_id}")
        return out_entity, action_type, previous_state, new_state

    def create_or_update(
        self,
        s_object_type: str,
        record_type: str,
        input_entity: BaseModel,
        update_if_exists: SalesforceUpdateIfExists,
        out_model_kls: Type[BaseModel],
    ):
        input_entity_data = input_entity.model_dump(exclude_none=True)
        existing_entity_id = input_entity_data.pop("Id", None)

        action_type = ActionType.NONE
        new_state = previous_state = None

        if existing_entity_id:
            if update_if_exists == SalesforceUpdateIfExists.UPDATE.value:
                out_entity, action_type, previous_state, new_state = self.update_entity(
                    s_object_type, existing_entity_id, input_entity_data, out_model_kls
                )
            elif update_if_exists == SalesforceUpdateIfExists.MAKE_UNIQUE.value:
                logger.error("Not implemented make_unique")
                raise NotImplementedError()
            else:
                out_entity = self.get_existing(s_object_type, "Id", existing_entity_id, out_model_kls)
                action_type = ActionType.NONE
                logger.debug(f"Skipped updating {s_object_type} with id={existing_entity_id}")
        else:
            try:
                out_entity = self.create_entity(s_object_type, record_type, input_entity_data, out_model_kls)

                new_state = {out_model_kls.model_fields[k].title: getattr(out_entity, k) for k in input_entity_data}
                action_type = ActionType.CREATE

                logger.debug(f"Created {s_object_type} with id={out_entity.Id}")
            except (SalesforceMalformedRequest,) as e:
                content = e.content[0]
                if content["errorCode"] == "DUPLICATES_DETECTED":
                    duplicate_id = content["duplicateResult"]["matchResults"][0]["matchRecords"][0]["record"]["Id"]
                    logger.debug(f"Duplicate value for {s_object_type} (with Id={duplicate_id}).")
                    existing = self.get_existing(s_object_type, "Id", duplicate_id, out_model_kls)
                    if update_if_exists == SalesforceUpdateIfExists.NO_UPDATE.value:
                        out_entity = existing
                        action_type = ActionType.NONE
                        logger.debug(f"Skipped updating {s_object_type} with id={duplicate_id}")
                    elif update_if_exists == SalesforceUpdateIfExists.MAKE_UNIQUE.value:
                        logger.error("Not implemented make_unique")
                        raise NotImplementedError()
                    elif update_if_exists == SalesforceUpdateIfExists.UPDATE.value:
                        out_entity, action_type, previous_state, new_state = self.update_entity(
                            s_object_type,
                            duplicate_id,
                            input_entity_data,
                            out_model_kls,
                        )
                    else:
                        raise ValueError(f"Unknown update_if_exists: {update_if_exists}")
                else:
                    raise e
        return out_entity, action_type, previous_state, new_state

    def create_entities(
        self,
        s_object_type: str,
        record_type: str,
        entities: List[BaseModel],
        update_if_exists,
        out_model_kls,
    ):
        actions = []
        out_entities = []
        name_field = out_model_kls.model_config["json_schema_extra"]["name_field"]
        for entity in entities:
            out_entity, action_type, previous_state, new_state = self.create_or_update(
                s_object_type,
                record_type,
                entity,
                update_if_exists=update_if_exists,
                out_model_kls=out_model_kls,
            )
            if not out_entity:
                logger.debug(f"{s_object_type} not created")
                continue
            out_entities.append(out_entity)
            url = self.get_object_url(s_object_type, out_entity.Id)
            identifier = getattr(out_entity, name_field, None)
            if not identifier:
                logger.error(f"Could not find {name_field} in {out_entity}")
                identifier = out_entity.Id
            actions.append(
                CrmAction(
                    icon=SALESFORCE_ICONS[s_object_type],
                    object_type=type(out_entity).__name__,
                    identifier=identifier,
                    action_type=CrmActionType(
                        label=_(
                            {
                                ActionType.CREATE: "crm_action_create",
                                ActionType.UPDATE: "crm_action_update",
                                ActionType.NONE: "crm_action_none",
                            }[action_type]
                        ),
                        name=action_type.value.upper(),
                    ),
                    url=url,
                    previous_state=previous_state,
                    new_state=new_state,
                )
            )

        return actions, out_entities

    def forward(self, node_inputs: InputSchema):
        actions = []
        output_entities = defaultdict(dict)

        for obj_to_sync in self.objects_to_sync:
            name = obj_to_sync.record_type.lower() if obj_to_sync.record_type else obj_to_sync.s_object_type.lower()
            parent_key = f"{name}_records"
            entities = getattr(node_inputs, parent_key)
            read_model_kls = self._read_kls.get((obj_to_sync.s_object_type, obj_to_sync.record_type))
            logger.debug(f"Creating {len(entities)} {obj_to_sync.s_object_type} ({obj_to_sync.record_type})")
            obj_actions, obj_entities = self.create_entities(
                obj_to_sync.s_object_type,
                obj_to_sync.record_type,
                entities,
                obj_to_sync.update_if_exists,
                out_model_kls=read_model_kls,
            )
            output_entities[parent_key] = obj_entities
            actions.extend(obj_actions)

        self.outputs["actions"] = actions

        for k, v in output_entities.items():
            self.outputs[k] = [e.model_dump() for e in v]

    def _set_schemas(self):
        create_classes = {}
        read_classes = {}
        for object_type in self.objects_to_sync:
            if self.is_resolved:
                create_kls = self.get_record_type_create_kls(
                    object_type.s_object_type,
                    object_type.record_type,
                    properties=object_type.properties_list,
                )
                read_kls = self.get_record_type_read_kls(
                    object_type.s_object_type,
                    object_type.record_type,
                    properties=object_type.properties_list,
                )
            else:
                create_kls = SalesforceAutoEntity
                read_kls = SalesforceAutoEntity

            self._read_kls[(object_type.s_object_type, object_type.record_type)] = read_kls
            name = object_type.record_type.lower() if object_type.record_type else object_type.s_object_type.lower()
            read_classes[name] = read_kls
            create_classes[name] = create_kls

        create_classes_map = {f"{name}_records": (List[create_kls], Field([])) for name, create_kls in create_classes.items()}
        self.InputSchema = create_model(
            "SalesforceAutoInput",
            **create_classes_map,
            __validators__={
                "validate_no_none": field_validator(
                    *list(create_classes_map),
                    mode="after",
                )(validate_no_none)
            },
            __base__=SalesforceAutoEntity,
        )

        self.OutputSchema = create_model(
            "OutputSchema",
            **{f"{name}_records": (List[read_kls], Field([])) for name, read_kls in read_classes.items()},
            __base__=SalesforceAuto.OutputSchemaBase,
        )


class RelationshipType(enum.Enum):
    CONTACT_TO_ACCOUNT = "Contact to Account"
    EVENT_TO_OPPORTUNITY = "Event to Opportunity"
    EVENT_TO_CONTACT = "Event to Contact"
    EVENT_TO_ACCOUNT = "Event to Account"
    EVENT_TO_POULAILLER = "Event to Poulailler"
    OPPORTUNITY_TO_CONTACT = "Opportunity to Contact"
    OPPORTUNITY_TO_ACCOUNT = "Opportunity to Account"
    TASK_TO_OPPORTUNITY = "Task to Opportunity"
    # TASK_TO_ACCOUNT = "Task to Account"
    TASK_TO_CONTACT = "Task to Contact"


RELATIONSHIP_TYPE_TO_RECORD_TYPES = {
    RelationshipType.CONTACT_TO_ACCOUNT: (
        SalesforceObjectType.CONTACT,
        SalesforceObjectType.ACCOUNT,
    ),
    RelationshipType.EVENT_TO_OPPORTUNITY: (
        SalesforceObjectType.EVENT,
        SalesforceObjectType.OPPORTUNITY,
    ),
    RelationshipType.EVENT_TO_CONTACT: (
        SalesforceObjectType.EVENT,
        SalesforceObjectType.CONTACT,
    ),
    RelationshipType.EVENT_TO_ACCOUNT: (
        SalesforceObjectType.EVENT,
        SalesforceObjectType.ACCOUNT,
    ),
    RelationshipType.EVENT_TO_POULAILLER: (
        SalesforceObjectType.EVENT,
        SalesforceObjectType.POULALLIER,
    ),
    RelationshipType.OPPORTUNITY_TO_CONTACT: (
        SalesforceObjectType.OPPORTUNITY,
        SalesforceObjectType.CONTACT,
    ),
    RelationshipType.OPPORTUNITY_TO_ACCOUNT: (
        SalesforceObjectType.OPPORTUNITY,
        SalesforceObjectType.ACCOUNT,
    ),
    RelationshipType.TASK_TO_OPPORTUNITY: (
        SalesforceObjectType.TASK,
        SalesforceObjectType.OPPORTUNITY,
    ),
    # RelationshipType.TASK_TO_ACCOUNT: (
    #     SalesforceObjectType.TASK,
    #     SalesforceObjectType.ACCOUNT,
    # ),
    RelationshipType.TASK_TO_CONTACT: (
        SalesforceObjectType.TASK,
        SalesforceObjectType.CONTACT,
    ),
}

ALLOWED_ASSOCS = defaultdict(
    lambda: (None, None),
    {
        (SalesforceObjectType.CONTACT, SalesforceObjectType.ACCOUNT): (
            "AccountId",
            None,
        ),
        (SalesforceObjectType.EVENT, SalesforceObjectType.OPPORTUNITY): (
            "WhatId",
            None,
        ),
        (SalesforceObjectType.EVENT, SalesforceObjectType.POULALLIER): (
            "Poulailler__c",
            None,
        ),
        (SalesforceObjectType.EVENT, SalesforceObjectType.ACCOUNT): (
            "WhatId",
            None,
        ),
        (SalesforceObjectType.EVENT, SalesforceObjectType.CONTACT): (
            "WhoId",
            None,
        ),
        (SalesforceObjectType.OPPORTUNITY, SalesforceObjectType.CONTACT): (
            "ContactId",
            "OpportunityContactRole",
        ),
        (SalesforceObjectType.OPPORTUNITY, SalesforceObjectType.ACCOUNT): (
            "AccountId",
            None,
        ),
        (SalesforceObjectType.TASK, SalesforceObjectType.ACCOUNT): ("WhatId", None),
        (SalesforceObjectType.TASK, SalesforceObjectType.OPPORTUNITY): ("WhatId", None),
        (SalesforceObjectType.TASK, SalesforceObjectType.CONTACT): ("WhoId", None),
    },
)


def get_name_field_from_object_type(s_object_type):
    if s_object_type in (
        SalesforceObjectType.ACCOUNT,
        SalesforceObjectType.CONTACT,
        SalesforceObjectType.OPPORTUNITY,
        SalesforceObjectType.POULALLIER,
    ):
        return "Name"
    elif s_object_type == SalesforceObjectType.LEAD:
        return "Company"
    elif s_object_type in (SalesforceObjectType.EVENT, SalesforceObjectType.TASK):
        return "Subject"
    raise ValueError(f"Unknown name field for {s_object_type}")


def get_name_from_id(service, s_object_type, object_id):
    name_field = get_name_field_from_object_type(s_object_type)
    records = service.query(f"SELECT Name FROM {s_object_type.value} WHERE Id='{object_id}'")["records"]
    if records:
        return records[0][name_field]
    logger.error(f"Could not find Name for {s_object_type} with Id={object_id}")
    return object_id


class SalesforceAssociation(BaseModel):
    chain_of_thought: str = Field(
        ...,
        description="Think step by step to determine the correct Salesfore Ids, not other fields like Name, Email etc...",
    )
    relationship_type: RelationshipType = Field(..., description="The type of relationship (reference) between the two records.")
    record1_id: str = Field(description="The Salesforce ID of the first record.")
    record2_id: str = Field(description="The Salesforce ID of the second record.")


class SalesforceAssocAuto(SalesforceBase):
    class InitSchema(SalesforceBase.InitSchema):
        __doc__ = """Will associate the objects in your Salesforce account."""
        model_config = ConfigDict(use_enum_values=True)

    DESC = InitSchema.__doc__

    class InputSchema(Node.InputSchema):
        model_config = ConfigDict(use_enum_values=True)
        assoc_id_pairs: List[SalesforceAssociation] = Field(
            [],
            title="Salesforce Relationship Pairs",
            description="These are used to reference records together. E.g. Associate a Contact with an Account, through Contact's AccountId field (reference).",
            json_schema_extra={"type-friendly": "Salesforce Auto Entity"},
        )
        entities: List[Any] = Field(None)

    class OutputSchema(Node.OutputSchema):
        actions: List[CrmAction] = Field([])

    def associate_opportunity_contact_role(self, opportunity_id, contact_id):
        if self.is_commit:
            # check if there already is a primary contact
            x = self.service.query(
                f"SELECT ContactId, OpportunityId, IsPrimary from OpportunityContactRole WHERE OpportunityId='{opportunity_id}' AND IsPrimary=true"
            )
            if x["totalSize"] > 0:
                logger.debug(f"Primary contact already exists for {opportunity_id}")
                return
            logger.debug(f"Associating {contact_id} with {opportunity_id}")
            return self.service.OpportunityContactRole.create(
                {
                    "OpportunityId": opportunity_id,
                    "ContactId": contact_id,
                    "IsPrimary": True,
                }
            )
        else:
            return True

    def get_obj_name(self, entities, obj_type, obj_id):
        for entity in entities:
            if obj_id == entity.Id:
                return getattr(entity, get_name_field_from_object_type(obj_type))

        if self.is_commit:
            return get_name_from_id(self.service, obj_type, obj_id)
        return obj_id

    def associate(self, assoc_pair: SalesforceAssociation, entities: list):
        obj1_type, obj2_type = RELATIONSHIP_TYPE_TO_RECORD_TYPES[assoc_pair.relationship_type]

        obj1_id, obj2_id = assoc_pair.record1_id, assoc_pair.record2_id

        obj1_name = self.get_obj_name(entities, obj1_type, obj1_id)
        obj2_name = self.get_obj_name(entities, obj2_type, obj2_id)

        key, special = ALLOWED_ASSOCS[(obj1_type, obj2_type)]
        if not key:
            obj1_id, obj2_id = obj2_id, obj1_id
            obj1_type, obj2_type = obj2_type, obj1_type
            obj1_name, obj2_name = obj2_name, obj1_name

        key, special = ALLOWED_ASSOCS[(obj1_type, obj2_type)]
        if not key:
            logger.warning(f"Could not associate {obj1_id} and {obj2_id}")
            return None

        if special == "OpportunityContactRole":
            # can only be one IsPrimary contact for an opportunity
            assoc = self.associate_opportunity_contact_role(obj1_id, obj2_id)
            if assoc:
                return CrmAction(
                    icon=SALESFORCE_ICONS["Relationship"],
                    object_type=_("Salesforce.Relationship", os.environ.get("SALESFORCE_LOCALE")),
                    identifier=obj1_name,
                    action_type=CrmActionType(label=_("crm_action_associate"), name="ASSOCIATE"),
                    extra=_("crm_action_associate_extra").format(other=f"{obj2_name} ({obj2_type.value})"),
                )
            return None

        else:
            # check if exists
            if self.is_commit:
                existing = self.service.query(f"SELECT Id FROM {obj1_type.value} WHERE {key}='{obj2_id}' AND Id='{obj1_id}'")
                if existing["totalSize"] > 0:
                    logger.debug(f"Already associated {obj1_id} with {obj2_id}")
                    return None

                logger.debug(f"Associating {obj1_id} ({obj1_type.value}) with {obj2_id} ({obj2_type.value})")

                update_api = getattr(self.service, obj1_type.value)
                update_api.update(obj1_id, {key: obj2_id})

        obj2_type_label = obj2_type.value
        obj2 = [e for e in entities if e.Id == obj2_id]
        if obj2:
            obj2_type_label = type(obj2[0]).__name__

        return CrmAction(
            icon=SALESFORCE_ICONS["Relationship"],
            object_type=_("Salesforce.Relationship", os.environ.get("SALESFORCE_LOCALE")),
            identifier=obj1_name,
            action_type=CrmActionType(label=_("crm_action_associate"), name="ASSOCIATE"),
            extra=_("crm_action_associate_extra").format(other=f"{obj2_name} ({obj2_type_label})"),
        )

    def flatten_entities(self, entities):
        flat = []
        for entity in entities:
            if isinstance(entity, list):
                flat.extend(self.flatten_entities(entity))
            else:
                flat.append(entity)
        return flat

    def forward(self, node_inputs: InputSchema):
        entities = self.flatten_entities(node_inputs.entities)
        actions = []
        for assoc_pair in node_inputs.assoc_id_pairs:
            try:
                action = self.associate(assoc_pair, entities)
                if action:
                    actions.append(action)
            except Exception as e:
                logger.error(f"Could not associate {assoc_pair}")
                logger.exception(e)
        self.outputs["actions"] = actions


__all__ = ["SalesforceReadAuto", "SalesforceAuto", "SalesforceAssocAuto"]
