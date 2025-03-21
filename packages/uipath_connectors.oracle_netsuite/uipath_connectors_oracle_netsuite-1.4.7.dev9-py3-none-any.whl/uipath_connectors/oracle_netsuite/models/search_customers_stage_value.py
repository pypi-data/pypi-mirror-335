from enum import Enum


class SearchCustomersStageValue(str, Enum):
    CUSTOMER = "_customer"
    LEAD = "_lead"
    PROSPECT = "_prospect"

    def __str__(self) -> str:
        return str(self.value)
