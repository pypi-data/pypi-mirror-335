from enum import Enum


class AddSharedLinktoaFileResponseOwnedByOwnedByType(str, Enum):
    USER = "user"

    def __str__(self) -> str:
        return str(self.value)
