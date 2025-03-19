from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

import datetime


class CreateSignRequestRequestPrefillTagsArrayItemRef(BaseModel):
    """
    Attributes:
        checkbox_value (Optional[bool]): Checkbox prefill value
        date_value (Optional[datetime.datetime]): Date prefill value
        document_tag_id (Optional[str]): This references the ID of a specific tag contained in a file of the sign
                request.
        text_value (Optional[str]): Text prefill value
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    checkbox_value: Optional[bool] = Field(alias="checkbox_value", default=None)
    date_value: Optional[datetime.datetime] = Field(alias="date_value", default=None)
    document_tag_id: Optional[str] = Field(alias="document_tag_id", default=None)
    text_value: Optional[str] = Field(alias="text_value", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(
        cls: Type["CreateSignRequestRequestPrefillTagsArrayItemRef"],
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
