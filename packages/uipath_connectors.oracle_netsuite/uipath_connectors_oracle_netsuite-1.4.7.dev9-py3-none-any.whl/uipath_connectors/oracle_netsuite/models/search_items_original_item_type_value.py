from enum import Enum


class SearchItemsOriginalItemTypeValue(str, Enum):
    ASSEMBLY = "_assembly"
    DESCRIPTION = "_description"
    DISCOUNT = "_discount"
    DOWNLOAD_ITEM = "_downloadItem"
    GIFT_CERTIFICATE_ITEM = "_giftCertificateItem"
    INVENTORY_ITEM = "_inventoryItem"
    ITEM_GROUP = "_itemGroup"
    KIT = "_kit"
    MARKUP = "_markup"
    NON_INVENTORY_ITEM = "_nonInventoryItem"
    OTHER_CHARGE = "_otherCharge"
    PAYMENT = "_payment"
    SERVICE = "_service"
    SUBTOTAL = "_subtotal"

    def __str__(self) -> str:
        return str(self.value)
