from enum import Enum


class CancelSignRequestResponseType(str, Enum):
    SIGN_REQUEST = "sign-request"

    def __str__(self) -> str:
        return str(self.value)
