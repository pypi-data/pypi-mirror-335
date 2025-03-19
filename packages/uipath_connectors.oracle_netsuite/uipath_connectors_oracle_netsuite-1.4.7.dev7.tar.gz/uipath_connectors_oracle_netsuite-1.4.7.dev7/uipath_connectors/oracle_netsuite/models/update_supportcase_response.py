from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.update_supportcase_response_status import UpdateSupportcaseResponseStatus
from ..models.update_supportcase_response_company import (
    UpdateSupportcaseResponseCompany,
)
from ..models.update_supportcase_response_subsidiary import (
    UpdateSupportcaseResponseSubsidiary,
)
from ..models.update_supportcase_response_priority import (
    UpdateSupportcaseResponsePriority,
)


class UpdateSupportcaseResponse(BaseModel):
    """
    Attributes:
        company (Optional[UpdateSupportcaseResponseCompany]):
        internal_id (Optional[str]): Support case ID. Example: 517.
        phone (Optional[str]): The phone number of the contact for the case Example: +11234567890.
        priority (Optional[UpdateSupportcaseResponsePriority]):
        status (Optional[UpdateSupportcaseResponseStatus]):
        subsidiary (Optional[UpdateSupportcaseResponseSubsidiary]):
        title (Optional[str]): The subject of the support case Example: Test case.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    company: Optional["UpdateSupportcaseResponseCompany"] = Field(
        alias="company", default=None
    )
    internal_id: Optional[str] = Field(alias="internalId", default=None)
    phone: Optional[str] = Field(alias="phone", default=None)
    priority: Optional["UpdateSupportcaseResponsePriority"] = Field(
        alias="priority", default=None
    )
    status: Optional["UpdateSupportcaseResponseStatus"] = Field(
        alias="status", default=None
    )
    subsidiary: Optional["UpdateSupportcaseResponseSubsidiary"] = Field(
        alias="subsidiary", default=None
    )
    title: Optional[str] = Field(alias="title", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["UpdateSupportcaseResponse"], src_dict: Dict[str, Any]):
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
