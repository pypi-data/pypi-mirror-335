from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

import datetime
from ..models.create_basic_contact_response_company import (
    CreateBasicContactResponseCompany,
)
from ..models.create_basic_contact_response_subsidiary import (
    CreateBasicContactResponseSubsidiary,
)


class CreateBasicContactResponse(BaseModel):
    """
    Attributes:
        company (Optional[CreateBasicContactResponseCompany]):
        date_created (Optional[datetime.datetime]):  Example: 2022-10-13T15:28:35.0000000+05:30.
        email (Optional[str]): The email address of the contact Example: uipath@uipath.com.
        entity_id (Optional[str]):  Example: John112 a Smith.
        first_name (Optional[str]): The first name of the contact Example: John112.
        internal_id (Optional[str]): Contact ID Example: 312592.
        is_inactive (Optional[bool]):
        last_name (Optional[str]): The last name of the contact Example: Smith.
        middle_name (Optional[str]): The middle name of the contact Example: ab.
        phone (Optional[str]): The phone number of the contact Example: +19999999999.
        subsidiary (Optional[CreateBasicContactResponseSubsidiary]):
        title (Optional[str]): The job title of the contact Example: contactTest.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    company: Optional["CreateBasicContactResponseCompany"] = Field(
        alias="company", default=None
    )
    date_created: Optional[datetime.datetime] = Field(alias="dateCreated", default=None)
    email: Optional[str] = Field(alias="email", default=None)
    entity_id: Optional[str] = Field(alias="entityId", default=None)
    first_name: Optional[str] = Field(alias="firstName", default=None)
    internal_id: Optional[str] = Field(alias="internalId", default=None)
    is_inactive: Optional[bool] = Field(alias="isInactive", default=None)
    last_name: Optional[str] = Field(alias="lastName", default=None)
    middle_name: Optional[str] = Field(alias="middleName", default=None)
    phone: Optional[str] = Field(alias="phone", default=None)
    subsidiary: Optional["CreateBasicContactResponseSubsidiary"] = Field(
        alias="subsidiary", default=None
    )
    title: Optional[str] = Field(alias="title", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["CreateBasicContactResponse"], src_dict: Dict[str, Any]):
        return cls.model_validate(src_dict)

    @property
    def additional_keys(self) -> list[str]:
        base_fields = self.model_fields.keys()
        return [k for k in self.__dict__ if k not in base_fields]

    def __getitem__(self, key: str) -> Any:
        if key in self.__dict__:
            return self.__dict__[key]
        raise KeyError(key)

    def __setitem__(self, key: str, value: Any) -> None:
        self.__dict__[key] = value

    def __delitem__(self, key: str) -> None:
        if key in self.__dict__:
            del self.__dict__[key]
        else:
            raise KeyError(key)

    def __contains__(self, key: str) -> bool:
        return key in self.__dict__
