from enum import Enum


class CreateFolderResponseFolderUploadEmailFolderUploadEmailAccess(str, Enum):
    COLLABORATORS = "collaborators"
    OPEN = "open"

    def __str__(self) -> str:
        return str(self.value)
