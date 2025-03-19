from enum import Enum


class SearchItemsVsoeSopGroupVsoeSopGroupValue(str, Enum):
    VALUE_0 = "_exclude"
    VALUE_1 = "_normal"
    VALUE_2 = "_software"

    def __str__(self) -> str:
        return str(self.value)
