from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.get_folder_items_file_type import GetFolderItemsFileType
from ..models.get_folder_items_file_version import GetFolderItemsFileVersion


class GetFolderItems(BaseModel):
    """
    Attributes:
        etag (Optional[str]): The HTTP `etag` of this file. This can be used within some API
                endpoints in the `If-Match` and `If-None-Match` headers to only
                perform changes on the file if (no) changes have happened.
        file_type (Optional[GetFolderItemsFileType]): `file`
        file_version (Optional[GetFolderItemsFileVersion]):
        folder_type (Optional[str]): Folder type Example: folder.
        id (Optional[str]): The unique identifier that represent a file.

                The ID for any file can be determined
                by visiting a file in the web application
                and copying the ID from the URL. For example,
                for the URL `https://*.app.box.com/files/123`
                the `file_id` is `123`.
        is_folder (Optional[bool]):  Example: True.
        name (Optional[str]): The name of the file
        sha1 (Optional[str]): The SHA1 hash of the file. This can be used to compare the contents
                of a file on Box with a local file.
        url (Optional[str]): The URL this web link points to
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    etag: Optional[str] = Field(alias="etag", default=None)
    file_type: Optional[GetFolderItemsFileType] = Field(alias="file_type", default=None)
    file_version: Optional["GetFolderItemsFileVersion"] = Field(
        alias="file_version", default=None
    )
    folder_type: Optional[str] = Field(alias="folder_type", default=None)
    id: Optional[str] = Field(alias="id", default=None)
    is_folder: Optional[bool] = Field(alias="isFolder", default=None)
    name: Optional[str] = Field(alias="name", default=None)
    sha1: Optional[str] = Field(alias="sha1", default=None)
    url: Optional[str] = Field(alias="url", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["GetFolderItems"], src_dict: Dict[str, Any]):
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
