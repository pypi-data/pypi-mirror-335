from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.update_customer_response_contact_roles_list_contact_roles_contact import (
    UpdateCustomerResponseContactRolesListContactRolesContact,
)
from ..models.update_customer_response_contact_roles_list_contact_roles_role import (
    UpdateCustomerResponseContactRolesListContactRolesRole,
)


class UpdateCustomerResponseContactRolesListContactRolesArrayItemRef(BaseModel):
    """
    Attributes:
        contact (Optional[UpdateCustomerResponseContactRolesListContactRolesContact]):
        give_access (Optional[bool]): The Contact roles list contact roles give access
        role (Optional[UpdateCustomerResponseContactRolesListContactRolesRole]):
        send_email (Optional[bool]): The Contact roles list contact roles send email
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    contact: Optional["UpdateCustomerResponseContactRolesListContactRolesContact"] = (
        Field(alias="contact", default=None)
    )
    give_access: Optional[bool] = Field(alias="giveAccess", default=None)
    role: Optional["UpdateCustomerResponseContactRolesListContactRolesRole"] = Field(
        alias="role", default=None
    )
    send_email: Optional[bool] = Field(alias="sendEmail", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(
        cls: Type["UpdateCustomerResponseContactRolesListContactRolesArrayItemRef"],
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
