from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.update_supportcase_request_subsidiary import (
    UpdateSupportcaseRequestSubsidiary,
)
from ..models.update_supportcase_request_contact import UpdateSupportcaseRequestContact
from ..models.update_supportcase_request_company import UpdateSupportcaseRequestCompany
from ..models.update_supportcase_request_priority import (
    UpdateSupportcaseRequestPriority,
)
from ..models.update_supportcase_request_status import UpdateSupportcaseRequestStatus
from ..models.update_supportcase_request_category import (
    UpdateSupportcaseRequestCategory,
)


class UpdateSupportcaseRequest(BaseModel):
    """
    Attributes:
        category (Optional[UpdateSupportcaseRequestCategory]):
        company (Optional[UpdateSupportcaseRequestCompany]):
        contact (Optional[UpdateSupportcaseRequestContact]):
        email (Optional[str]): The email of contact who raised the support case. This field is required only during
                create if company or the associated contact does not have an email address Example: samar@yopmail.com.
        incoming_message (Optional[str]): The message that was added along with the case Example: Test.
        phone (Optional[str]): The phone number of the contact for the case Example: +11234567890.
        priority (Optional[UpdateSupportcaseRequestPriority]):
        status (Optional[UpdateSupportcaseRequestStatus]):
        subsidiary (Optional[UpdateSupportcaseRequestSubsidiary]):
        title (Optional[str]): The subject of the support case Example: Test case.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    category: Optional["UpdateSupportcaseRequestCategory"] = Field(
        alias="category", default=None
    )
    company: Optional["UpdateSupportcaseRequestCompany"] = Field(
        alias="company", default=None
    )
    contact: Optional["UpdateSupportcaseRequestContact"] = Field(
        alias="contact", default=None
    )
    email: Optional[str] = Field(alias="email", default=None)
    incoming_message: Optional[str] = Field(alias="incomingMessage", default=None)
    phone: Optional[str] = Field(alias="phone", default=None)
    priority: Optional["UpdateSupportcaseRequestPriority"] = Field(
        alias="priority", default=None
    )
    status: Optional["UpdateSupportcaseRequestStatus"] = Field(
        alias="status", default=None
    )
    subsidiary: Optional["UpdateSupportcaseRequestSubsidiary"] = Field(
        alias="subsidiary", default=None
    )
    title: Optional[str] = Field(alias="title", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["UpdateSupportcaseRequest"], src_dict: Dict[str, Any]):
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
