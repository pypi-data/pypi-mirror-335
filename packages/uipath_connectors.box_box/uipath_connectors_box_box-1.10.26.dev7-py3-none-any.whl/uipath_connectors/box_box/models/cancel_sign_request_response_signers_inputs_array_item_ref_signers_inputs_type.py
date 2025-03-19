from enum import Enum


class CancelSignRequestResponseSignersInputsArrayItemRefSignersInputsType(str, Enum):
    CHECKBOX = "checkbox"
    DATE = "date"
    SIGNATURE = "signature"
    TEXT = "text"

    def __str__(self) -> str:
        return str(self.value)
