from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.create_supportcase_request_contact import CreateSupportcaseRequestContact
from ..models.create_supportcase_request_status import CreateSupportcaseRequestStatus
from ..models.create_supportcase_request_subsidiary import (
    CreateSupportcaseRequestSubsidiary,
)
from ..models.create_supportcase_request_company import CreateSupportcaseRequestCompany
from ..models.create_supportcase_request_origin import CreateSupportcaseRequestOrigin
from ..models.create_supportcase_request_category import (
    CreateSupportcaseRequestCategory,
)
from ..models.create_supportcase_request_priority import (
    CreateSupportcaseRequestPriority,
)


class CreateSupportcaseRequest(BaseModel):
    """
    Attributes:
        title (str): The subject of the support case Example: Test case.
        category (Optional[CreateSupportcaseRequestCategory]):
        company (Optional[CreateSupportcaseRequestCompany]):
        contact (Optional[CreateSupportcaseRequestContact]):
        email (Optional[str]): The email of contact who raised the support case. This field is required only during
                create if company or the associated contact does not have an email address Example: samar@yopmail.com.
        incoming_message (Optional[str]): The message that was added along with the case Example: Test.
        origin (Optional[CreateSupportcaseRequestOrigin]):
        phone (Optional[str]): The phone number of the contact for the case Example: +11234567890.
        priority (Optional[CreateSupportcaseRequestPriority]):
        status (Optional[CreateSupportcaseRequestStatus]):
        subsidiary (Optional[CreateSupportcaseRequestSubsidiary]):
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    title: str = Field(alias="title")
    category: Optional["CreateSupportcaseRequestCategory"] = Field(
        alias="category", default=None
    )
    company: Optional["CreateSupportcaseRequestCompany"] = Field(
        alias="company", default=None
    )
    contact: Optional["CreateSupportcaseRequestContact"] = Field(
        alias="contact", default=None
    )
    email: Optional[str] = Field(alias="email", default=None)
    incoming_message: Optional[str] = Field(alias="incomingMessage", default=None)
    origin: Optional["CreateSupportcaseRequestOrigin"] = Field(
        alias="origin", default=None
    )
    phone: Optional[str] = Field(alias="phone", default=None)
    priority: Optional["CreateSupportcaseRequestPriority"] = Field(
        alias="priority", default=None
    )
    status: Optional["CreateSupportcaseRequestStatus"] = Field(
        alias="status", default=None
    )
    subsidiary: Optional["CreateSupportcaseRequestSubsidiary"] = Field(
        alias="subsidiary", default=None
    )

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["CreateSupportcaseRequest"], src_dict: Dict[str, Any]):
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
