from enum import Enum


class AddSharedLinktoaFolderResponseSharedLinkSharedLinkEffectiveAccess(str, Enum):
    COLLABORATORS = "collaborators"
    COMPANY = "company"
    OPEN = "open"

    def __str__(self) -> str:
        return str(self.value)
