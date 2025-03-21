from enum import Enum


class AddSharedLinktoaFolderResponseType(str, Enum):
    FOLDER = "folder"

    def __str__(self) -> str:
        return str(self.value)
