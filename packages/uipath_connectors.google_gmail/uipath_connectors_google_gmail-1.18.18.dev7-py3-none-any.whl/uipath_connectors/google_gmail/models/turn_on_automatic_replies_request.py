from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

import datetime


class TurnOnAutomaticRepliesRequest(BaseModel):
    """
    Attributes:
        response_subject (str): The subject line used for the automatic reply email.
        end_time (Optional[datetime.datetime]): The date and time when automatic replies will stop. Example: 1737527373.
        response_body_plain_text (Optional[str]): The text content of the automatic reply.
        restrict_to_contacts (Optional[bool]): Limit automatic replies to only those in your contacts list.
        send_replies_outside_domain (Optional[bool]): Sends replies to user who are outside users domain.
        start_time (Optional[datetime.datetime]): The date and time when automatic replies will begin. Example:
                1737527373.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    response_subject: str = Field(alias="responseSubject")
    end_time: Optional[datetime.datetime] = Field(alias="endTime", default=None)
    response_body_plain_text: Optional[str] = Field(
        alias="responseBodyPlainText", default=None
    )
    restrict_to_contacts: Optional[bool] = Field(
        alias="restrictToContacts", default=None
    )
    send_replies_outside_domain: Optional[bool] = Field(
        alias="sendRepliesOutsideDomain", default=None
    )
    start_time: Optional[datetime.datetime] = Field(alias="startTime", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["TurnOnAutomaticRepliesRequest"], src_dict: Dict[str, Any]):
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
