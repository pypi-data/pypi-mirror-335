from enum import Enum


class UploadFileVersionResponsePathCollectionEntriesType(str, Enum):
    FOLDER = "folder"

    def __str__(self) -> str:
        return str(self.value)
