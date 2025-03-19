from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.search_inventory_item_record_ref import SearchInventoryItemRecordRef


class SearchItemsBinNumberListBinNumberArrayItemRef(BaseModel):
    """
    Attributes:
        bin_number (Optional[SearchInventoryItemRecordRef]):
        location (Optional[str]):
        on_hand (Optional[str]):
        on_hand_avail (Optional[str]):
        preferred_bin (Optional[bool]):
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    bin_number: Optional["SearchInventoryItemRecordRef"] = Field(
        alias="binNumber", default=None
    )
    location: Optional[str] = Field(alias="location", default=None)
    on_hand: Optional[str] = Field(alias="onHand", default=None)
    on_hand_avail: Optional[str] = Field(alias="onHandAvail", default=None)
    preferred_bin: Optional[bool] = Field(alias="preferredBin", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(
        cls: Type["SearchItemsBinNumberListBinNumberArrayItemRef"],
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
