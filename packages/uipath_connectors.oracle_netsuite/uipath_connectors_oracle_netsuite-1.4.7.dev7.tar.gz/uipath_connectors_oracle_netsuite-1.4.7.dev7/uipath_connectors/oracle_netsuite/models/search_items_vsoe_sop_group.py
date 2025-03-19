from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.search_items_vsoe_sop_group_vsoe_sop_group_value import (
    SearchItemsVsoeSopGroupVsoeSopGroupValue,
)


class SearchItemsVsoeSopGroup(BaseModel):
    """
    Attributes:
        value (Optional[SearchItemsVsoeSopGroupVsoeSopGroupValue]): Select an allocation type to associate with this
                item on sales transactions.    * Normal - Revenue allocation follows EITF 08-01 rules when you use VSOE and the
                fair value price list with advanced revenue management.    * Exclude - This item is excluded from revenue
                allocation. The item discounted sales amount is the revenue amount.    * Software - The item is software. When
                you use VSOE with the EITF SuiteApp, both EITF 08-01 and SOP 97-2 rules apply for revenue allocation. When you
                use advanced revenue management, revenue allocation follows the fair value price list. Then if the fair value
                prices for any of the items in the allocation are estimates rather than VSOE, the allocation is recalculated
                using the residual method.Note: Do not select the Software value unless you are using VSOE with the EITF
                SuiteApp or Advanced Revenue Management.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    value: Optional[SearchItemsVsoeSopGroupVsoeSopGroupValue] = Field(
        alias="value", default=None
    )

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["SearchItemsVsoeSopGroup"], src_dict: Dict[str, Any]):
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
