from enum import Enum


class UploadFileResponseOwnedByOwnedByType(str, Enum):
    USER = "user"

    def __str__(self) -> str:
        return str(self.value)
