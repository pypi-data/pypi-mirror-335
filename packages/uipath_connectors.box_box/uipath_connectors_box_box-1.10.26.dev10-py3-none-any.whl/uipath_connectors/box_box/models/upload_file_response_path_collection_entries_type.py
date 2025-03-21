from enum import Enum


class UploadFileResponsePathCollectionEntriesType(str, Enum):
    FOLDER = "folder"

    def __str__(self) -> str:
        return str(self.value)
