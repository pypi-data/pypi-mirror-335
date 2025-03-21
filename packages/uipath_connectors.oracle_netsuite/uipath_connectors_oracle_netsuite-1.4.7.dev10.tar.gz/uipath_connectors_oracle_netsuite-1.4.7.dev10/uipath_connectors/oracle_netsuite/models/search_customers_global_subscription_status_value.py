from enum import Enum


class SearchCustomersGlobalSubscriptionStatusValue(str, Enum):
    CONFIRMED_OPT_IN = "_confirmedOptIn"
    CONFIRMED_OPT_OUT = "_confirmedOptOut"
    SOFT_OPT_IN = "_softOptIn"
    SOFT_OPT_OUT = "_softOptOut"

    def __str__(self) -> str:
        return str(self.value)
