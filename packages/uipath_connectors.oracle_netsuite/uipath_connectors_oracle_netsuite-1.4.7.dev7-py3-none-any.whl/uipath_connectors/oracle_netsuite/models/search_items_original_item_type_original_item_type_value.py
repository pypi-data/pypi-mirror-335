from enum import Enum


class SearchItemsOriginalItemTypeOriginalItemTypeValue(str, Enum):
    VALUE_0 = "_assembly"
    VALUE_1 = "_description"
    VALUE_10 = "_otherCharge"
    VALUE_11 = "_payment"
    VALUE_12 = "_service"
    VALUE_13 = "_subtotal"
    VALUE_2 = "_discount"
    VALUE_3 = "_downloadItem"
    VALUE_4 = "_giftCertificateItem"
    VALUE_5 = "_inventoryItem"
    VALUE_6 = "_itemGroup"
    VALUE_7 = "_kit"
    VALUE_8 = "_markup"
    VALUE_9 = "_nonInventoryItem"

    def __str__(self) -> str:
        return str(self.value)
