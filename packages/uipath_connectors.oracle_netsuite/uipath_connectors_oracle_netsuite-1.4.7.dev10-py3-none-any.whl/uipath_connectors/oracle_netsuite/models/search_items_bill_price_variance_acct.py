from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.search_items_bill_price_variance_acct_type import (
    SearchItemsBillPriceVarianceAcctType,
)


class SearchItemsBillPriceVarianceAcct(BaseModel):
    """
    Attributes:
        external_id (Optional[str]): Select the account to post to for variances in billing prices associated with this
                item. These variances occur when there is a difference in the price of an item showing on the purchase order and
                the price of an item showing on the bill.Note: After you select a variance account in this field, you can select
                another account at a later date if a change is necessary. Account changes are noted on the System Notes subtab
                of the History subtab of item records.
        internal_id (Optional[str]): Select the account to post to for variances in billing prices associated with this
                item. These variances occur when there is a difference in the price of an item showing on the purchase order and
                the price of an item showing on the bill.Note: After you select a variance account in this field, you can select
                another account at a later date if a change is necessary. Account changes are noted on the System Notes subtab
                of the History subtab of item records.
        name (Optional[str]): Select the account to post to for variances in billing prices associated with this item.
                These variances occur when there is a difference in the price of an item showing on the purchase order and the
                price of an item showing on the bill.Note: After you select a variance account in this field, you can select
                another account at a later date if a change is necessary. Account changes are noted on the System Notes subtab
                of the History subtab of item records.
        type_ (Optional[SearchItemsBillPriceVarianceAcctType]):
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    external_id: Optional[str] = Field(alias="externalId", default=None)
    internal_id: Optional[str] = Field(alias="internalId", default=None)
    name: Optional[str] = Field(alias="name", default=None)
    type_: Optional["SearchItemsBillPriceVarianceAcctType"] = Field(
        alias="type", default=None
    )

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(
        cls: Type["SearchItemsBillPriceVarianceAcct"], src_dict: Dict[str, Any]
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
