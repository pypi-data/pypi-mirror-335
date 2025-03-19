from enum import Enum


class ListSignRequestSignFilesFilesArrayItemRefSignFilesType(str, Enum):
    FILE = "file"

    def __str__(self) -> str:
        return str(self.value)
