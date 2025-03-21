from enum import Enum


class CreateFolderResponseModifiedByType(str, Enum):
    USER = "user"

    def __str__(self) -> str:
        return str(self.value)
