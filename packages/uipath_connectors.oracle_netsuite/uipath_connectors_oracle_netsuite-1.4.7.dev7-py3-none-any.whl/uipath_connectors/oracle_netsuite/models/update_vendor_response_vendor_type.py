from enum import Enum


class UpdateVendorResponseVendorType(str, Enum):
    COMPANY = "COMPANY"
    INDIVIDUAL = "INDIVIDUAL"

    def __str__(self) -> str:
        return str(self.value)
