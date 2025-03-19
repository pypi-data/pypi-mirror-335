from enum import Enum


class SearchItemsFraudRiskFraudRiskValue(str, Enum):
    VALUE_0 = "_high"
    VALUE_1 = "_low"
    VALUE_2 = "_medium"

    def __str__(self) -> str:
        return str(self.value)
