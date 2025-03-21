from enum import Enum


class CreateFolderRequestSyncState(str, Enum):
    NOT_SYNCED = "not_synced"
    PARTIALLY_SYNCED = "partially_synced"
    SYNCED = "synced"

    def __str__(self) -> str:
        return str(self.value)
