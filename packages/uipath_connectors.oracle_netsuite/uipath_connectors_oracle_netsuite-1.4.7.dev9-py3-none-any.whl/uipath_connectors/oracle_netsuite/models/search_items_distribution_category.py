from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.search_items_distribution_category_type import (
    SearchItemsDistributionCategoryType,
)


class SearchItemsDistributionCategory(BaseModel):
    """
    Attributes:
        external_id (Optional[str]): Choose the appropriate category. Once a distribution category is defined on the
                item record, NetSuite can incorporate network transfers into demand planning for the item.Note: The network and
                category you select must be associated with the subsidiary selected for the item in the Classifications section
                of the item record. For details about how categories are associated with subsidiaries, click Help and read
                Creating Distribution Categories.
        internal_id (Optional[str]): Choose the appropriate category. Once a distribution category is defined on the
                item record, NetSuite can incorporate network transfers into demand planning for the item.Note: The network and
                category you select must be associated with the subsidiary selected for the item in the Classifications section
                of the item record. For details about how categories are associated with subsidiaries, click Help and read
                Creating Distribution Categories.
        name (Optional[str]): Choose the appropriate category. Once a distribution category is defined on the item
                record, NetSuite can incorporate network transfers into demand planning for the item.Note: The network and
                category you select must be associated with the subsidiary selected for the item in the Classifications section
                of the item record. For details about how categories are associated with subsidiaries, click Help and read
                Creating Distribution Categories.
        type_ (Optional[SearchItemsDistributionCategoryType]):
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    external_id: Optional[str] = Field(alias="externalId", default=None)
    internal_id: Optional[str] = Field(alias="internalId", default=None)
    name: Optional[str] = Field(alias="name", default=None)
    type_: Optional["SearchItemsDistributionCategoryType"] = Field(
        alias="type", default=None
    )

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(
        cls: Type["SearchItemsDistributionCategory"], src_dict: Dict[str, Any]
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
