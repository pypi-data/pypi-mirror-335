from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.search_items_interco_def_rev_account_type import (
    SearchItemsIntercoDefRevAccountType,
)


class SearchItemsIntercoDefRevAccount(BaseModel):
    """
    Attributes:
        external_id (Optional[str]): Select the account to use for intercompany deferred revenue. This account is used
                to record transactions between subsidiaries in NetSuite OneWorld accounts. The options include only accounts
                with the Eliminate Intercompany Transactions box checked.For more more information about intercompany
                transactions, see the help topic Understanding Automated Intercompany Management.
        internal_id (Optional[str]): Select the account to use for intercompany deferred revenue. This account is used
                to record transactions between subsidiaries in NetSuite OneWorld accounts. The options include only accounts
                with the Eliminate Intercompany Transactions box checked.For more more information about intercompany
                transactions, see the help topic Understanding Automated Intercompany Management.
        name (Optional[str]): Select the account to use for intercompany deferred revenue. This account is used to
                record transactions between subsidiaries in NetSuite OneWorld accounts. The options include only accounts with
                the Eliminate Intercompany Transactions box checked.For more more information about intercompany transactions,
                see the help topic Understanding Automated Intercompany Management.
        type_ (Optional[SearchItemsIntercoDefRevAccountType]):
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    external_id: Optional[str] = Field(alias="externalId", default=None)
    internal_id: Optional[str] = Field(alias="internalId", default=None)
    name: Optional[str] = Field(alias="name", default=None)
    type_: Optional["SearchItemsIntercoDefRevAccountType"] = Field(
        alias="type", default=None
    )

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(
        cls: Type["SearchItemsIntercoDefRevAccount"], src_dict: Dict[str, Any]
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
