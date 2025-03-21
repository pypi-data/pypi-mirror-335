from enum import Enum


class SearchItemsSitemapPriorityValue(str, Enum):
    AUTO = "_auto"
    VALUE_00 = "_00"
    VALUE_01 = "_01"
    VALUE_02 = "_02"
    VALUE_03 = "_03"
    VALUE_04 = "_04"
    VALUE_05 = "_05"
    VALUE_06 = "_06"
    VALUE_07 = "_07"
    VALUE_08 = "_08"
    VALUE_09 = "_09"
    VALUE_10 = "_10"

    def __str__(self) -> str:
        return str(self.value)
