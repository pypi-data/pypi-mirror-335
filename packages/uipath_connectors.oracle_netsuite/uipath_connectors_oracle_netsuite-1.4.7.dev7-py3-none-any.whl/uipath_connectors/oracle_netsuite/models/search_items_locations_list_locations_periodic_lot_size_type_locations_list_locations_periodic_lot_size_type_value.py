from enum import Enum


class SearchItemsLocationsListLocationsPeriodicLotSizeTypeLocationsListLocationsPeriodicLotSizeTypeValue(
    str, Enum
):
    VALUE_0 = "_interval"
    VALUE_1 = "_monthly"
    VALUE_2 = "_weekly"

    def __str__(self) -> str:
        return str(self.value)
