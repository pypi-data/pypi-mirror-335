from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.search_items_accounting_book_detail_list_item_accounting_book_detail_accounting_book_type import (
    SearchItemsAccountingBookDetailListItemAccountingBookDetailAccountingBookType,
)


class SearchInventoryItemRecordRef(BaseModel):
    """
    Attributes:
        external_id (Optional[str]): In order to retrieve a list of available values for this field, use the
                GetSelectValue operation.
        internal_id (Optional[str]): In order to retrieve a list of available values for this field, use the
                GetSelectValue operation.
        name (Optional[str]): In order to retrieve a list of available values for this field, use the GetSelectValue
                operation.
        type_ (Optional[SearchItemsAccountingBookDetailListItemAccountingBookDetailAccountingBookType]):
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    external_id: Optional[str] = Field(alias="externalId", default=None)
    internal_id: Optional[str] = Field(alias="internalId", default=None)
    name: Optional[str] = Field(alias="name", default=None)
    type_: Optional[
        "SearchItemsAccountingBookDetailListItemAccountingBookDetailAccountingBookType"
    ] = Field(alias="type", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["SearchInventoryItemRecordRef"], src_dict: Dict[str, Any]):
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
