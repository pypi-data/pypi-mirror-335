from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type



class SearchItemsGainLossAccountType(BaseModel):
    """
    Attributes:
        value (Optional[str]): When the Use Item Cost as Transfer Cost preference is disabled, the transfer price on a
                transfer order is used as the item cost on the item receipt. Any difference between the actual cost and the
                transfer price posts to a Gain/Loss account when the item is shipped.In this field, select the Gain/Loss account
                you prefer to use to post transfer cost discrepancies. The account you select must be different than the Asset
                or Cost of Goods Sold (COGS) account for the item.You can choose an Income account, Other Income account,
                Expense account, or Other Expense account. Note: If you have enabled the Expand Account Lists preference, you
                can choose any account in this field.If you leave this field blank or select Use Income Account, then the income
                account for the item is used.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    value: Optional[str] = Field(alias="value", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(
        cls: Type["SearchItemsGainLossAccountType"], src_dict: Dict[str, Any]
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
