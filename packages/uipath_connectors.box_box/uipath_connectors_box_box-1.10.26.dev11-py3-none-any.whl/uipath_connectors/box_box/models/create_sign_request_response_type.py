from enum import Enum


class CreateSignRequestResponseType(str, Enum):
    SIGN_REQUEST = "sign-request"

    def __str__(self) -> str:
        return str(self.value)
