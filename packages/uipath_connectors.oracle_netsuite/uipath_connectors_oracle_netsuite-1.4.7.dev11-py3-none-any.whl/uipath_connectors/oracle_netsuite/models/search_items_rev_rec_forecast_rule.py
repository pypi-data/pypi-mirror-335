from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.search_items_rev_rec_forecast_rule_type import (
    SearchItemsRevRecForecastRuleType,
)


class SearchItemsRevRecForecastRule(BaseModel):
    """
    Attributes:
        external_id (Optional[str]): Select a revenue rule to use for forecast revenue recognition plans. The default is
                determined by the same accounting preference as the Revenue Recognition Rule.You may select the same rule or a
                different rule for actual and forecast rules. Percent complete rules are not available as forecast rules. For
                information about forecast revenue plans for project progress, see Working with Percent-Complete Revenue
                Recognition Plans.
        internal_id (Optional[str]): Select a revenue rule to use for forecast revenue recognition plans. The default is
                determined by the same accounting preference as the Revenue Recognition Rule.You may select the same rule or a
                different rule for actual and forecast rules. Percent complete rules are not available as forecast rules. For
                information about forecast revenue plans for project progress, see Working with Percent-Complete Revenue
                Recognition Plans.
        name (Optional[str]): Select a revenue rule to use for forecast revenue recognition plans. The default is
                determined by the same accounting preference as the Revenue Recognition Rule.You may select the same rule or a
                different rule for actual and forecast rules. Percent complete rules are not available as forecast rules. For
                information about forecast revenue plans for project progress, see Working with Percent-Complete Revenue
                Recognition Plans.
        type_ (Optional[SearchItemsRevRecForecastRuleType]):
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    external_id: Optional[str] = Field(alias="externalId", default=None)
    internal_id: Optional[str] = Field(alias="internalId", default=None)
    name: Optional[str] = Field(alias="name", default=None)
    type_: Optional["SearchItemsRevRecForecastRuleType"] = Field(
        alias="type", default=None
    )

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["SearchItemsRevRecForecastRule"], src_dict: Dict[str, Any]):
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
