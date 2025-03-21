from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.search_items_item_revenue_category_type import (
    SearchItemsItemRevenueCategoryType,
)


class SearchItemsItemRevenueCategory(BaseModel):
    """
    Attributes:
        external_id (Optional[str]): The item revenue category is a classification for items that have similar
                characteristics and revenue allocation requirements. It is used in the fair value price list.
        internal_id (Optional[str]): The item revenue category is a classification for items that have similar
                characteristics and revenue allocation requirements. It is used in the fair value price list.
        name (Optional[str]): The item revenue category is a classification for items that have similar characteristics
                and revenue allocation requirements. It is used in the fair value price list.
        type_ (Optional[SearchItemsItemRevenueCategoryType]):
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    external_id: Optional[str] = Field(alias="externalId", default=None)
    internal_id: Optional[str] = Field(alias="internalId", default=None)
    name: Optional[str] = Field(alias="name", default=None)
    type_: Optional["SearchItemsItemRevenueCategoryType"] = Field(
        alias="type", default=None
    )

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(
        cls: Type["SearchItemsItemRevenueCategory"], src_dict: Dict[str, Any]
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
