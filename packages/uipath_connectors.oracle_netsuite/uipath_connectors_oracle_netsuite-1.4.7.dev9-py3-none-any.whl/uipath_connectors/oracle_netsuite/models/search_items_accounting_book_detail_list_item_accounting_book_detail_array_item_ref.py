from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.search_items_accounting_book_detail_list_item_accounting_book_detail_accounting_book import (
    SearchItemsAccountingBookDetailListItemAccountingBookDetailAccountingBook,
)
from ..models.search_items_accounting_book_detail_list_item_accounting_book_detail_amortization_template import (
    SearchItemsAccountingBookDetailListItemAccountingBookDetailAmortizationTemplate,
)
from ..models.search_items_accounting_book_detail_list_item_accounting_book_detail_create_revenue_plans_on import (
    SearchItemsAccountingBookDetailListItemAccountingBookDetailCreateRevenuePlansOn,
)
from ..models.search_items_accounting_book_detail_list_item_accounting_book_detail_rev_rec_forecast_rule import (
    SearchItemsAccountingBookDetailListItemAccountingBookDetailRevRecForecastRule,
)
from ..models.search_items_accounting_book_detail_list_item_accounting_book_detail_rev_rec_schedule import (
    SearchItemsAccountingBookDetailListItemAccountingBookDetailRevRecSchedule,
)
from ..models.search_items_accounting_book_detail_list_item_accounting_book_detail_revenue_recognition_rule import (
    SearchItemsAccountingBookDetailListItemAccountingBookDetailRevenueRecognitionRule,
)


class SearchItemsAccountingBookDetailListItemAccountingBookDetailArrayItemRef(
    BaseModel
):
    """
    Attributes:
        accounting_book (Optional[SearchItemsAccountingBookDetailListItemAccountingBookDetailAccountingBook]):
        amortization_template
                (Optional[SearchItemsAccountingBookDetailListItemAccountingBookDetailAmortizationTemplate]):
        create_revenue_plans_on
                (Optional[SearchItemsAccountingBookDetailListItemAccountingBookDetailCreateRevenuePlansOn]):
        rev_rec_forecast_rule (Optional[SearchItemsAccountingBookDetailListItemAccountingBookDetailRevRecForecastRule]):
        rev_rec_schedule (Optional[SearchItemsAccountingBookDetailListItemAccountingBookDetailRevRecSchedule]):
        revenue_recognition_rule
                (Optional[SearchItemsAccountingBookDetailListItemAccountingBookDetailRevenueRecognitionRule]):
        same_as_primary_amortization (Optional[bool]):
        same_as_primary_rev_rec (Optional[bool]):
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    accounting_book: Optional[
        "SearchItemsAccountingBookDetailListItemAccountingBookDetailAccountingBook"
    ] = Field(alias="accountingBook", default=None)
    amortization_template: Optional[
        "SearchItemsAccountingBookDetailListItemAccountingBookDetailAmortizationTemplate"
    ] = Field(alias="amortizationTemplate", default=None)
    create_revenue_plans_on: Optional[
        "SearchItemsAccountingBookDetailListItemAccountingBookDetailCreateRevenuePlansOn"
    ] = Field(alias="createRevenuePlansOn", default=None)
    rev_rec_forecast_rule: Optional[
        "SearchItemsAccountingBookDetailListItemAccountingBookDetailRevRecForecastRule"
    ] = Field(alias="revRecForecastRule", default=None)
    rev_rec_schedule: Optional[
        "SearchItemsAccountingBookDetailListItemAccountingBookDetailRevRecSchedule"
    ] = Field(alias="revRecSchedule", default=None)
    revenue_recognition_rule: Optional[
        "SearchItemsAccountingBookDetailListItemAccountingBookDetailRevenueRecognitionRule"
    ] = Field(alias="revenueRecognitionRule", default=None)
    same_as_primary_amortization: Optional[bool] = Field(
        alias="sameAsPrimaryAmortization", default=None
    )
    same_as_primary_rev_rec: Optional[bool] = Field(
        alias="sameAsPrimaryRevRec", default=None
    )

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(
        cls: Type[
            "SearchItemsAccountingBookDetailListItemAccountingBookDetailArrayItemRef"
        ],
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
