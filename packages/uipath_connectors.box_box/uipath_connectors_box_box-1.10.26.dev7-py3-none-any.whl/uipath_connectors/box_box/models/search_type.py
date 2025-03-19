from enum import Enum


class SearchType(str, Enum):
    FILE = "file"
    FOLDER = "folder"
    WEB_LINK = "web_link"

    def __str__(self) -> str:
        return str(self.value)
