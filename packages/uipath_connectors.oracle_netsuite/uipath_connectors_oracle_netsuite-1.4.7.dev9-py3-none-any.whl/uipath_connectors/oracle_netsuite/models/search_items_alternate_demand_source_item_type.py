from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type



class SearchItemsAlternateDemandSourceItemType(BaseModel):
    """
    Attributes:
        value (Optional[str]): For demand planning purposes, choose another item if you want to examine the historical
                sales of an item other than the one on the current record. When this field is left blank, the source for
                historical data is the original item.For example, if you are setting up Item A for demand planning, but Item A
                does not have an extensive sales history, you can choose Item B as an alternate source for historical data.
                Then, when demand calculations need to be made for Item A, NetSuite uses Item B’s history for the
                calculations.Note: You can select only an item that is of the same item type to be an alternate source. For
                example, if the original item is an inventory item, the alternate source item must also be an inventory item.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    value: Optional[str] = Field(alias="value", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(
        cls: Type["SearchItemsAlternateDemandSourceItemType"], src_dict: Dict[str, Any]
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
