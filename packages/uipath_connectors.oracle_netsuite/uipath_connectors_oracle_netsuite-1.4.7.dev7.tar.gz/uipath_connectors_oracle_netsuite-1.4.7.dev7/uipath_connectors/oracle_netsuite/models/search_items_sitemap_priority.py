from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.search_items_sitemap_priority_sitemap_priority_value import (
    SearchItemsSitemapPrioritySitemapPriorityValue,
)


class SearchItemsSitemapPriority(BaseModel):
    """
    Attributes:
        value (Optional[SearchItemsSitemapPrioritySitemapPriorityValue]): Use the Sitemap Priority list to indicate the
                relative importance of your Web site URLs.You can select a priority ranging from 0.0 to 1.0 on item, category,
                and tab records.NetSuite assigns the default priority “Auto” to all new and existing tab, category and item
                records in your account. The priority is calculated based on the position of the item or category in the
                hierarchy of your Web site.For example, your Web site tabs automatically generate a default priority value of
                1.0 because they are top level pages. A category published to a tab gets a priority of 0.5. An item published to
                a category on a tab gets a priority of 0.3.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    value: Optional[SearchItemsSitemapPrioritySitemapPriorityValue] = Field(
        alias="value", default=None
    )

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["SearchItemsSitemapPriority"], src_dict: Dict[str, Any]):
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
