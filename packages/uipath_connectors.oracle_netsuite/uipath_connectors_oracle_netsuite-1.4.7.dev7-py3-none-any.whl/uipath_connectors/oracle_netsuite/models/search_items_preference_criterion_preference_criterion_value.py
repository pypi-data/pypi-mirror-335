from enum import Enum


class SearchItemsPreferenceCriterionPreferenceCriterionValue(str, Enum):
    VALUE_0 = "_A"
    VALUE_1 = "_B"
    VALUE_2 = "_C"
    VALUE_3 = "_D"
    VALUE_4 = "_E"
    VALUE_5 = "_F"

    def __str__(self) -> str:
        return str(self.value)
