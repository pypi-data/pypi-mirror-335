from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.search_items_location_type import SearchItemsLocationType


class SearchItemsLocation(BaseModel):
    """
    Attributes:
        external_id (Optional[str]): Select a location to associate with this item.To use a location, the Multi-Location
                Inventory feature must be enabled.    * If the Multi-Location Inventory feature is not enabled:      Selecting
                an item record location limits the items that certain roles can access.      For example, Role A is set up to
                access only items associated with Location One. Therefore, employees who have Role A can access only items
                associated with Location One.      Note: If the Multi-Location Inventory feature is not enabled, you cannot use
                this field to track inventory by locations. For example, you cannot track how many widgets you have in stock in
                Location One.      For more information click here.    * If the Multi-Location Inventory feature is enabled:
                Selecting an item record location classifies the item by that location to limit the items that certain roles can
                access. To track inventory per location, use the Locations subtab at the bottom of this form.      For more
                information click here.Select New to enter a new location record.Go to <_TABNAME=LIST_LOCATION_> >
                <_TASKCATEGORY=LIST_LOCATION_> > Locations for details about existing location records.
        internal_id (Optional[str]): Select a location to associate with this item.To use a location, the Multi-Location
                Inventory feature must be enabled.    * If the Multi-Location Inventory feature is not enabled:      Selecting
                an item record location limits the items that certain roles can access.      For example, Role A is set up to
                access only items associated with Location One. Therefore, employees who have Role A can access only items
                associated with Location One.      Note: If the Multi-Location Inventory feature is not enabled, you cannot use
                this field to track inventory by locations. For example, you cannot track how many widgets you have in stock in
                Location One.      For more information click here.    * If the Multi-Location Inventory feature is enabled:
                Selecting an item record location classifies the item by that location to limit the items that certain roles can
                access. To track inventory per location, use the Locations subtab at the bottom of this form.      For more
                information click here.Select New to enter a new location record.Go to <_TABNAME=LIST_LOCATION_> >
                <_TASKCATEGORY=LIST_LOCATION_> > Locations for details about existing location records.
        name (Optional[str]): Select a location to associate with this item.To use a location, the Multi-Location
                Inventory feature must be enabled.    * If the Multi-Location Inventory feature is not enabled:      Selecting
                an item record location limits the items that certain roles can access.      For example, Role A is set up to
                access only items associated with Location One. Therefore, employees who have Role A can access only items
                associated with Location One.      Note: If the Multi-Location Inventory feature is not enabled, you cannot use
                this field to track inventory by locations. For example, you cannot track how many widgets you have in stock in
                Location One.      For more information click here.    * If the Multi-Location Inventory feature is enabled:
                Selecting an item record location classifies the item by that location to limit the items that certain roles can
                access. To track inventory per location, use the Locations subtab at the bottom of this form.      For more
                information click here.Select New to enter a new location record.Go to <_TABNAME=LIST_LOCATION_> >
                <_TASKCATEGORY=LIST_LOCATION_> > Locations for details about existing location records.
        type_ (Optional[SearchItemsLocationType]):
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    external_id: Optional[str] = Field(alias="externalId", default=None)
    internal_id: Optional[str] = Field(alias="internalId", default=None)
    name: Optional[str] = Field(alias="name", default=None)
    type_: Optional["SearchItemsLocationType"] = Field(alias="type", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["SearchItemsLocation"], src_dict: Dict[str, Any]):
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
