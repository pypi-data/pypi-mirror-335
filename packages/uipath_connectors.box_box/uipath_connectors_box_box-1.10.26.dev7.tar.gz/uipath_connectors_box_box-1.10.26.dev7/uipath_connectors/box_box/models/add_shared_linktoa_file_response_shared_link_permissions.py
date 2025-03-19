from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type


class AddSharedLinktoaFileResponseSharedLinkPermissions(BaseModel):
    """
    Attributes:
        can_download (Optional[bool]): Defines if the shared link allows for the item to be downloaded. For
                shared links on folders, this also applies to any items in the folder.

                This value can be set to `true` when the effective access level is
                set to `open` or `company`, not `collaborators`.
        can_preview (Optional[bool]): Defines if the shared link allows for the item to be previewed.

                This value is always `true`. For shared links on folders this also
                applies to any items in the folder.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    can_download: Optional[bool] = Field(alias="can_download", default=None)
    can_preview: Optional[bool] = Field(alias="can_preview", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(
        cls: Type["AddSharedLinktoaFileResponseSharedLinkPermissions"],
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
