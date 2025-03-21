from enum import Enum


class SearchItemsVsoeDeferralValue(str, Enum):
    DEFER_BUNDLE_UNTIL_DELIVERED = "_deferBundleUntilDelivered"
    DEFER_UNTIL_ITEM_DELIVERED = "_deferUntilItemDelivered"

    def __str__(self) -> str:
        return str(self.value)
