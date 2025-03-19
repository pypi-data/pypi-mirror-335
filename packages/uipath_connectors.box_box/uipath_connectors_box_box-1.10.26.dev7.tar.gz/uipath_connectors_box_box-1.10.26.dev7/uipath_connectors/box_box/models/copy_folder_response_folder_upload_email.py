from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.copy_folder_response_folder_upload_email_folder_upload_email_access import (
    CopyFolderResponseFolderUploadEmailFolderUploadEmailAccess,
)


class CopyFolderResponseFolderUploadEmail(BaseModel):
    """
    Attributes:
        access (Optional[CopyFolderResponseFolderUploadEmailFolderUploadEmailAccess]): When this parameter has been set,
                users can email files
                to the email address that has been automatically
                created for this folder.

                To create an email address, set this property either when
                creating or updating the folder.

                When set to `collaborators`, only emails from registered email
                addresses for collaborators will be accepted. This includes
                any email aliases a user might have registered.

                When set to `open` it will accept emails from any email
                address.
        email (Optional[str]): The optional upload email address for this folder.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    access: Optional[CopyFolderResponseFolderUploadEmailFolderUploadEmailAccess] = (
        Field(alias="access", default=None)
    )
    email: Optional[str] = Field(alias="email", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(
        cls: Type["CopyFolderResponseFolderUploadEmail"], src_dict: Dict[str, Any]
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
