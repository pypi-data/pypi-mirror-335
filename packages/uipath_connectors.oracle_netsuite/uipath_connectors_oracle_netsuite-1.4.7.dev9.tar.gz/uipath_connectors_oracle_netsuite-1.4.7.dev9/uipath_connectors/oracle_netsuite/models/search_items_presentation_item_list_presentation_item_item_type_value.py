from enum import Enum


class SearchItemsPresentationItemListPresentationItemItemTypeValue(str, Enum):
    FILE_CABINET_ITEM = "_fileCabinetItem"
    INFORMATION_ITEM = "_informationItem"
    ITEM = "_item"
    PRESENTATION_CATEGORY = "_presentationCategory"

    def __str__(self) -> str:
        return str(self.value)
