from enum import Enum


class CancelSignRequestResponseSignFilesFilesFileVersionSignFilesFileVersionType(
    str, Enum
):
    FILE_VERSION = "file_version"

    def __str__(self) -> str:
        return str(self.value)
