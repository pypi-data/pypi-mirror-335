from enum import Enum


class UploadFileResponsePathCollectionEntriesArrayItemRefPathCollectionEntriesType(
    str, Enum
):
    FOLDER = "folder"

    def __str__(self) -> str:
        return str(self.value)
