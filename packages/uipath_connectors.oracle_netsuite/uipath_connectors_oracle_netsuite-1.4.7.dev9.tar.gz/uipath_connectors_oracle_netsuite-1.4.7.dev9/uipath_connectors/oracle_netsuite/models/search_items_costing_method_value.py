from enum import Enum


class SearchItemsCostingMethodValue(str, Enum):
    AVERAGE = "_average"
    FIFO = "_fifo"
    GROUP_AVERAGE = "_groupAverage"
    LIFO = "_lifo"
    LOT_NUMBERED = "_lotNumbered"
    SERIALIZED = "_serialized"
    STANDARD = "_standard"

    def __str__(self) -> str:
        return str(self.value)
