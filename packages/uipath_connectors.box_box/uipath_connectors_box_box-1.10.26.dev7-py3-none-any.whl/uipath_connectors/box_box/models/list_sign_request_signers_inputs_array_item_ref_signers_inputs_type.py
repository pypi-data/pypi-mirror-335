from enum import Enum


class ListSignRequestSignersInputsArrayItemRefSignersInputsType(str, Enum):
    CHECKBOX = "checkbox"
    DATE = "date"
    SIGNATURE = "signature"
    TEXT = "text"

    def __str__(self) -> str:
        return str(self.value)
