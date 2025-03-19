from enum import Enum


class SearchItemsPresentationItemListPresentationItemItemTypePresentationItemListPresentationItemItemTypeValue(
    str, Enum
):
    VALUE_0 = "_fileCabinetItem"
    VALUE_1 = "_informationItem"
    VALUE_2 = "_item"
    VALUE_3 = "_presentationCategory"

    def __str__(self) -> str:
        return str(self.value)
