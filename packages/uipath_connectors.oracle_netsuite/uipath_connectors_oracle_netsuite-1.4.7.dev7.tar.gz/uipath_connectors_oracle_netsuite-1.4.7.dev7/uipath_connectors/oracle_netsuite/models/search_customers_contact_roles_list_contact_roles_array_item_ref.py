from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.search_customers_record_ref import SearchCustomersRecordRef


class SearchCustomersContactRolesListContactRolesArrayItemRef(BaseModel):
    """
    Attributes:
        contact (Optional[SearchCustomersRecordRef]):
        email (Optional[str]):
        give_access (Optional[bool]):
        password (Optional[str]):
        password2 (Optional[str]):
        role (Optional[SearchCustomersRecordRef]):
        send_email (Optional[bool]):
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    contact: Optional["SearchCustomersRecordRef"] = Field(alias="contact", default=None)
    email: Optional[str] = Field(alias="email", default=None)
    give_access: Optional[bool] = Field(alias="giveAccess", default=None)
    password: Optional[str] = Field(alias="password", default=None)
    password2: Optional[str] = Field(alias="password2", default=None)
    role: Optional["SearchCustomersRecordRef"] = Field(alias="role", default=None)
    send_email: Optional[bool] = Field(alias="sendEmail", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(
        cls: Type["SearchCustomersContactRolesListContactRolesArrayItemRef"],
        src_dict: Dict[str, Any],
    ):
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
