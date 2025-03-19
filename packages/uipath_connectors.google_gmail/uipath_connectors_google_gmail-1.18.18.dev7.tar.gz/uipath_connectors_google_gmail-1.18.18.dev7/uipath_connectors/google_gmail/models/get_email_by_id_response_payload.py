from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.get_email_by_id_response_payload_body import (
    GetEmailByIDResponsePayloadBody,
)
from ..models.get_email_by_id_response_payload_parts_array_item_ref import (
    GetEmailByIDResponsePayloadPartsArrayItemRef,
)
from ..models.get_email_by_id_response_payload_headers_array_item_ref import (
    GetEmailByIDResponsePayloadHeadersArrayItemRef,
)


class GetEmailByIDResponsePayload(BaseModel):
    """
    Attributes:
        body (Optional[GetEmailByIDResponsePayloadBody]):
        filename (Optional[str]):
        headers (Optional[list['GetEmailByIDResponsePayloadHeadersArrayItemRef']]):
        mime_type (Optional[str]):
        part_id (Optional[str]):
        parts (Optional[list['GetEmailByIDResponsePayloadPartsArrayItemRef']]):
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    body: Optional["GetEmailByIDResponsePayloadBody"] = Field(
        alias="body", default=None
    )
    filename: Optional[str] = Field(alias="filename", default=None)
    headers: Optional[list["GetEmailByIDResponsePayloadHeadersArrayItemRef"]] = Field(
        alias="headers", default=None
    )
    mime_type: Optional[str] = Field(alias="mimeType", default=None)
    part_id: Optional[str] = Field(alias="partId", default=None)
    parts: Optional[list["GetEmailByIDResponsePayloadPartsArrayItemRef"]] = Field(
        alias="parts", default=None
    )

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["GetEmailByIDResponsePayload"], src_dict: Dict[str, Any]):
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
