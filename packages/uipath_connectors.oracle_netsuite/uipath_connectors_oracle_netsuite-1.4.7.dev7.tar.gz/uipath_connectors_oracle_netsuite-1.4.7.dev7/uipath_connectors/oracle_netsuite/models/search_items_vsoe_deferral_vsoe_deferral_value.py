from enum import Enum


class SearchItemsVsoeDeferralVsoeDeferralValue(str, Enum):
    VALUE_0 = "_deferBundleUntilDelivered"
    VALUE_1 = "_deferUntilItemDelivered"

    def __str__(self) -> str:
        return str(self.value)
