from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.copy_file_response_path_collection_entries_array_item_ref_path_collection_entries_type import (
    CopyFileResponsePathCollectionEntriesArrayItemRefPathCollectionEntriesType,
)


class CopyFileResponsePathCollectionEntriesArrayItemRef(BaseModel):
    """
    Attributes:
        etag (Optional[str]): The HTTP `etag` of this folder. This can be used within some API
                endpoints in the `If-Match` and `If-None-Match` headers to only
                perform changes on the folder if (no) changes have happened.
        id (Optional[str]): The unique identifier that represent a folder.

                The ID for any folder can be determined
                by visiting a folder in the web application
                and copying the ID from the URL. For example,
                for the URL `https://*.app.box.com/folders/123`
                the `folder_id` is `123`.
        name (Optional[str]): The name of the folder.
        type_ (Optional[CopyFileResponsePathCollectionEntriesArrayItemRefPathCollectionEntriesType]): `folder`
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    etag: Optional[str] = Field(alias="etag", default=None)
    id: Optional[str] = Field(alias="id", default=None)
    name: Optional[str] = Field(alias="name", default=None)
    type_: Optional[
        CopyFileResponsePathCollectionEntriesArrayItemRefPathCollectionEntriesType
    ] = Field(alias="type", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(
        cls: Type["CopyFileResponsePathCollectionEntriesArrayItemRef"],
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
