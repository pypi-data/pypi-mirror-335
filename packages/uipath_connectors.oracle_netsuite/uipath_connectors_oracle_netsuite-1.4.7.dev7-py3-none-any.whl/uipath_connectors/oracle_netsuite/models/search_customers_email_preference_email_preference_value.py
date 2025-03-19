from enum import Enum


class SearchCustomersEmailPreferenceEmailPreferenceValue(str, Enum):
    VALUE_0 = "_default"
    VALUE_1 = "_hTML"
    VALUE_2 = "_pDF"

    def __str__(self) -> str:
        return str(self.value)
