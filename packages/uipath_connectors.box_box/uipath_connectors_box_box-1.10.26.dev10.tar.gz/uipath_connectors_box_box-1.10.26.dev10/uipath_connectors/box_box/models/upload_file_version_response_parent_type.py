from enum import Enum


class UploadFileVersionResponseParentType(str, Enum):
    FOLDER = "folder"

    def __str__(self) -> str:
        return str(self.value)
