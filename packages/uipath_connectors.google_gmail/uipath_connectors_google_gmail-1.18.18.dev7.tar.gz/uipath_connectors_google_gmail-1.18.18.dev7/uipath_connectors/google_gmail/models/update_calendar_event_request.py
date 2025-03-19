from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.update_calendar_event_request_show_as import (
    UpdateCalendarEventRequestShowAs,
)
from ..models.update_calendar_event_request_visibility import (
    UpdateCalendarEventRequestVisibility,
)
import datetime


class UpdateCalendarEventRequest(BaseModel):
    """
    Attributes:
        all_day_event (Optional[bool]):
        can_invite_others (Optional[bool]):
        can_modify_event (Optional[bool]):
        can_see_attendees_list (Optional[bool]):
        description (Optional[str]):  Example: string.
        end_date_time (Optional[datetime.datetime]):  Example: 2023-01-02T06:35:28.6310000+00:00.
        event_title (Optional[str]): The new name of the event. If left blank, the existing value will not be updated.
                Example: string.
        location (Optional[str]):  Example: string.
        optional_attendees (Optional[str]):  Example: string.
        output_event_timezone (Optional[str]):  Example: string.
        required_attendees (Optional[str]):  Example: string.
        resource_attendees (Optional[str]):  Example: string.
        show_as (Optional[UpdateCalendarEventRequestShowAs]): Show as Example: string.
        start_date_time (Optional[datetime.datetime]):  Example: 2023-01-02T06:35:28.6310000+00:00.
        timezone (Optional[str]):  Example: string.
        visibility (Optional[UpdateCalendarEventRequestVisibility]): Visibility of the event. Example: string.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    all_day_event: Optional[bool] = Field(alias="AllDayEvent", default=None)
    can_invite_others: Optional[bool] = Field(alias="CanInviteOthers", default=None)
    can_modify_event: Optional[bool] = Field(alias="CanModifyEvent", default=None)
    can_see_attendees_list: Optional[bool] = Field(
        alias="CanSeeAttendeesList", default=None
    )
    description: Optional[str] = Field(alias="Description", default=None)
    end_date_time: Optional[datetime.datetime] = Field(
        alias="EndDateTime", default=None
    )
    event_title: Optional[str] = Field(alias="EventTitle", default=None)
    location: Optional[str] = Field(alias="Location", default=None)
    optional_attendees: Optional[str] = Field(alias="OptionalAttendees", default=None)
    output_event_timezone: Optional[str] = Field(
        alias="OutputEventTimezone", default=None
    )
    required_attendees: Optional[str] = Field(alias="RequiredAttendees", default=None)
    resource_attendees: Optional[str] = Field(alias="ResourceAttendees", default=None)
    show_as: Optional[UpdateCalendarEventRequestShowAs] = Field(
        alias="ShowAs", default=None
    )
    start_date_time: Optional[datetime.datetime] = Field(
        alias="StartDateTime", default=None
    )
    timezone: Optional[str] = Field(alias="Timezone", default=None)
    visibility: Optional[UpdateCalendarEventRequestVisibility] = Field(
        alias="Visibility", default=None
    )

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["UpdateCalendarEventRequest"], src_dict: Dict[str, Any]):
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
