from enum import Enum


class SearchItemsPreferenceCriterionValue(str, Enum):
    A = "_A"
    B = "_B"
    C = "_C"
    D = "_D"
    E = "_E"
    F = "_F"

    def __str__(self) -> str:
        return str(self.value)
