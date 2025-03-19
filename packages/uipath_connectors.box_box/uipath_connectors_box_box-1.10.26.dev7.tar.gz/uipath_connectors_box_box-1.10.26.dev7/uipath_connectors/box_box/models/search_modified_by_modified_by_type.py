from enum import Enum


class SearchModifiedByModifiedByType(str, Enum):
    USER = "user"

    def __str__(self) -> str:
        return str(self.value)
