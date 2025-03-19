from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.search_items_vsoe_deferral_vsoe_deferral_value import (
    SearchItemsVsoeDeferralVsoeDeferralValue,
)


class SearchItemsVsoeDeferral(BaseModel):
    """
    Attributes:
        value (Optional[SearchItemsVsoeDeferralVsoeDeferralValue]): In this field set how to handle deferment when this
                item is sold as part of a bundle. The available options are:_deferBundleUntilDelivered � Until this item is
                marked delivered, the revenue recognition of all items in the bundle is deferred. A typical use for this option
                is to identify items whose revenue recognition depends on the delivery of the item itself, in addition to the
                delivery of a separate service. For example, a specified upgrade would typically be marked Defer Bundle Until
                Delivered._deferUntilItemDelivered � Until this item is marked delivered, the revenue recognition of this item
                is deferred. This setting is the default for this field. Note: The deferral setting you set for each item in a
                bundle works together with the deferral settings for other items in the bundle.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    value: Optional[SearchItemsVsoeDeferralVsoeDeferralValue] = Field(
        alias="value", default=None
    )

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["SearchItemsVsoeDeferral"], src_dict: Dict[str, Any]):
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
