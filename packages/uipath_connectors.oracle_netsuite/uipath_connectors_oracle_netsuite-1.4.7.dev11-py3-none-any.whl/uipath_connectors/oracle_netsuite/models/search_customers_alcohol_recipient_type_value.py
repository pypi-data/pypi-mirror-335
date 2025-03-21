from enum import Enum


class SearchCustomersAlcoholRecipientTypeValue(str, Enum):
    CONSUMER = "_consumer"
    LICENSEE = "_licensee"

    def __str__(self) -> str:
        return str(self.value)
