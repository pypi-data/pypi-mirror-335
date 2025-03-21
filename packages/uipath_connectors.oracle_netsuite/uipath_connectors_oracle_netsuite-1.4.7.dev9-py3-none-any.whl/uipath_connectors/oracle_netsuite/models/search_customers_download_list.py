from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.search_customers_download_list_download_array_item_ref import (
    SearchCustomersDownloadListDownloadArrayItemRef,
)


class SearchCustomersDownloadList(BaseModel):
    """
    Attributes:
        download (Optional[list['SearchCustomersDownloadListDownloadArrayItemRef']]):
        replace_all (Optional[bool]):
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    download: Optional[list["SearchCustomersDownloadListDownloadArrayItemRef"]] = Field(
        alias="download", default=None
    )
    replace_all: Optional[bool] = Field(alias="replaceAll", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["SearchCustomersDownloadList"], src_dict: Dict[str, Any]):
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
