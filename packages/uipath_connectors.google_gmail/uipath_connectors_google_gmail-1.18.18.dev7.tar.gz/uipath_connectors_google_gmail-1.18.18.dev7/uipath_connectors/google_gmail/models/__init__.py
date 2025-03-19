"""Contains all the data models used in inputs/outputs"""

from .apply_gmail_label_request import ApplyGmailLabelRequest
from .apply_gmail_label_response import ApplyGmailLabelResponse
from .archive_email_response import ArchiveEmailResponse
from .create_calendar_event_request import CreateCalendarEventRequest
from .create_calendar_event_request_show_as import CreateCalendarEventRequestShowAs
from .create_calendar_event_request_visibility import (
    CreateCalendarEventRequestVisibility,
)
from .create_calendar_event_response import CreateCalendarEventResponse
from .create_calendar_event_response_creator import CreateCalendarEventResponseCreator
from .create_calendar_event_response_end import CreateCalendarEventResponseEnd
from .create_calendar_event_response_organizer import (
    CreateCalendarEventResponseOrganizer,
)
from .create_calendar_event_response_reminders import (
    CreateCalendarEventResponseReminders,
)
from .create_calendar_event_response_show_as import CreateCalendarEventResponseShowAs
from .create_calendar_event_response_start import CreateCalendarEventResponseStart
from .create_calendar_event_response_visibility import (
    CreateCalendarEventResponseVisibility,
)
from .default_error import DefaultError
from .delete_email_response import DeleteEmailResponse
from .forward_mail_response import ForwardMailResponse
from .get_calendar_list import GetCalendarList
from .get_email_by_id_format import GetEmailByIDFormat
from .get_email_by_id_response import GetEmailByIDResponse
from .get_email_by_id_response_payload import GetEmailByIDResponsePayload
from .get_email_by_id_response_payload_body import GetEmailByIDResponsePayloadBody
from .get_email_by_id_response_payload_headers_array_item_ref import (
    GetEmailByIDResponsePayloadHeadersArrayItemRef,
)
from .get_email_by_id_response_payload_parts_array_item_ref import (
    GetEmailByIDResponsePayloadPartsArrayItemRef,
)
from .get_email_by_id_response_payload_parts_body import (
    GetEmailByIDResponsePayloadPartsBody,
)
from .get_email_by_id_response_payload_parts_headers_array_item_ref import (
    GetEmailByIDResponsePayloadPartsHeadersArrayItemRef,
)
from .get_email_labels import GetEmailLabels
from .get_single_label_by_id_response import GetSingleLabelByIDResponse
from .list_calendar_event import ListCalendarEvent
from .list_calendar_event_attendees_array_item_ref import (
    ListCalendarEventAttendeesArrayItemRef,
)
from .list_email import ListEmail
from .list_email_bcc_array_item_ref import ListEmailBCCArrayItemRef
from .list_email_categories_array_item_ref import ListEmailCategoriesArrayItemRef
from .list_email_categories_array_item_ref_category_id import (
    ListEmailCategoriesArrayItemRefCategoryId,
)
from .list_email_categories_array_item_ref_category_name import (
    ListEmailCategoriesArrayItemRefCategoryName,
)
from .list_email_cc_array_item_ref import ListEmailCCArrayItemRef
from .list_email_from import ListEmailFrom
from .list_email_parent_folders_array_item_ref import ListEmailParentFoldersArrayItemRef
from .list_email_to_array_item_ref import ListEmailToArrayItemRef
from .list_email_type import ListEmailType
from .mark_email_read_unread_response import MarkEmailReadUnreadResponse
from .move_email_response import MoveEmailResponse
from .remove_gmail_label_request import RemoveGmailLabelRequest
from .remove_gmail_label_response import RemoveGmailLabelResponse
from .reply_to_email_body import ReplyToEmailBody
from .reply_to_email_request import ReplyToEmailRequest
from .reply_to_email_request_importance import ReplyToEmailRequestImportance
from .reply_to_email_response import ReplyToEmailResponse
from .reply_to_email_response_importance import ReplyToEmailResponseImportance
from .send_email_body import SendEmailBody
from .send_email_request import SendEmailRequest
from .send_email_request_importance import SendEmailRequestImportance
from .send_email_response import SendEmailResponse
from .send_email_response_importance import SendEmailResponseImportance
from .turn_off_automatic_replies_response import TurnOffAutomaticRepliesResponse
from .turn_on_automatic_replies_request import TurnOnAutomaticRepliesRequest
from .turn_on_automatic_replies_response import TurnOnAutomaticRepliesResponse
from .update_calendar_event_request import UpdateCalendarEventRequest
from .update_calendar_event_request_show_as import UpdateCalendarEventRequestShowAs
from .update_calendar_event_request_visibility import (
    UpdateCalendarEventRequestVisibility,
)
from .update_calendar_event_response import UpdateCalendarEventResponse
from .update_calendar_event_response_creator import UpdateCalendarEventResponseCreator
from .update_calendar_event_response_end import UpdateCalendarEventResponseEnd
from .update_calendar_event_response_organizer import (
    UpdateCalendarEventResponseOrganizer,
)
from .update_calendar_event_response_reminders import (
    UpdateCalendarEventResponseReminders,
)
from .update_calendar_event_response_show_as import UpdateCalendarEventResponseShowAs
from .update_calendar_event_response_start import UpdateCalendarEventResponseStart
from .update_calendar_event_response_visibility import (
    UpdateCalendarEventResponseVisibility,
)

