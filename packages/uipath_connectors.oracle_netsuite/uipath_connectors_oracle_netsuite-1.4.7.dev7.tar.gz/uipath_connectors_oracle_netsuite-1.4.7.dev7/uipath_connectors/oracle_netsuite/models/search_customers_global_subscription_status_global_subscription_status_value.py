from enum import Enum


class SearchCustomersGlobalSubscriptionStatusGlobalSubscriptionStatusValue(str, Enum):
    VALUE_0 = "_confirmedOptIn"
    VALUE_1 = "_confirmedOptOut"
    VALUE_2 = "_softOptIn"
    VALUE_3 = "_softOptOut"

    def __str__(self) -> str:
        return str(self.value)
