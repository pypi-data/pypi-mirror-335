from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type


class TurnOffAutomaticRepliesResponse(BaseModel):
    """
    Attributes:
        enable_auto_reply (Optional[bool]): Indicates if automatic replies are currently enabled.
        response_subject (Optional[str]): The subject line used in automatic reply emails.
        restrict_to_contacts (Optional[bool]): Limits automatic replies to only your contacts.
        restrict_to_domain (Optional[bool]): Limits automatic replies to recipients within your domain.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    enable_auto_reply: Optional[bool] = Field(alias="enableAutoReply", default=None)
    response_subject: Optional[str] = Field(alias="responseSubject", default=None)
    restrict_to_contacts: Optional[bool] = Field(
        alias="restrictToContacts", default=None
    )
    restrict_to_domain: Optional[bool] = Field(alias="restrictToDomain", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(
        cls: Type["TurnOffAutomaticRepliesResponse"], src_dict: Dict[str, Any]
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
