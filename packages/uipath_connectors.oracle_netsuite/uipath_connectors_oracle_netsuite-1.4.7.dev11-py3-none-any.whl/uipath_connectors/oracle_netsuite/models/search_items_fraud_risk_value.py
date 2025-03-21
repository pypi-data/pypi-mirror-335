from enum import Enum


class SearchItemsFraudRiskValue(str, Enum):
    HIGH = "_high"
    LOW = "_low"
    MEDIUM = "_medium"

    def __str__(self) -> str:
        return str(self.value)
