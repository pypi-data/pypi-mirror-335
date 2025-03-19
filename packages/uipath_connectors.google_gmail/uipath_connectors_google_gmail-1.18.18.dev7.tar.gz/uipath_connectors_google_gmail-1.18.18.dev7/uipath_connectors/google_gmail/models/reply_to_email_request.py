from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.reply_to_email_request_importance import ReplyToEmailRequestImportance


class ReplyToEmailRequest(BaseModel):
    """
    Attributes:
        reply_to (str): The email message to reply to Example: string.
        bcc (Optional[str]):  Example: string.
        body (Optional[str]): Body Example: string.
        cc (Optional[str]):  Example: string.
        importance (Optional[ReplyToEmailRequestImportance]): Importance of email Example: string.
        reply_to_all (Optional[bool]): Reply to all
        subject (Optional[str]):  Example: string.
        to (Optional[str]):  Example: string.
        thread_id (Optional[str]):  Example: 18572a181dfd50a3.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    reply_to: str = Field(alias="ReplyTo")
    bcc: Optional[str] = Field(alias="BCC", default=None)
    body: Optional[str] = Field(alias="Body", default=None)
    cc: Optional[str] = Field(alias="CC", default=None)
    importance: Optional[ReplyToEmailRequestImportance] = Field(
        alias="Importance", default=None
    )
    reply_to_all: Optional[bool] = Field(alias="ReplyToAll", default=None)
    subject: Optional[str] = Field(alias="Subject", default=None)
    to: Optional[str] = Field(alias="To", default=None)
    thread_id: Optional[str] = Field(alias="threadId", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["ReplyToEmailRequest"], src_dict: Dict[str, Any]):
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
