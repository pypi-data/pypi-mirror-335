from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.create_supportcase_response_contact import (
    CreateSupportcaseResponseContact,
)
from ..models.create_supportcase_response_subsidiary import (
    CreateSupportcaseResponseSubsidiary,
)
from ..models.create_supportcase_response_priority import (
    CreateSupportcaseResponsePriority,
)
from ..models.create_supportcase_response_category import (
    CreateSupportcaseResponseCategory,
)
from ..models.create_supportcase_response_origin import CreateSupportcaseResponseOrigin
from ..models.create_supportcase_response_company import (
    CreateSupportcaseResponseCompany,
)
from ..models.create_supportcase_response_status import CreateSupportcaseResponseStatus


class CreateSupportcaseResponse(BaseModel):
    """
    Attributes:
        case_number (Optional[str]): Case number Example: 38.
        category (Optional[CreateSupportcaseResponseCategory]):
        company (Optional[CreateSupportcaseResponseCompany]):
        contact (Optional[CreateSupportcaseResponseContact]):
        incoming_message (Optional[str]): The message that was added along with the case Example: Test.
        internal_id (Optional[str]): Support case ID. Example: 517.
        origin (Optional[CreateSupportcaseResponseOrigin]):
        phone (Optional[str]): The phone number of the contact for the case Example: +11234567890.
        priority (Optional[CreateSupportcaseResponsePriority]):
        status (Optional[CreateSupportcaseResponseStatus]):
        subsidiary (Optional[CreateSupportcaseResponseSubsidiary]):
        title (Optional[str]): The subject of the support case Example: Test case.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    case_number: Optional[str] = Field(alias="caseNumber", default=None)
    category: Optional["CreateSupportcaseResponseCategory"] = Field(
        alias="category", default=None
    )
    company: Optional["CreateSupportcaseResponseCompany"] = Field(
        alias="company", default=None
    )
    contact: Optional["CreateSupportcaseResponseContact"] = Field(
        alias="contact", default=None
    )
    incoming_message: Optional[str] = Field(alias="incomingMessage", default=None)
    internal_id: Optional[str] = Field(alias="internalId", default=None)
    origin: Optional["CreateSupportcaseResponseOrigin"] = Field(
        alias="origin", default=None
    )
    phone: Optional[str] = Field(alias="phone", default=None)
    priority: Optional["CreateSupportcaseResponsePriority"] = Field(
        alias="priority", default=None
    )
    status: Optional["CreateSupportcaseResponseStatus"] = Field(
        alias="status", default=None
    )
    subsidiary: Optional["CreateSupportcaseResponseSubsidiary"] = Field(
        alias="subsidiary", default=None
    )
    title: Optional[str] = Field(alias="title", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["CreateSupportcaseResponse"], src_dict: Dict[str, Any]):
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
