from enum import Enum


class SearchCustomersMonthlyClosingValue(str, Enum):
    END_OF_THE_MONTH = "_endOfTheMonth"
    FIFTEEN = "_fifteen"
    FIVE = "_five"
    ONE = "_one"
    TEN = "_ten"
    TWENTY = "_twenty"
    TWENTY_FIVE = "_twentyFive"

    def __str__(self) -> str:
        return str(self.value)
