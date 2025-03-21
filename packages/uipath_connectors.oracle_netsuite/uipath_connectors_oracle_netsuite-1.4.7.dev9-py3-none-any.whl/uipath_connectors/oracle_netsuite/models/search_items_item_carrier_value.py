from enum import Enum


class SearchItemsItemCarrierValue(str, Enum):
    FEDEX_USPS_MORE = "_fedexUspsMore"
    UPS = "_ups"

    def __str__(self) -> str:
        return str(self.value)
