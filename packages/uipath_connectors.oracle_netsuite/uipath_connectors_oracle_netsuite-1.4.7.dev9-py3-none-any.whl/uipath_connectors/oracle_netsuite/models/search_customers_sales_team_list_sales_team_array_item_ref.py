from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.search_customers_sales_team_list_sales_team_employee import (
    SearchCustomersSalesTeamListSalesTeamEmployee,
)
from ..models.search_customers_sales_team_list_sales_team_sales_role import (
    SearchCustomersSalesTeamListSalesTeamSalesRole,
)


class SearchCustomersSalesTeamListSalesTeamArrayItemRef(BaseModel):
    """
    Attributes:
        contribution (Optional[float]):
        employee (Optional[SearchCustomersSalesTeamListSalesTeamEmployee]):
        is_primary (Optional[bool]):
        sales_role (Optional[SearchCustomersSalesTeamListSalesTeamSalesRole]):
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    contribution: Optional[float] = Field(alias="contribution", default=None)
    employee: Optional["SearchCustomersSalesTeamListSalesTeamEmployee"] = Field(
        alias="employee", default=None
    )
    is_primary: Optional[bool] = Field(alias="isPrimary", default=None)
    sales_role: Optional["SearchCustomersSalesTeamListSalesTeamSalesRole"] = Field(
        alias="salesRole", default=None
    )

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(
        cls: Type["SearchCustomersSalesTeamListSalesTeamArrayItemRef"],
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
