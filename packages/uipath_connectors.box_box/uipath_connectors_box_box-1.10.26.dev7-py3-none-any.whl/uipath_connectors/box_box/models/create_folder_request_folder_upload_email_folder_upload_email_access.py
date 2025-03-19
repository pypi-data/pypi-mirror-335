from enum import Enum


class CreateFolderRequestFolderUploadEmailFolderUploadEmailAccess(str, Enum):
    COLLABORATORS = "collaborators"
    OPEN = "open"

    def __str__(self) -> str:
        return str(self.value)
