from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.create_calendar_event_response_show_as import (
    CreateCalendarEventResponseShowAs,
)
from ..models.create_calendar_event_response_visibility import (
    CreateCalendarEventResponseVisibility,
)
import datetime
from ..models.create_calendar_event_response_reminders import (
    CreateCalendarEventResponseReminders,
)
from ..models.create_calendar_event_response_end import CreateCalendarEventResponseEnd
from ..models.create_calendar_event_response_organizer import (
    CreateCalendarEventResponseOrganizer,
)
from ..models.create_calendar_event_response_creator import (
    CreateCalendarEventResponseCreator,
)
from ..models.create_calendar_event_response_start import (
    CreateCalendarEventResponseStart,
)


class CreateCalendarEventResponse(BaseModel):
    """
    Attributes:
        show_as (Optional[CreateCalendarEventResponseShowAs]): Show as Example: string.
        visibility (Optional[CreateCalendarEventResponseVisibility]): Visibility of the event. Example: string.
        created (Optional[datetime.datetime]):  Example: 2023-01-02T04:49:58.0000000+00:00.
        creator (Optional[CreateCalendarEventResponseCreator]):
        end (Optional[CreateCalendarEventResponseEnd]):
        etag (Optional[str]):  Example: "3345269997634000".
        event_type (Optional[str]):  Example: default.
        html_link (Optional[str]):  Example:
                https://www.google.com/calendar/event?eid=dGV0NmVhMW90MWNjNDNsaHJ1NzF2c3I2aGsgdGVzdGNsb3VkMTU1QG0.
        i_cal_uid (Optional[str]):  Example: tet6ea1ot1cc43lhru71vsr6hk@google.com.
        id (Optional[str]):  Example: tet6ea1ot1cc43lhru71vsr6hk.
        kind (Optional[str]):  Example: calendar#event.
        organizer (Optional[CreateCalendarEventResponseOrganizer]):
        reminders (Optional[CreateCalendarEventResponseReminders]):
        sequence (Optional[int]):  Example: 0.0.
        start (Optional[CreateCalendarEventResponseStart]):
        status (Optional[str]):  Example: confirmed.
        summary (Optional[str]):  Example: New.
        updated (Optional[datetime.datetime]):  Example: 2023-01-02T04:49:58.8170000+00:00.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    show_as: Optional[CreateCalendarEventResponseShowAs] = Field(
        alias="ShowAs", default=None
    )
    visibility: Optional[CreateCalendarEventResponseVisibility] = Field(
        alias="Visibility", default=None
    )
    created: Optional[datetime.datetime] = Field(alias="created", default=None)
    creator: Optional["CreateCalendarEventResponseCreator"] = Field(
        alias="creator", default=None
    )
    end: Optional["CreateCalendarEventResponseEnd"] = Field(alias="end", default=None)
    etag: Optional[str] = Field(alias="etag", default=None)
    event_type: Optional[str] = Field(alias="eventType", default=None)
    html_link: Optional[str] = Field(alias="htmlLink", default=None)
    i_cal_uid: Optional[str] = Field(alias="iCalUID", default=None)
    id: Optional[str] = Field(alias="id", default=None)
    kind: Optional[str] = Field(alias="kind", default=None)
    organizer: Optional["CreateCalendarEventResponseOrganizer"] = Field(
        alias="organizer", default=None
    )
    reminders: Optional["CreateCalendarEventResponseReminders"] = Field(
        alias="reminders", default=None
    )
    sequence: Optional[int] = Field(alias="sequence", default=None)
    start: Optional["CreateCalendarEventResponseStart"] = Field(
        alias="start", default=None
    )
    status: Optional[str] = Field(alias="status", default=None)
    summary: Optional[str] = Field(alias="summary", default=None)
    updated: Optional[datetime.datetime] = Field(alias="updated", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["CreateCalendarEventResponse"], src_dict: Dict[str, Any]):
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
