from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

import datetime
from ..models.search_customers_record_ref import SearchCustomersRecordRef


class SearchCustomersCreditCardsListCreditCardsArrayItemRef(BaseModel):
    """
    Attributes:
        card_state (Optional[SearchCustomersRecordRef]):
        cc_default (Optional[bool]):
        cc_expire_date (Optional[datetime.datetime]):
        cc_memo (Optional[str]):
        cc_name (Optional[str]):
        cc_number (Optional[str]):
        debitcard_issue_no (Optional[str]):
        internal_id (Optional[str]):
        payment_method (Optional[SearchCustomersRecordRef]):
        state_from (Optional[datetime.datetime]):
        validfrom (Optional[datetime.datetime]):
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    card_state: Optional["SearchCustomersRecordRef"] = Field(
        alias="cardState", default=None
    )
    cc_default: Optional[bool] = Field(alias="ccDefault", default=None)
    cc_expire_date: Optional[datetime.datetime] = Field(
        alias="ccExpireDate", default=None
    )
    cc_memo: Optional[str] = Field(alias="ccMemo", default=None)
    cc_name: Optional[str] = Field(alias="ccName", default=None)
    cc_number: Optional[str] = Field(alias="ccNumber", default=None)
    debitcard_issue_no: Optional[str] = Field(alias="debitcardIssueNo", default=None)
    internal_id: Optional[str] = Field(alias="internalId", default=None)
    payment_method: Optional["SearchCustomersRecordRef"] = Field(
        alias="paymentMethod", default=None
    )
    state_from: Optional[datetime.datetime] = Field(alias="stateFrom", default=None)
    validfrom: Optional[datetime.datetime] = Field(alias="validfrom", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(
        cls: Type["SearchCustomersCreditCardsListCreditCardsArrayItemRef"],
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
