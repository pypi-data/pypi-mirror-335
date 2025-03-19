from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type


class GetSingleLabelByIDResponse(BaseModel):
    """
    Attributes:
        display_name (Optional[str]): The name of the folder as shown in the user interface. Example: INBOX.
        id (Optional[str]): The unique identifier for the folder. Example: CHAT.
        label_list_visibility (Optional[str]): Indicates if the label is visible in the label list. Example: labelShow.
        message_list_visibility (Optional[str]): Indicates if messages are visible in the folder's message list.
                Example: show.
        messages_total (Optional[int]): The total count of messages within the folder. Example: 3202.0.
        messages_unread (Optional[int]): The total number of unread messages within the folder. Example: 3079.0.
        name (Optional[str]): The unique identifier name of the folder used by the system. Example: INBOX.
        threads_total (Optional[int]): The total count of email threads within the folder. Example: 3136.0.
        threads_unread (Optional[int]): The total number of unread conversation threads within the folder. Example:
                3031.0.
        type_ (Optional[str]): The type of the folder, such as inbox, sent, etc. Example: system.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    display_name: Optional[str] = Field(alias="displayName", default=None)
    id: Optional[str] = Field(alias="id", default=None)
    label_list_visibility: Optional[str] = Field(
        alias="labelListVisibility", default=None
    )
    message_list_visibility: Optional[str] = Field(
        alias="messageListVisibility", default=None
    )
    messages_total: Optional[int] = Field(alias="messagesTotal", default=None)
    messages_unread: Optional[int] = Field(alias="messagesUnread", default=None)
    name: Optional[str] = Field(alias="name", default=None)
    threads_total: Optional[int] = Field(alias="threadsTotal", default=None)
    threads_unread: Optional[int] = Field(alias="threadsUnread", default=None)
    type_: Optional[str] = Field(alias="type", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["GetSingleLabelByIDResponse"], src_dict: Dict[str, Any]):
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
