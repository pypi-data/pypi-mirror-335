from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type



class ArchiveEmailResponse(BaseModel):
    """
    Attributes:
        history_id (Optional[str]): Unique ID for tracking changes in the email. Example: 99759.
        id (Optional[str]): Unique ID representing the specific email message. Example: 1949140817e1249d.
        internal_date (Optional[str]): The timestamp when the email was received by Gmail. Example: 1737603707000.
        label_ids (Optional[list[str]]):  Example: Label_6094343900192509552.
        size_estimate (Optional[int]): Approximate size of the email in bytes. Example: 16484.0.
        snippet (Optional[str]): A short preview of the email content. Example: Config download.
        thread_id (Optional[str]): Unique ID representing the email thread. Example: 1949140817e1249d.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    history_id: Optional[str] = Field(alias="historyId", default=None)
    id: Optional[str] = Field(alias="id", default=None)
    internal_date: Optional[str] = Field(alias="internalDate", default=None)
    label_ids: Optional[list[str]] = Field(alias="labelIds", default=None)
    size_estimate: Optional[int] = Field(alias="sizeEstimate", default=None)
    snippet: Optional[str] = Field(alias="snippet", default=None)
    thread_id: Optional[str] = Field(alias="threadId", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["ArchiveEmailResponse"], src_dict: Dict[str, Any]):
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
