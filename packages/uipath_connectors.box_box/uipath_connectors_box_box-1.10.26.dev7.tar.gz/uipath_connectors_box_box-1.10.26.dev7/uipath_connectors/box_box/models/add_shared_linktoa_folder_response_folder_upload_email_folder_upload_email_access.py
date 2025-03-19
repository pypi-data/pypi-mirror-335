from enum import Enum


class AddSharedLinktoaFolderResponseFolderUploadEmailFolderUploadEmailAccess(str, Enum):
    COLLABORATORS = "collaborators"
    OPEN = "open"

    def __str__(self) -> str:
        return str(self.value)
