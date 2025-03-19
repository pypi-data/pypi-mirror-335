from enum import Enum


class AddSharedLinktoaFileResponseSharedLinkSharedLinkAccess(str, Enum):
    COLLABORATORS = "collaborators"
    COMPANY = "company"
    OPEN = "open"

    def __str__(self) -> str:
        return str(self.value)
