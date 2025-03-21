from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.search_items_custom_form_type import SearchItemsCustomFormType


class SearchItemsCustomForm(BaseModel):
    """
    Attributes:
        external_id (Optional[str]): References an existing custom form for this record type. To ensure that field
                relationships defined within a desired custom form are maintained, you must provide the customForm value. Also,
                if defaults are off, then customForm is required, if defaults are on then the default form is used. Internal ID
                values for existing forms can be found at Setup > Customization > Entry Forms. In order to retrieve a list of
                available values for this field, use the GetSelectValue operation.
        internal_id (Optional[str]): References an existing custom form for this record type. To ensure that field
                relationships defined within a desired custom form are maintained, you must provide the customForm value. Also,
                if defaults are off, then customForm is required, if defaults are on then the default form is used. Internal ID
                values for existing forms can be found at Setup > Customization > Entry Forms. In order to retrieve a list of
                available values for this field, use the GetSelectValue operation.
        name (Optional[str]): References an existing custom form for this record type. To ensure that field
                relationships defined within a desired custom form are maintained, you must provide the customForm value. Also,
                if defaults are off, then customForm is required, if defaults are on then the default form is used. Internal ID
                values for existing forms can be found at Setup > Customization > Entry Forms. In order to retrieve a list of
                available values for this field, use the GetSelectValue operation.
        type_ (Optional[SearchItemsCustomFormType]):
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    external_id: Optional[str] = Field(alias="externalId", default=None)
    internal_id: Optional[str] = Field(alias="internalId", default=None)
    name: Optional[str] = Field(alias="name", default=None)
    type_: Optional["SearchItemsCustomFormType"] = Field(alias="type", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["SearchItemsCustomForm"], src_dict: Dict[str, Any]):
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
