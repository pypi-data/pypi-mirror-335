from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

import datetime
from ..models.search_items_locations_list_locations_periodic_lot_size_type import (
    SearchItemsLocationsListLocationsPeriodicLotSizeType,
)
from ..models.search_inventory_item_record_ref import SearchInventoryItemRecordRef
from ..models.search_items_locations_list_locations_invt_classification import (
    SearchItemsLocationsListLocationsInvtClassification,
)


class SearchItemsLocationsListLocationsArrayItemRef(BaseModel):
    """
    Attributes:
        alternate_demand_source_item (Optional[SearchInventoryItemRecordRef]):
        average_cost_mli (Optional[float]):
        backward_consumption_days (Optional[int]):
        build_time (Optional[float]):
        cost (Optional[float]):
        costing_lot_size (Optional[float]):
        default_return_cost (Optional[float]):
        demand_source (Optional[SearchInventoryItemRecordRef]):
        demand_time_fence (Optional[int]):
        fixed_lot_size (Optional[float]):
        forward_consumption_days (Optional[int]):
        inventory_cost_template (Optional[SearchInventoryItemRecordRef]):
        invt_classification (Optional[SearchItemsLocationsListLocationsInvtClassification]):
        invt_count_interval (Optional[int]):
        is_wip (Optional[bool]):
        last_invt_count_date (Optional[datetime.datetime]):
        last_purchase_price_mli (Optional[float]):
        lead_time (Optional[int]):
        location (Optional[str]):
        location_allow_store_pickup (Optional[bool]):
        location_id (Optional[SearchInventoryItemRecordRef]):
        location_qty_avail_for_store_pickup (Optional[float]):
        location_store_pickup_buffer_stock (Optional[float]):
        next_invt_count_date (Optional[datetime.datetime]):
        on_hand_value_mli (Optional[float]):
        periodic_lot_size_days (Optional[int]):
        periodic_lot_size_type (Optional[SearchItemsLocationsListLocationsPeriodicLotSizeType]):
        preferred_stock_level (Optional[float]):
        quantity_available (Optional[float]):
        quantity_back_ordered (Optional[float]):
        quantity_committed (Optional[float]):
        quantity_on_hand (Optional[float]):
        quantity_on_order (Optional[float]):
        reorder_point (Optional[float]):
        reschedule_in_days (Optional[int]):
        reschedule_out_days (Optional[int]):
        safety_stock_level (Optional[float]):
        supply_lot_sizing_method (Optional[SearchInventoryItemRecordRef]):
        supply_replenishment_method (Optional[SearchInventoryItemRecordRef]):
        supply_time_fence (Optional[int]):
        supply_type (Optional[SearchInventoryItemRecordRef]):
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    alternate_demand_source_item: Optional["SearchInventoryItemRecordRef"] = Field(
        alias="alternateDemandSourceItem", default=None
    )
    average_cost_mli: Optional[float] = Field(alias="averageCostMli", default=None)
    backward_consumption_days: Optional[int] = Field(
        alias="backwardConsumptionDays", default=None
    )
    build_time: Optional[float] = Field(alias="buildTime", default=None)
    cost: Optional[float] = Field(alias="cost", default=None)
    costing_lot_size: Optional[float] = Field(alias="costingLotSize", default=None)
    default_return_cost: Optional[float] = Field(
        alias="defaultReturnCost", default=None
    )
    demand_source: Optional["SearchInventoryItemRecordRef"] = Field(
        alias="demandSource", default=None
    )
    demand_time_fence: Optional[int] = Field(alias="demandTimeFence", default=None)
    fixed_lot_size: Optional[float] = Field(alias="fixedLotSize", default=None)
    forward_consumption_days: Optional[int] = Field(
        alias="forwardConsumptionDays", default=None
    )
    inventory_cost_template: Optional["SearchInventoryItemRecordRef"] = Field(
        alias="inventoryCostTemplate", default=None
    )
    invt_classification: Optional[
        "SearchItemsLocationsListLocationsInvtClassification"
    ] = Field(alias="invtClassification", default=None)
    invt_count_interval: Optional[int] = Field(alias="invtCountInterval", default=None)
    is_wip: Optional[bool] = Field(alias="isWip", default=None)
    last_invt_count_date: Optional[datetime.datetime] = Field(
        alias="lastInvtCountDate", default=None
    )
    last_purchase_price_mli: Optional[float] = Field(
        alias="lastPurchasePriceMli", default=None
    )
    lead_time: Optional[int] = Field(alias="leadTime", default=None)
    location: Optional[str] = Field(alias="location", default=None)
    location_allow_store_pickup: Optional[bool] = Field(
        alias="locationAllowStorePickup", default=None
    )
    location_id: Optional["SearchInventoryItemRecordRef"] = Field(
        alias="locationId", default=None
    )
    location_qty_avail_for_store_pickup: Optional[float] = Field(
        alias="locationQtyAvailForStorePickup", default=None
    )
    location_store_pickup_buffer_stock: Optional[float] = Field(
        alias="locationStorePickupBufferStock", default=None
    )
    next_invt_count_date: Optional[datetime.datetime] = Field(
        alias="nextInvtCountDate", default=None
    )
    on_hand_value_mli: Optional[float] = Field(alias="onHandValueMli", default=None)
    periodic_lot_size_days: Optional[int] = Field(
        alias="periodicLotSizeDays", default=None
    )
    periodic_lot_size_type: Optional[
        "SearchItemsLocationsListLocationsPeriodicLotSizeType"
    ] = Field(alias="periodicLotSizeType", default=None)
    preferred_stock_level: Optional[float] = Field(
        alias="preferredStockLevel", default=None
    )
    quantity_available: Optional[float] = Field(alias="quantityAvailable", default=None)
    quantity_back_ordered: Optional[float] = Field(
        alias="quantityBackOrdered", default=None
    )
    quantity_committed: Optional[float] = Field(alias="quantityCommitted", default=None)
    quantity_on_hand: Optional[float] = Field(alias="quantityOnHand", default=None)
    quantity_on_order: Optional[float] = Field(alias="quantityOnOrder", default=None)
    reorder_point: Optional[float] = Field(alias="reorderPoint", default=None)
    reschedule_in_days: Optional[int] = Field(alias="rescheduleInDays", default=None)
    reschedule_out_days: Optional[int] = Field(alias="rescheduleOutDays", default=None)
    safety_stock_level: Optional[float] = Field(alias="safetyStockLevel", default=None)
    supply_lot_sizing_method: Optional["SearchInventoryItemRecordRef"] = Field(
        alias="supplyLotSizingMethod", default=None
    )
    supply_replenishment_method: Optional["SearchInventoryItemRecordRef"] = Field(
        alias="supplyReplenishmentMethod", default=None
    )
    supply_time_fence: Optional[int] = Field(alias="supplyTimeFence", default=None)
    supply_type: Optional["SearchInventoryItemRecordRef"] = Field(
        alias="supplyType", default=None
    )

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(
        cls: Type["SearchItemsLocationsListLocationsArrayItemRef"],
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
