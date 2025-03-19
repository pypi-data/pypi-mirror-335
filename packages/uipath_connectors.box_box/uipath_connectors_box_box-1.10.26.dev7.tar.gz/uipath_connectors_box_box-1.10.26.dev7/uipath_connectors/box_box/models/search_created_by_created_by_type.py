from enum import Enum


class SearchCreatedByCreatedByType(str, Enum):
    USER = "user"

    def __str__(self) -> str:
        return str(self.value)
