from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.search_inventory_item_record_ref import SearchInventoryItemRecordRef


class SearchItemsItemVendorListItemVendorArrayItemRef(BaseModel):
    """
    Attributes:
        preferred_vendor (Optional[bool]):
        purchase_price (Optional[float]):
        schedule (Optional[SearchInventoryItemRecordRef]):
        subsidiary (Optional[str]):
        vendor (Optional[SearchInventoryItemRecordRef]):
        vendor_code (Optional[str]):
        vendor_currency (Optional[SearchInventoryItemRecordRef]):
        vendor_currency_name (Optional[str]):
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    preferred_vendor: Optional[bool] = Field(alias="preferredVendor", default=None)
    purchase_price: Optional[float] = Field(alias="purchasePrice", default=None)
    schedule: Optional["SearchInventoryItemRecordRef"] = Field(
        alias="schedule", default=None
    )
    subsidiary: Optional[str] = Field(alias="subsidiary", default=None)
    vendor: Optional["SearchInventoryItemRecordRef"] = Field(
        alias="vendor", default=None
    )
    vendor_code: Optional[str] = Field(alias="vendorCode", default=None)
    vendor_currency: Optional["SearchInventoryItemRecordRef"] = Field(
        alias="vendorCurrency", default=None
    )
    vendor_currency_name: Optional[str] = Field(
        alias="vendorCurrencyName", default=None
    )

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(
        cls: Type["SearchItemsItemVendorListItemVendorArrayItemRef"],
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
