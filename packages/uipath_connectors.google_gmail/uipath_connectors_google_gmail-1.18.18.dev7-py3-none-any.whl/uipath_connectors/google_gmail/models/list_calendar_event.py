from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.list_calendar_event_attendees_array_item_ref import (
    ListCalendarEventAttendeesArrayItemRef,
)


class ListCalendarEvent(BaseModel):
    """
    Attributes:
        all_day (Optional[bool]):
        attendees (Optional[list['ListCalendarEventAttendeesArrayItemRef']]):
        calendar_id (Optional[str]):  Example: primary.
        calendar_name (Optional[str]):  Example: primary.
        description (Optional[str]):  Example: string.
        has_attachments (Optional[bool]):
        id (Optional[str]):  Example: tet6ea1ot1cc43lhru71vsr6hk.
        title (Optional[str]):  Example: New.
        self_organizer (Optional[bool]):  Example: True.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    all_day: Optional[bool] = Field(alias="AllDay", default=None)
    attendees: Optional[list["ListCalendarEventAttendeesArrayItemRef"]] = Field(
        alias="Attendees", default=None
    )
    calendar_id: Optional[str] = Field(alias="CalendarID", default=None)
    calendar_name: Optional[str] = Field(alias="CalendarName", default=None)
    description: Optional[str] = Field(alias="Description", default=None)
    has_attachments: Optional[bool] = Field(alias="HasAttachments", default=None)
    id: Optional[str] = Field(alias="ID", default=None)
    title: Optional[str] = Field(alias="Title", default=None)
    self_organizer: Optional[bool] = Field(alias="selfOrganizer", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["ListCalendarEvent"], src_dict: Dict[str, Any]):
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
