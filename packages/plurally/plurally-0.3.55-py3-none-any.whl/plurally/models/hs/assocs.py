from typing import List

from pydantic import BaseModel, Field


class AssociationTo(BaseModel):
    id: str


class AssociationTypes(BaseModel):
    associationTypeId: int = Field()
    associationCategory: str = Field("HUBSPOT_DEFINED")


class Association(BaseModel):
    to: AssociationTo
    types: List[AssociationTypes]
    from_oject_type: str = Field(exclude=True)
    to_object_type: str = Field(exclude=True)


class ContactToCompany(Association):
    types: List[AssociationTypes] = [AssociationTypes(associationTypeId=279)]
    from_oject_type: str = "contact"
    to_object_type: str = "company"


class ContactToCall(Association):
    types: List[AssociationTypes] = [AssociationTypes(associationTypeId=193)]
    from_oject_type: str = "contact"
    to_object_type: str = "call"


class CallToContact(Association):
    types: List[AssociationTypes] = [AssociationTypes(associationTypeId=194)]
    from_oject_type: str = "call"
    to_object_type: str = "contact"


class DealToCompany(Association):
    types: List[AssociationTypes] = [AssociationTypes(associationTypeId=5)]
    from_oject_type: str = "deal"
    to_object_type: str = "company"


class TaskToContact(Association):
    types: List[AssociationTypes] = [AssociationTypes(associationTypeId=204)]
    from_oject_type: str = "task"
    to_object_type: str = "contact"
