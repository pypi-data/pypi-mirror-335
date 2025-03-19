from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

import datetime


class TurnOnAutomaticRepliesResponse(BaseModel):
    """
    Attributes:
        enable_auto_reply (Optional[bool]): Toggle to turn the automatic reply feature on or off.
        end_time (Optional[datetime.datetime]): The date and time when automatic replies will stop. Example: 1737527373.
        response_body_plain_text (Optional[str]): The text content of the automatic reply.
        response_subject (Optional[str]): The subject line used for the automatic reply email.
        restrict_to_contacts (Optional[bool]): Limit automatic replies to only those in your contacts list.
        restrict_to_domain (Optional[bool]): Send automatic replies to recipients outside your domain.
        start_time (Optional[datetime.datetime]): The date and time when automatic replies will begin. Example:
                1737527373.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    enable_auto_reply: Optional[bool] = Field(alias="enableAutoReply", default=None)
    end_time: Optional[datetime.datetime] = Field(alias="endTime", default=None)
    response_body_plain_text: Optional[str] = Field(
        alias="responseBodyPlainText", default=None
    )
    response_subject: Optional[str] = Field(alias="responseSubject", default=None)
    restrict_to_contacts: Optional[bool] = Field(
        alias="restrictToContacts", default=None
    )
    restrict_to_domain: Optional[bool] = Field(alias="restrictToDomain", default=None)
    start_time: Optional[datetime.datetime] = Field(alias="startTime", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(
        cls: Type["TurnOnAutomaticRepliesResponse"], src_dict: Dict[str, Any]
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
