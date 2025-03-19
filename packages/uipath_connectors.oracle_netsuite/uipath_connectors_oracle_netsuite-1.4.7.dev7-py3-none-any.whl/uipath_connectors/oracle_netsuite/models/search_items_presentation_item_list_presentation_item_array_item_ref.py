from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.search_inventory_item_record_ref import SearchInventoryItemRecordRef
from ..models.search_items_presentation_item_list_presentation_item_item_type import (
    SearchItemsPresentationItemListPresentationItemItemType,
)


class SearchItemsPresentationItemListPresentationItemArrayItemRef(BaseModel):
    """
    Attributes:
        base_price (Optional[float]):
        description (Optional[str]):
        item (Optional[SearchInventoryItemRecordRef]):
        item_type (Optional[SearchItemsPresentationItemListPresentationItemItemType]):
        online_price (Optional[float]):
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    base_price: Optional[float] = Field(alias="basePrice", default=None)
    description: Optional[str] = Field(alias="description", default=None)
    item: Optional["SearchInventoryItemRecordRef"] = Field(alias="item", default=None)
    item_type: Optional["SearchItemsPresentationItemListPresentationItemItemType"] = (
        Field(alias="itemType", default=None)
    )
    online_price: Optional[float] = Field(alias="onlinePrice", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(
        cls: Type["SearchItemsPresentationItemListPresentationItemArrayItemRef"],
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
