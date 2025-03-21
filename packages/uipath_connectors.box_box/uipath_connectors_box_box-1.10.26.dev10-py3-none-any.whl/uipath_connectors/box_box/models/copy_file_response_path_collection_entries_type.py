from enum import Enum


class CopyFileResponsePathCollectionEntriesType(str, Enum):
    FOLDER = "folder"

    def __str__(self) -> str:
        return str(self.value)
