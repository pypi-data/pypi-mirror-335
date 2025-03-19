from enum import Enum


class SearchCustomersMonthlyClosingMonthlyClosingValue(str, Enum):
    VALUE_0 = "_one"
    VALUE_1 = "_five"
    VALUE_2 = "_ten"
    VALUE_3 = "_fifteen"
    VALUE_4 = "_twenty"
    VALUE_5 = "_twentyFive"
    VALUE_6 = "_endOfTheMonth"

    def __str__(self) -> str:
        return str(self.value)
