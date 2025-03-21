from enum import Enum


class SearchItemStatus(str, Enum):
    ACTIVE = "active"
    DELETED = "deleted"
    TRASHED = "trashed"

    def __str__(self) -> str:
        return str(self.value)
