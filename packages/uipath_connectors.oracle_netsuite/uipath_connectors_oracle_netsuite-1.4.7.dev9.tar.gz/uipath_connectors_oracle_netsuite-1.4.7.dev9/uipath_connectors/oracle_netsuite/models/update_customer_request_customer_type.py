from enum import Enum


class UpdateCustomerRequestCustomerType(str, Enum):
    COMPANY = "COMPANY"
    INDIVIDUAL = "INDIVIDUAL"

    def __str__(self) -> str:
        return str(self.value)
