from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.search_items_translations_list_translation_locale import (
    SearchItemsTranslationsListTranslationLocale,
)


class SearchItemsTranslationsListTranslationArrayItemRef(BaseModel):
    """
    Attributes:
        description (Optional[str]):
        display_name (Optional[str]):
        featured_description (Optional[str]):
        language (Optional[str]):
        locale (Optional[SearchItemsTranslationsListTranslationLocale]):
        no_price_message (Optional[str]):
        out_of_stock_message (Optional[str]):
        page_title (Optional[str]):
        sales_description (Optional[str]):
        specials_description (Optional[str]):
        store_description (Optional[str]):
        store_detailed_description (Optional[str]):
        store_display_name (Optional[str]):
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    description: Optional[str] = Field(alias="description", default=None)
    display_name: Optional[str] = Field(alias="displayName", default=None)
    featured_description: Optional[str] = Field(
        alias="featuredDescription", default=None
    )
    language: Optional[str] = Field(alias="language", default=None)
    locale: Optional["SearchItemsTranslationsListTranslationLocale"] = Field(
        alias="locale", default=None
    )
    no_price_message: Optional[str] = Field(alias="noPriceMessage", default=None)
    out_of_stock_message: Optional[str] = Field(alias="outOfStockMessage", default=None)
    page_title: Optional[str] = Field(alias="pageTitle", default=None)
    sales_description: Optional[str] = Field(alias="salesDescription", default=None)
    specials_description: Optional[str] = Field(
        alias="specialsDescription", default=None
    )
    store_description: Optional[str] = Field(alias="storeDescription", default=None)
    store_detailed_description: Optional[str] = Field(
        alias="storeDetailedDescription", default=None
    )
    store_display_name: Optional[str] = Field(alias="storeDisplayName", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(
        cls: Type["SearchItemsTranslationsListTranslationArrayItemRef"],
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
