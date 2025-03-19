from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.copy_file_request_parent import CopyFileRequestParent


class CopyFileRequest(BaseModel):
    """
    Attributes:
        name (Optional[str]): The name of the file
        parent (Optional[CopyFileRequestParent]):
        version (Optional[str]): An optional ID of the specific file version to copy.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    name: Optional[str] = Field(alias="name", default=None)
    parent: Optional["CopyFileRequestParent"] = Field(alias="parent", default=None)
    version: Optional[str] = Field(alias="version", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["CopyFileRequest"], src_dict: Dict[str, Any]):
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
