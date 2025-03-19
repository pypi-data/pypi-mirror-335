from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

import datetime
from ..models.search_inventory_item_record_ref import SearchInventoryItemRecordRef


class SearchItemsHierarchyVersionsListInventoryItemHierarchyVersionsArrayItemRef(
    BaseModel
):
    """
    Attributes:
        end_date (Optional[datetime.datetime]):
        hierarchy_node (Optional[SearchInventoryItemRecordRef]):
        hierarchy_version (Optional[SearchInventoryItemRecordRef]):
        is_included (Optional[bool]):
        start_date (Optional[datetime.datetime]):
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    end_date: Optional[datetime.datetime] = Field(alias="endDate", default=None)
    hierarchy_node: Optional["SearchInventoryItemRecordRef"] = Field(
        alias="hierarchyNode", default=None
    )
    hierarchy_version: Optional["SearchInventoryItemRecordRef"] = Field(
        alias="hierarchyVersion", default=None
    )
    is_included: Optional[bool] = Field(alias="isIncluded", default=None)
    start_date: Optional[datetime.datetime] = Field(alias="startDate", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(
        cls: Type[
            "SearchItemsHierarchyVersionsListInventoryItemHierarchyVersionsArrayItemRef"
        ],
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
