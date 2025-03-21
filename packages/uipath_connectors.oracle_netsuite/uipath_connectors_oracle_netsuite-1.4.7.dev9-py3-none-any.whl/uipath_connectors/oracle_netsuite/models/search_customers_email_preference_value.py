from enum import Enum


class SearchCustomersEmailPreferenceValue(str, Enum):
    DEFAULT = "_default"
    HTML = "_hTML"
    PDF = "_pDF"

    def __str__(self) -> str:
        return str(self.value)
