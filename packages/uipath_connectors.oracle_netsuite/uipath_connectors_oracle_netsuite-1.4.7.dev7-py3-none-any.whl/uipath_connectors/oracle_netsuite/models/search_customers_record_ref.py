from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.search_customers_access_role_type import SearchCustomersAccessRoleType


class SearchCustomersRecordRef(BaseModel):
    """
    Attributes:
        external_id (Optional[str]): References a value in a user-defined list at Setup > Sales > Sales Management >
                Sales Territories. This value sets the sales territory this customer belongs in. In order to retrieve a list of
                available values for this field, use the GetSelectValue operation. For more information, see getSelectValue of
                the Platform Guide.
        internal_id (Optional[str]): References a value in a user-defined list at Setup > Sales > Sales Management >
                Sales Territories. This value sets the sales territory this customer belongs in. In order to retrieve a list of
                available values for this field, use the GetSelectValue operation. For more information, see getSelectValue of
                the Platform Guide.
        name (Optional[str]): References a value in a user-defined list at Setup > Sales > Sales Management > Sales
                Territories. This value sets the sales territory this customer belongs in. In order to retrieve a list of
                available values for this field, use the GetSelectValue operation. For more information, see getSelectValue of
                the Platform Guide.
        type_ (Optional[SearchCustomersAccessRoleType]):
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    external_id: Optional[str] = Field(alias="externalId", default=None)
    internal_id: Optional[str] = Field(alias="internalId", default=None)
    name: Optional[str] = Field(alias="name", default=None)
    type_: Optional["SearchCustomersAccessRoleType"] = Field(alias="type", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["SearchCustomersRecordRef"], src_dict: Dict[str, Any]):
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
