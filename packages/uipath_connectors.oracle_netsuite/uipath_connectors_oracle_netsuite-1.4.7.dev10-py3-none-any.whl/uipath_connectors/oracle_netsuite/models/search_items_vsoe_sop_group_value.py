from enum import Enum


class SearchItemsVsoeSopGroupValue(str, Enum):
    EXCLUDE = "_exclude"
    NORMAL = "_normal"
    SOFTWARE = "_software"

    def __str__(self) -> str:
        return str(self.value)
