from enum import Enum


class SearchItemsLocationsListLocationsPeriodicLotSizeTypeValue(str, Enum):
    INTERVAL = "_interval"
    MONTHLY = "_monthly"
    WEEKLY = "_weekly"

    def __str__(self) -> str:
        return str(self.value)
