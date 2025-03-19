from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.create_folder_response_item_status import CreateFolderResponseItemStatus
from ..models.create_folder_response_type import CreateFolderResponseType
import datetime
from ..models.create_folder_response_owned_by import CreateFolderResponseOwnedBy
from ..models.create_folder_response_created_by import CreateFolderResponseCreatedBy
from ..models.create_folder_response_shared_link import CreateFolderResponseSharedLink
from ..models.create_folder_response_folder_upload_email import (
    CreateFolderResponseFolderUploadEmail,
)
from ..models.create_folder_response_parent import CreateFolderResponseParent
from ..models.create_folder_response_item_collection import (
    CreateFolderResponseItemCollection,
)
from ..models.create_folder_response_modified_by import CreateFolderResponseModifiedBy
from ..models.create_folder_response_path_collection import (
    CreateFolderResponsePathCollection,
)


class CreateFolderResponse(BaseModel):
    """
    Attributes:
        content_created_at (Optional[datetime.datetime]): The date and time at which this folder was originally
                created.
        content_modified_at (Optional[datetime.datetime]): The date and time at which this folder was last updated.
        created_at (Optional[datetime.datetime]): The date and time when the folder was created. This value may
                be `null` for some folders such as the root folder or the trash
                folder.
        created_by (Optional[CreateFolderResponseCreatedBy]):
        etag (Optional[str]): The HTTP `etag` of this folder. This can be used within some API
                endpoints in the `If-Match` and `If-None-Match` headers to only
                perform changes on the folder if (no) changes have happened.
        expires_at (Optional[datetime.datetime]): The time and which the folder will be automatically be deleted.
        folder_upload_email (Optional[CreateFolderResponseFolderUploadEmail]):
        id (Optional[str]): The unique identifier that represent a folder.

                The ID for any folder can be determined
                by visiting a folder in the web application
                and copying the ID from the URL. For example,
                for the URL `https://*.app.box.com/folders/123`
                the `folder_id` is `123`.
        item_collection (Optional[CreateFolderResponseItemCollection]):
        item_status (Optional[CreateFolderResponseItemStatus]): Defines if this item has been deleted or not.

                * `active` when the item has is not in the trash
                * `trashed` when the item has been moved to the trash but not deleted
                * `deleted` when the item has been permanently deleted.
        modified_at (Optional[datetime.datetime]): The date and time when the folder was last updated. This value may
                be `null` for some folders such as the root folder or the trash
                folder.
        modified_by (Optional[CreateFolderResponseModifiedBy]):
        name (Optional[str]): The name of the folder.
        owned_by (Optional[CreateFolderResponseOwnedBy]):
        parent (Optional[CreateFolderResponseParent]):
        path_collection (Optional[CreateFolderResponsePathCollection]):
        purged_at (Optional[datetime.datetime]): The time at which this folder is expected to be purged
                from the trash.
        shared_link (Optional[CreateFolderResponseSharedLink]):
        size (Optional[int]): The folder size in bytes.

                Be careful parsing this integer as its
                value can get very large.
        trashed_at (Optional[datetime.datetime]): The time at which this folder was put in the trash.
        type_ (Optional[CreateFolderResponseType]): `folder`
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    content_created_at: Optional[datetime.datetime] = Field(
        alias="content_created_at", default=None
    )
    content_modified_at: Optional[datetime.datetime] = Field(
        alias="content_modified_at", default=None
    )
    created_at: Optional[datetime.datetime] = Field(alias="created_at", default=None)
    created_by: Optional["CreateFolderResponseCreatedBy"] = Field(
        alias="created_by", default=None
    )
    etag: Optional[str] = Field(alias="etag", default=None)
    expires_at: Optional[datetime.datetime] = Field(alias="expires_at", default=None)
    folder_upload_email: Optional["CreateFolderResponseFolderUploadEmail"] = Field(
        alias="folder_upload_email", default=None
    )
    id: Optional[str] = Field(alias="id", default=None)
    item_collection: Optional["CreateFolderResponseItemCollection"] = Field(
        alias="item_collection", default=None
    )
    item_status: Optional[CreateFolderResponseItemStatus] = Field(
        alias="item_status", default=None
    )
    modified_at: Optional[datetime.datetime] = Field(alias="modified_at", default=None)
    modified_by: Optional["CreateFolderResponseModifiedBy"] = Field(
        alias="modified_by", default=None
    )
    name: Optional[str] = Field(alias="name", default=None)
    owned_by: Optional["CreateFolderResponseOwnedBy"] = Field(
        alias="owned_by", default=None
    )
    parent: Optional["CreateFolderResponseParent"] = Field(alias="parent", default=None)
    path_collection: Optional["CreateFolderResponsePathCollection"] = Field(
        alias="path_collection", default=None
    )
    purged_at: Optional[datetime.datetime] = Field(alias="purged_at", default=None)
    shared_link: Optional["CreateFolderResponseSharedLink"] = Field(
        alias="shared_link", default=None
    )
    size: Optional[int] = Field(alias="size", default=None)
    trashed_at: Optional[datetime.datetime] = Field(alias="trashed_at", default=None)
    type_: Optional[CreateFolderResponseType] = Field(alias="type", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["CreateFolderResponse"], src_dict: Dict[str, Any]):
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
