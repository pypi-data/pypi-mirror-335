from enum import Enum


class SearchItemsSitemapPrioritySitemapPriorityValue(str, Enum):
    VALUE_0 = "_00"
    VALUE_1 = "_01"
    VALUE_10 = "_10"
    VALUE_11 = "_auto"
    VALUE_2 = "_02"
    VALUE_3 = "_03"
    VALUE_4 = "_04"
    VALUE_5 = "_05"
    VALUE_6 = "_06"
    VALUE_7 = "_07"
    VALUE_8 = "_08"
    VALUE_9 = "_09"

    def __str__(self) -> str:
        return str(self.value)
