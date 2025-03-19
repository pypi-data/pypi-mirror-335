from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type


class SearchCustomersAccessRoleType(BaseModel):
    """
    Attributes:
        value (Optional[str]): References a value in a user-defined list at Setup > Users/Roles > Manage Roles. This
                value sets the role assigned to this customer. In order to retrieve a list of available values for this field,
                use the GetSelectValue operation. For more information, see getSelectValue of the Platform Guide.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    value: Optional[str] = Field(alias="value", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["SearchCustomersAccessRoleType"], src_dict: Dict[str, Any]):
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
