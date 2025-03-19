from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.create_sign_request_response_sign_files_files_file_version_sign_files_file_version_type import (
    CreateSignRequestResponseSignFilesFilesFileVersionSignFilesFileVersionType,
)


class CreateSignRequestResponseSignFilesFilesFileVersion(BaseModel):
    """
    Attributes:
        id (Optional[str]): The unique identifier that represent a file version.
        sha1 (Optional[str]): The SHA1 hash of this version of the file.
        type_ (Optional[CreateSignRequestResponseSignFilesFilesFileVersionSignFilesFileVersionType]): `file_version`
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    id: Optional[str] = Field(alias="id", default=None)
    sha1: Optional[str] = Field(alias="sha1", default=None)
    type_: Optional[
        CreateSignRequestResponseSignFilesFilesFileVersionSignFilesFileVersionType
    ] = Field(alias="type", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(
        cls: Type["CreateSignRequestResponseSignFilesFilesFileVersion"],
        src_dict: Dict[str, Any],
    ):
        return cls.model_validate(src_dict)

    @property
    def additional_keys(self) -> list[str]:
        base_fields = self.model_fields.keys()
        return [k for k in self.__dict__ if k not in base_fields]

    def __getitem__(self, key: str) -> Any:
        if key in self.__dict__:
            return self.__dict__[key]
        raise KeyError(key)

    def __setitem__(self, key: str, value: Any) -> None:
        self.__dict__[key] = value

    def __delitem__(self, key: str) -> None:
        if key in self.__dict__:
            del self.__dict__[key]
        else:
            raise KeyError(key)

    def __contains__(self, key: str) -> bool:
        return key in self.__dict__
