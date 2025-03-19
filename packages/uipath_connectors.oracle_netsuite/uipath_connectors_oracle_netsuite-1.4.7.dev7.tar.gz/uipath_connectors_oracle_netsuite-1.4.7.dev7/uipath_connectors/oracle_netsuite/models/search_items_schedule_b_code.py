from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.search_items_schedule_b_code_schedule_bcode_value import (
    SearchItemsScheduleBCodeScheduleBcodeValue,
)


class SearchItemsScheduleBCode(BaseModel):
    """
    Attributes:
        value (Optional[SearchItemsScheduleBCodeScheduleBcodeValue]): Select the code for the Schedule B form for this
                item. Available values are:_1000, _1000cubicMeters, _barrels, _carat, _cleanYieldKilogram, _contentKilogram,
                _contentTon, _cubicMeters, _curie, _dozen, _dozenPairs, _dozenPieces, _fiberMeter, _gram, _gross,
                _grossContainers, _hundred, _kilogram, _kilogramTotalSugars, _liter, _meter, _millicurie, _noQuantityReq,
                _number, _pack, _pairs, _pieces, _proofLiter, _runningBales, _square, _squareCentimeters, _squareMeters, _ton
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    value: Optional[SearchItemsScheduleBCodeScheduleBcodeValue] = Field(
        alias="value", default=None
    )

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["SearchItemsScheduleBCode"], src_dict: Dict[str, Any]):
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
