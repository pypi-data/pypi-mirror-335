from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type


class GetCalendarList(BaseModel):
    """
    Attributes:
        full_name (Optional[str]): The Full name Example: My Calendars.
        id (Optional[str]): The ID Example: me.
        reference_id (Optional[str]): The Reference ID Example: me.
        selectable (Optional[bool]): The Selectable
        time_zone (Optional[str]): The Time zone Example: Asia/Kolkata.
        type_ (Optional[str]): The Type Example: folder.
        is_folder (Optional[bool]): The Is folder Example: True.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    full_name: Optional[str] = Field(alias="FullName", default=None)
    id: Optional[str] = Field(alias="ID", default=None)
    reference_id: Optional[str] = Field(alias="ReferenceID", default=None)
    selectable: Optional[bool] = Field(alias="Selectable", default=None)
    time_zone: Optional[str] = Field(alias="TimeZone", default=None)
    type_: Optional[str] = Field(alias="Type", default=None)
    is_folder: Optional[bool] = Field(alias="isFolder", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["GetCalendarList"], src_dict: Dict[str, Any]):
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
