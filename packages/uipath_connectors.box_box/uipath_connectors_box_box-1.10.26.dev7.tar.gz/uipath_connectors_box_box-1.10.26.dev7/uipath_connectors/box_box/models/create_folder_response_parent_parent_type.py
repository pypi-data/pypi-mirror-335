from enum import Enum


class CreateFolderResponseParentParentType(str, Enum):
    FOLDER = "folder"

    def __str__(self) -> str:
        return str(self.value)
