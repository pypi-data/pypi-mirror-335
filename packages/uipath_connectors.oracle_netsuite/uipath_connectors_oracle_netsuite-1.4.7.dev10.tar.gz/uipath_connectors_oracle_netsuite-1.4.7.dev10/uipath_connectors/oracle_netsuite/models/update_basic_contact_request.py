from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.update_basic_contact_request_company import (
    UpdateBasicContactRequestCompany,
)
from ..models.update_basic_contact_request_subsidiary import (
    UpdateBasicContactRequestSubsidiary,
)


class UpdateBasicContactRequest(BaseModel):
    """
    Attributes:
        company (Optional[UpdateBasicContactRequestCompany]):
        email (Optional[str]): The email address of the contact Example: uipath@uipath.com.
        first_name (Optional[str]): The first name of the contact Example: John112.
        last_name (Optional[str]): The last name of the contact Example: Smith.
        middle_name (Optional[str]): The middle name of the contact Example: ab.
        phone (Optional[str]): The phone number of the contact Example: +19999999999.
        subsidiary (Optional[UpdateBasicContactRequestSubsidiary]):
        title (Optional[str]): The job title of the contact Example: contactTest.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    company: Optional["UpdateBasicContactRequestCompany"] = Field(
        alias="company", default=None
    )
    email: Optional[str] = Field(alias="email", default=None)
    first_name: Optional[str] = Field(alias="firstName", default=None)
    last_name: Optional[str] = Field(alias="lastName", default=None)
    middle_name: Optional[str] = Field(alias="middleName", default=None)
    phone: Optional[str] = Field(alias="phone", default=None)
    subsidiary: Optional["UpdateBasicContactRequestSubsidiary"] = Field(
        alias="subsidiary", default=None
    )
    title: Optional[str] = Field(alias="title", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["UpdateBasicContactRequest"], src_dict: Dict[str, Any]):
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
