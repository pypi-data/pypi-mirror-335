from enum import Enum


class SearchCustomersAlcoholRecipientTypeAlcoholRecipientTypeValue(str, Enum):
    VALUE_0 = "_consumer"
    VALUE_1 = "_licensee"

    def __str__(self) -> str:
        return str(self.value)
