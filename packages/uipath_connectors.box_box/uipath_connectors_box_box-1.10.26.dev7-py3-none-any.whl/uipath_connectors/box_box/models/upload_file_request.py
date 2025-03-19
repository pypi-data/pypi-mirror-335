from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

import datetime
from ..models.upload_file_request_parent import UploadFileRequestParent


class UploadFileRequest(BaseModel):
    """
    Attributes:
        content_created_at (Optional[datetime.datetime]): The date and time at which this file was originally
                created, which might be before it was uploaded to Box.
        content_modified_at (Optional[datetime.datetime]): The date and time at which this file was last updated,
                which might be before it was uploaded to Box.
        name (Optional[str]): The name of the file
        parent (Optional[UploadFileRequestParent]):
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    content_created_at: Optional[datetime.datetime] = Field(
        alias="content_created_at", default=None
    )
    content_modified_at: Optional[datetime.datetime] = Field(
        alias="content_modified_at", default=None
    )
    name: Optional[str] = Field(alias="name", default=None)
    parent: Optional["UploadFileRequestParent"] = Field(alias="parent", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["UploadFileRequest"], src_dict: Dict[str, Any]):
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
