from enum import Enum


class GetFileInfoResponseOwnedByOwnedByType(str, Enum):
    USER = "user"

    def __str__(self) -> str:
        return str(self.value)
