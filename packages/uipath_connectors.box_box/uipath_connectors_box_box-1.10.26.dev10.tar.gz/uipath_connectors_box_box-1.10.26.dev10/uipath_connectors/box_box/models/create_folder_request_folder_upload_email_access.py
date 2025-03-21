from enum import Enum


class CreateFolderRequestFolderUploadEmailAccess(str, Enum):
    COLLABORATORS = "collaborators"
    OPEN = "open"

    def __str__(self) -> str:
        return str(self.value)
