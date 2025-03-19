from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.create_sign_request_response_signers_array_item_ref_signers_role import (
    CreateSignRequestResponseSignersArrayItemRefSignersRole,
)
from ..models.create_sign_request_response_signers_signer_decision import (
    CreateSignRequestResponseSignersSignerDecision,
)
from ..models.create_sign_request_response_signers_inputs_array_item_ref import (
    CreateSignRequestResponseSignersInputsArrayItemRef,
)


class CreateSignRequestResponseSignersArrayItemRef(BaseModel):
    """
    Attributes:
        email (Optional[str]): Email address of the signer
        embed_url (Optional[str]): URL to direct a signer to for signing
        embed_url_external_user_id (Optional[str]): User ID for the signer in an external application responsible
                for authentication when accessing the embed URL.
        has_viewed_document (Optional[bool]): Set to `true` if the signer views the document
        inputs (Optional[list['CreateSignRequestResponseSignersInputsArrayItemRef']]):
        is_in_person (Optional[bool]): Used in combination with an embed URL for a sender. After the
                sender signs, they will be redirected to the next `in_person` signer.
        order (Optional[int]): Order of the signer
        role (Optional[CreateSignRequestResponseSignersArrayItemRefSignersRole]): Defines the role of the signer in the
                sign request. A `signer`
                must sign the document and an `approver` must approve the document. A
                `final_copy_reader` only receives the final signed document and signing
                log.
        signer_decision (Optional[CreateSignRequestResponseSignersSignerDecision]):
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    email: Optional[str] = Field(alias="email", default=None)
    embed_url: Optional[str] = Field(alias="embed_url", default=None)
    embed_url_external_user_id: Optional[str] = Field(
        alias="embed_url_external_user_id", default=None
    )
    has_viewed_document: Optional[bool] = Field(
        alias="has_viewed_document", default=None
    )
    inputs: Optional[list["CreateSignRequestResponseSignersInputsArrayItemRef"]] = (
        Field(alias="inputs", default=None)
    )
    is_in_person: Optional[bool] = Field(alias="is_in_person", default=None)
    order: Optional[int] = Field(alias="order", default=None)
    role: Optional[CreateSignRequestResponseSignersArrayItemRefSignersRole] = Field(
        alias="role", default=None
    )
    signer_decision: Optional["CreateSignRequestResponseSignersSignerDecision"] = Field(
        alias="signer_decision", default=None
    )

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(
        cls: Type["CreateSignRequestResponseSignersArrayItemRef"],
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