__all__ = (
    "ApplyGmailLabelRequest",
    "ApplyGmailLabelResponse",
    "ArchiveEmailResponse",
    "CreateCalendarEventRequest",
    "CreateCalendarEventRequestShowAs",
    "CreateCalendarEventRequestVisibility",
    "CreateCalendarEventResponse",
    "CreateCalendarEventResponseCreator",
    "CreateCalendarEventResponseEnd",
    "CreateCalendarEventResponseOrganizer",
    "CreateCalendarEventResponseReminders",
    "CreateCalendarEventResponseShowAs",
    "CreateCalendarEventResponseStart",
    "CreateCalendarEventResponseVisibility",
    "DefaultError",
    "DeleteEmailResponse",
    "ForwardMailResponse",
    "GetCalendarList",
    "GetEmailByIDFormat",
    "GetEmailByIDResponse",
    "GetEmailByIDResponsePayload",
    "GetEmailByIDResponsePayloadBody",
    "GetEmailByIDResponsePayloadHeadersArrayItemRef",
    "GetEmailByIDResponsePayloadPartsArrayItemRef",
    "GetEmailByIDResponsePayloadPartsBody",
    "GetEmailByIDResponsePayloadPartsHeadersArrayItemRef",
    "GetEmailLabels",
    "GetSingleLabelByIDResponse",
    "ListCalendarEvent",
    "ListCalendarEventAttendeesArrayItemRef",
    "ListEmail",
    "ListEmailBCCArrayItemRef",
    "ListEmailCategoriesArrayItemRef",
    "ListEmailCategoriesArrayItemRefCategoryId",
    "ListEmailCategoriesArrayItemRefCategoryName",
    "ListEmailCCArrayItemRef",
    "ListEmailFrom",
    "ListEmailParentFoldersArrayItemRef",
    "ListEmailToArrayItemRef",
    "ListEmailType",
    "MarkEmailReadUnreadResponse",
    "MoveEmailResponse",
    "RemoveGmailLabelRequest",
    "RemoveGmailLabelResponse",
    "ReplyToEmailBody",
    "ReplyToEmailRequest",
    "ReplyToEmailRequestImportance",
    "ReplyToEmailResponse",
    "ReplyToEmailResponseImportance",
    "SendEmailBody",
    "SendEmailRequest",
    "SendEmailRequestImportance",
    "SendEmailResponse",
    "SendEmailResponseImportance",
    "TurnOffAutomaticRepliesResponse",
    "TurnOnAutomaticRepliesRequest",
    "TurnOnAutomaticRepliesResponse",
    "UpdateCalendarEventRequest",
    "UpdateCalendarEventRequestShowAs",
    "UpdateCalendarEventRequestVisibility",
    "UpdateCalendarEventResponse",
    "UpdateCalendarEventResponseCreator",
    "UpdateCalendarEventResponseEnd",
    "UpdateCalendarEventResponseOrganizer",
    "UpdateCalendarEventResponseReminders",
    "UpdateCalendarEventResponseShowAs",
    "UpdateCalendarEventResponseStart",
    "UpdateCalendarEventResponseVisibility",
)
