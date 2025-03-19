from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.copy_file_response_shared_link_shared_link_access import (
    CopyFileResponseSharedLinkSharedLinkAccess,
)
from ..models.copy_file_response_shared_link_shared_link_effective_access import (
    CopyFileResponseSharedLinkSharedLinkEffectiveAccess,
)
from ..models.copy_file_response_shared_link_shared_link_effective_permission import (
    CopyFileResponseSharedLinkSharedLinkEffectivePermission,
)
import datetime
from ..models.copy_file_response_shared_link_permissions import (
    CopyFileResponseSharedLinkPermissions,
)


class CopyFileResponseSharedLink(BaseModel):
    """
    Attributes:
        access (Optional[CopyFileResponseSharedLinkSharedLinkAccess]): The access level for this shared link.

                * `open` - provides access to this item to anyone with this link
                * `company` - only provides access to this item to people the same company
                * `collaborators` - only provides access to this item to people who are
                   collaborators on this item

                If this field is omitted when creating the shared link, the access level
                will be set to the default access level specified by the enterprise admin.
        download_count (Optional[int]): The number of times this item has been downloaded.
        download_url (Optional[str]): A URL that can be used to download the file. This URL can be used in
                a browser to download the file. This URL includes the file
                extension so that the file will be saved with the right file type.

                This property will be `null` for folders.
        effective_access (Optional[CopyFileResponseSharedLinkSharedLinkEffectiveAccess]): The effective access level for
                the shared link. This can be a more
                restrictive access level than the value in the `access` field when the
                enterprise settings restrict the allowed access levels.
        effective_permission (Optional[CopyFileResponseSharedLinkSharedLinkEffectivePermission]): The effective
                permissions for this shared link.
        is_password_enabled (Optional[bool]): Defines if the shared link requires a password to access the item.
        permissions (Optional[CopyFileResponseSharedLinkPermissions]):
        preview_count (Optional[int]): The number of times this item has been previewed.
        unshared_at (Optional[datetime.datetime]): The date and time when this link will be unshared. This field can
                only be
                set by users with paid accounts.
        url (Optional[str]): The URL that can be used to access the item on Box.

                This URL will display the item in Box's preview UI where the file
                can be downloaded if allowed.

                This URL will continue to work even when a custom `vanity_url`
                has been set for this shared link.
        vanity_name (Optional[str]): The custom name of a shared link, as used in the `vanity_url` field.
        vanity_url (Optional[str]): The "Custom URL" that can also be used to preview the item on Box.  Custom
                URLs can only be created or modified in the Box Web application.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    access: Optional[CopyFileResponseSharedLinkSharedLinkAccess] = Field(
        alias="access", default=None
    )
    download_count: Optional[int] = Field(alias="download_count", default=None)
    download_url: Optional[str] = Field(alias="download_url", default=None)
    effective_access: Optional[CopyFileResponseSharedLinkSharedLinkEffectiveAccess] = (
        Field(alias="effective_access", default=None)
    )
    effective_permission: Optional[
        CopyFileResponseSharedLinkSharedLinkEffectivePermission
    ] = Field(alias="effective_permission", default=None)
    is_password_enabled: Optional[bool] = Field(
        alias="is_password_enabled", default=None
    )
    permissions: Optional["CopyFileResponseSharedLinkPermissions"] = Field(
        alias="permissions", default=None
    )
    preview_count: Optional[int] = Field(alias="preview_count", default=None)
    unshared_at: Optional[datetime.datetime] = Field(alias="unshared_at", default=None)
    url: Optional[str] = Field(alias="url", default=None)
    vanity_name: Optional[str] = Field(alias="vanity_name", default=None)
    vanity_url: Optional[str] = Field(alias="vanity_url", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["CopyFileResponseSharedLink"], src_dict: Dict[str, Any]):
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
