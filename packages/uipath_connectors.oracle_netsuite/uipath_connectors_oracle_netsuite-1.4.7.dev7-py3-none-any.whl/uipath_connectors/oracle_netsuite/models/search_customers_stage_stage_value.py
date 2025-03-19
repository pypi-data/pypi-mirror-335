from enum import Enum


class SearchCustomersStageStageValue(str, Enum):
    VALUE_0 = "_customer"
    VALUE_1 = "_lead"
    VALUE_2 = "_prospect"

    def __str__(self) -> str:
        return str(self.value)
