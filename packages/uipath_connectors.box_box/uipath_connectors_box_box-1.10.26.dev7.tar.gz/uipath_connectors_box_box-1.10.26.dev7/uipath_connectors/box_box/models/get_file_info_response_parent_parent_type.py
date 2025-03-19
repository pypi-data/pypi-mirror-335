from enum import Enum


class GetFileInfoResponseParentParentType(str, Enum):
    FOLDER = "folder"

    def __str__(self) -> str:
        return str(self.value)
