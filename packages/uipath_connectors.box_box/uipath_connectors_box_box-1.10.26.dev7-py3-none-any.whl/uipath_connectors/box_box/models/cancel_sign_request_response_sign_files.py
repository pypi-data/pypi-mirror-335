from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.cancel_sign_request_response_sign_files_files_array_item_ref import (
    CancelSignRequestResponseSignFilesFilesArrayItemRef,
)


class CancelSignRequestResponseSignFiles(BaseModel):
    """
    Attributes:
        files (Optional[list['CancelSignRequestResponseSignFilesFilesArrayItemRef']]):
        is_ready_for_download (Optional[bool]): Indicates whether the `sign_files` documents are processing
                and the PDFs may be out of date. A change to any document
                requires processing on all `sign_files`. We
                recommended waiting until processing is finished
                (and this value is true) before downloading the PDFs.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    files: Optional[list["CancelSignRequestResponseSignFilesFilesArrayItemRef"]] = (
        Field(alias="files", default=None)
    )
    is_ready_for_download: Optional[bool] = Field(
        alias="is_ready_for_download", default=None
    )

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(
        cls: Type["CancelSignRequestResponseSignFiles"], src_dict: Dict[str, Any]
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
