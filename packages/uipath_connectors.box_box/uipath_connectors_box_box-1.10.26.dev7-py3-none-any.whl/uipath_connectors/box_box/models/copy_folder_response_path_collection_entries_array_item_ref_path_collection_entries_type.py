from enum import Enum


class CopyFolderResponsePathCollectionEntriesArrayItemRefPathCollectionEntriesType(
    str, Enum
):
    FOLDER = "folder"

    def __str__(self) -> str:
        return str(self.value)
