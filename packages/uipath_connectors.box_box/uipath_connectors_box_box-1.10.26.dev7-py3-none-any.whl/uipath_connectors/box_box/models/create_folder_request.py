from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.create_folder_request_sync_state import CreateFolderRequestSyncState
from ..models.create_folder_request_folder_upload_email import (
    CreateFolderRequestFolderUploadEmail,
)
from ..models.create_folder_request_parent import CreateFolderRequestParent


class CreateFolderRequest(BaseModel):
    """
    Attributes:
        name (str): The name of the folder.
        folder_upload_email (Optional[CreateFolderRequestFolderUploadEmail]):
        parent (Optional[CreateFolderRequestParent]):
        sync_state (Optional[CreateFolderRequestSyncState]): Specifies whether a folder should be synced to a
                user's device or not. This is used by Box Sync
                (discontinued) and is not used by Box Drive.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    name: str = Field(alias="name")
    folder_upload_email: Optional["CreateFolderRequestFolderUploadEmail"] = Field(
        alias="folder_upload_email", default=None
    )
    parent: Optional["CreateFolderRequestParent"] = Field(alias="parent", default=None)
    sync_state: Optional[CreateFolderRequestSyncState] = Field(
        alias="sync_state", default=None
    )

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["CreateFolderRequest"], src_dict: Dict[str, Any]):
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
