from enum import Enum


class CreateFolderResponseParentType(str, Enum):
    FOLDER = "folder"

    def __str__(self) -> str:
        return str(self.value)
