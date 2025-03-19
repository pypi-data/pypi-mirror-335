from .download_email import (
    download_email as _download_email,
    download_email_async as _download_email_async,
)
from ..models.default_error import DefaultError
from typing import cast
from .archive_email import (
    archive_email as _archive_email,
    archive_email_async as _archive_email_async,
)
from ..models.archive_email_response import ArchiveEmailResponse
from .apply_gmail_label import (
    apply_gmail_label as _apply_gmail_label,
    apply_gmail_label_async as _apply_gmail_label_async,
)
from ..models.apply_gmail_label_request import ApplyGmailLabelRequest
from ..models.apply_gmail_label_response import ApplyGmailLabelResponse
from .reply_to_email import (
    reply_to_email as _reply_to_email,
    reply_to_email_async as _reply_to_email_async,
)
from ..models.reply_to_email_body import ReplyToEmailBody
from ..models.reply_to_email_response import ReplyToEmailResponse
from .forward_mail import (
    forward_mail as _forward_mail,
    forward_mail_async as _forward_mail_async,
)
from ..models.forward_mail_response import ForwardMailResponse
from .turn_off_automatic_replies import (
    turn_off_automatic_replies as _turn_off_automatic_replies,
    turn_off_automatic_replies_async as _turn_off_automatic_replies_async,
)
from ..models.turn_off_automatic_replies_response import TurnOffAutomaticRepliesResponse
from .send_email import (
    send_email as _send_email,
    send_email_async as _send_email_async,
)
from ..models.send_email_body import SendEmailBody
from ..models.send_email_response import SendEmailResponse
from .remove_gmail_label import (
    remove_gmail_label as _remove_gmail_label,
    remove_gmail_label_async as _remove_gmail_label_async,
)
from ..models.remove_gmail_label_request import RemoveGmailLabelRequest
from ..models.remove_gmail_label_response import RemoveGmailLabelResponse
from .message import (
    get_email_by_id as _get_email_by_id,
    get_email_by_id_async as _get_email_by_id_async,
)
from ..models.get_email_by_id_format import GetEmailByIDFormat
from ..models.get_email_by_id_response import GetEmailByIDResponse
from .curated_calendar_list import (
    get_calendar_list as _get_calendar_list,
    get_calendar_list_async as _get_calendar_list_async,
)
from ..models.get_calendar_list import GetCalendarList
from .mark_email_read_unread import (
    mark_email_read_unread as _mark_email_read_unread,
    mark_email_read_unread_async as _mark_email_read_unread_async,
)
from ..models.mark_email_read_unread_response import MarkEmailReadUnreadResponse
from .list_calendar_event import (
    list_calendar_event as _list_calendar_event,
    list_calendar_event_async as _list_calendar_event_async,
)
from ..models.list_calendar_event import ListCalendarEvent
from dateutil.parser import isoparse
import datetime
from .folder import (
    get_single_label_by_id as _get_single_label_by_id,
    get_single_label_by_id_async as _get_single_label_by_id_async,
    get_email_labels as _get_email_labels,
    get_email_labels_async as _get_email_labels_async,
)
from ..models.get_single_label_by_id_response import GetSingleLabelByIDResponse
from ..models.get_email_labels import GetEmailLabels
from .create_calendar_event import (
    create_calendar_event as _create_calendar_event,
    create_calendar_event_async as _create_calendar_event_async,
)
from ..models.create_calendar_event_request import CreateCalendarEventRequest
from ..models.create_calendar_event_response import CreateCalendarEventResponse
from .list_email import (
    list_email as _list_email,
    list_email_async as _list_email_async,
)
from ..models.list_email import ListEmail
from .delete_email import (
    delete_email as _delete_email,
    delete_email_async as _delete_email_async,
)
from ..models.delete_email_response import DeleteEmailResponse
from .update_calendar_event import (
    update_calendar_event as _update_calendar_event,
    update_calendar_event_async as _update_calendar_event_async,
)
from ..models.update_calendar_event_request import UpdateCalendarEventRequest
from ..models.update_calendar_event_response import UpdateCalendarEventResponse
from .download_attachment import (
    download_attachment as _download_attachment,
    download_attachment_async as _download_attachment_async,
)
from .move_email import (
    move_email as _move_email,
    move_email_async as _move_email_async,
)
from ..models.move_email_response import MoveEmailResponse
from .turn_on_automatic_replies import (
    turn_on_automatic_replies as _turn_on_automatic_replies,
    turn_on_automatic_replies_async as _turn_on_automatic_replies_async,
)
from ..models.turn_on_automatic_replies_request import TurnOnAutomaticRepliesRequest
from ..models.turn_on_automatic_replies_response import TurnOnAutomaticRepliesResponse

from pydantic import Field
from typing import Any, Optional, Union

from ..client import Client
import httpx


class GoogleGmail:
    def __init__(self, *, instance_id: str, client: httpx.Client):
        base_url = str(client.base_url).rstrip("/")
        new_headers = {
            k: v for k, v in client.headers.items() if k not in ["content-type"]
        }
        new_client = httpx.Client(
            base_url=base_url + f"/elements_/v3/element/instances/{instance_id}",
            headers=new_headers,
            timeout=100,
        )
        new_client_async = httpx.AsyncClient(
            base_url=base_url + f"/elements_/v3/element/instances/{instance_id}",
            headers=new_headers,
            timeout=100,
        )
        self.client = (
            Client(
                base_url="",  # this will be overridden by the base_url in the Client constructor
            )
            .set_httpx_client(new_client)
            .set_async_httpx_client(new_client_async)
        )

    def download_email(
        self,
        *,
        id: str,
        id_lookup: Any,
    ) -> Optional[Union[Any, DefaultError]]:
        return _download_email(
            client=self.client,
            id=id,
            id_lookup=id_lookup,
        )

    async def download_email_async(
        self,
        *,
        id: str,
        id_lookup: Any,
    ) -> Optional[Union[Any, DefaultError]]:
        return await _download_email_async(
            client=self.client,
            id=id,
            id_lookup=id_lookup,
        )

    def archive_email(
        self,
        *,
        id: str,
        id_lookup: Any,
    ) -> Optional[Union[ArchiveEmailResponse, DefaultError]]:
        return _archive_email(
            client=self.client,
            id=id,
            id_lookup=id_lookup,
        )

    async def archive_email_async(
        self,
        *,
        id: str,
        id_lookup: Any,
    ) -> Optional[Union[ArchiveEmailResponse, DefaultError]]:
        return await _archive_email_async(
            client=self.client,
            id=id,
            id_lookup=id_lookup,
        )

    def apply_gmail_label(
        self,
        *,
        body: ApplyGmailLabelRequest,
        id: str,
        id_lookup: Any,
    ) -> Optional[Union[ApplyGmailLabelResponse, DefaultError]]:
        return _apply_gmail_label(
            client=self.client,
            body=body,
            id=id,
            id_lookup=id_lookup,
        )

    async def apply_gmail_label_async(
        self,
        *,
        body: ApplyGmailLabelRequest,
        id: str,
        id_lookup: Any,
    ) -> Optional[Union[ApplyGmailLabelResponse, DefaultError]]:
        return await _apply_gmail_label_async(
            client=self.client,
            body=body,
            id=id,
            id_lookup=id_lookup,
        )

    def reply_to_email(
        self,
        *,
        body: ReplyToEmailBody,
        save_as_draft: Optional[bool] = None,
        save_as_draft_lookup: Any,
    ) -> Optional[Union[DefaultError, ReplyToEmailResponse]]:
        return _reply_to_email(
            client=self.client,
            body=body,
            save_as_draft=save_as_draft,
            save_as_draft_lookup=save_as_draft_lookup,
        )

    async def reply_to_email_async(
        self,
        *,
        body: ReplyToEmailBody,
        save_as_draft: Optional[bool] = None,
        save_as_draft_lookup: Any,
    ) -> Optional[Union[DefaultError, ReplyToEmailResponse]]:
        return await _reply_to_email_async(
            client=self.client,
            body=body,
            save_as_draft=save_as_draft,
            save_as_draft_lookup=save_as_draft_lookup,
        )

    def forward_mail(
        self,
        *,
        to: str,
        to_lookup: Any,
        id: str,
        id_lookup: Any,
    ) -> Optional[Union[DefaultError, ForwardMailResponse]]:
        return _forward_mail(
            client=self.client,
            to=to,
            to_lookup=to_lookup,
            id=id,
            id_lookup=id_lookup,
        )

    async def forward_mail_async(
        self,
        *,
        to: str,
        to_lookup: Any,
        id: str,
        id_lookup: Any,
    ) -> Optional[Union[DefaultError, ForwardMailResponse]]:
        return await _forward_mail_async(
            client=self.client,
            to=to,
            to_lookup=to_lookup,
            id=id,
            id_lookup=id_lookup,
        )

    def turn_off_automatic_replies(
        self,
    ) -> Optional[Union[DefaultError, TurnOffAutomaticRepliesResponse]]:
        return _turn_off_automatic_replies(
            client=self.client,
        )

    async def turn_off_automatic_replies_async(
        self,
    ) -> Optional[Union[DefaultError, TurnOffAutomaticRepliesResponse]]:
        return await _turn_off_automatic_replies_async(
            client=self.client,
        )

    def send_email(
        self,
        *,
        body: SendEmailBody,
        save_as_draft: Optional[bool] = None,
        save_as_draft_lookup: Any,
    ) -> Optional[Union[DefaultError, SendEmailResponse]]:
        return _send_email(
            client=self.client,
            body=body,
            save_as_draft=save_as_draft,
            save_as_draft_lookup=save_as_draft_lookup,
        )

    async def send_email_async(
        self,
        *,
        body: SendEmailBody,
        save_as_draft: Optional[bool] = None,
        save_as_draft_lookup: Any,
    ) -> Optional[Union[DefaultError, SendEmailResponse]]:
        return await _send_email_async(
            client=self.client,
            body=body,
            save_as_draft=save_as_draft,
            save_as_draft_lookup=save_as_draft_lookup,
        )

    def remove_gmail_label(
        self,
        *,
        body: RemoveGmailLabelRequest,
        id: str,
        id_lookup: Any,
    ) -> Optional[Union[DefaultError, RemoveGmailLabelResponse]]:
        return _remove_gmail_label(
            client=self.client,
            body=body,
            id=id,
            id_lookup=id_lookup,
        )

    async def remove_gmail_label_async(
        self,
        *,
        body: RemoveGmailLabelRequest,
        id: str,
        id_lookup: Any,
    ) -> Optional[Union[DefaultError, RemoveGmailLabelResponse]]:
        return await _remove_gmail_label_async(
            client=self.client,
            body=body,
            id=id,
            id_lookup=id_lookup,
        )

    def get_email_by_id(
        self,
        id: str,
        id_lookup: Any,
        *,
        format_: Optional[GetEmailByIDFormat] = None,
        format__lookup: Any,
        metadata_headers: Optional[str] = None,
        metadata_headers_lookup: Any,
    ) -> Optional[Union[DefaultError, GetEmailByIDResponse]]:
        return _get_email_by_id(
            client=self.client,
            id=id,
            id_lookup=id_lookup,
            format_=format_,
            format__lookup=format__lookup,
            metadata_headers=metadata_headers,
            metadata_headers_lookup=metadata_headers_lookup,
        )

    async def get_email_by_id_async(
        self,
        id: str,
        id_lookup: Any,
        *,
        format_: Optional[GetEmailByIDFormat] = None,
        format__lookup: Any,
        metadata_headers: Optional[str] = None,
        metadata_headers_lookup: Any,
    ) -> Optional[Union[DefaultError, GetEmailByIDResponse]]:
        return await _get_email_by_id_async(
            client=self.client,
            id=id,
            id_lookup=id_lookup,
            format_=format_,
            format__lookup=format__lookup,
            metadata_headers=metadata_headers,
            metadata_headers_lookup=metadata_headers_lookup,
        )

    def get_calendar_list(
        self,
        *,
        fields: Optional[str] = None,
        fields_lookup: Any,
        next_page: Optional[str] = None,
        next_page_lookup: Any,
        page_size: Optional[int] = None,
        page_size_lookup: Any,
        parent_reference: Optional[str] = None,
        parent_reference_lookup: Any,
    ) -> Optional[Union[DefaultError, list["GetCalendarList"]]]:
        return _get_calendar_list(
            client=self.client,
            fields=fields,
            fields_lookup=fields_lookup,
            next_page=next_page,
            next_page_lookup=next_page_lookup,
            page_size=page_size,
            page_size_lookup=page_size_lookup,
            parent_reference=parent_reference,
            parent_reference_lookup=parent_reference_lookup,
        )

    async def get_calendar_list_async(
        self,
        *,
        fields: Optional[str] = None,
        fields_lookup: Any,
        next_page: Optional[str] = None,
        next_page_lookup: Any,
        page_size: Optional[int] = None,
        page_size_lookup: Any,
        parent_reference: Optional[str] = None,
        parent_reference_lookup: Any,
    ) -> Optional[Union[DefaultError, list["GetCalendarList"]]]:
        return await _get_calendar_list_async(
            client=self.client,
            fields=fields,
            fields_lookup=fields_lookup,
            next_page=next_page,
            next_page_lookup=next_page_lookup,
            page_size=page_size,
            page_size_lookup=page_size_lookup,
            parent_reference=parent_reference,
            parent_reference_lookup=parent_reference_lookup,
        )

    def mark_email_read_unread(
        self,
        *,
        id: str,
        id_lookup: Any,
        mark_as: Optional[str] = "Read",
        mark_as_lookup: Any,
    ) -> Optional[Union[DefaultError, MarkEmailReadUnreadResponse]]:
        return _mark_email_read_unread(
            client=self.client,
            id=id,
            id_lookup=id_lookup,
            mark_as=mark_as,
            mark_as_lookup=mark_as_lookup,
        )

    async def mark_email_read_unread_async(
        self,
        *,
        id: str,
        id_lookup: Any,
        mark_as: Optional[str] = "Read",
        mark_as_lookup: Any,
    ) -> Optional[Union[DefaultError, MarkEmailReadUnreadResponse]]:
        return await _mark_email_read_unread_async(
            client=self.client,
            id=id,
            id_lookup=id_lookup,
            mark_as=mark_as,
            mark_as_lookup=mark_as_lookup,
        )

    def list_calendar_event(
        self,
        *,
        from_: datetime.datetime,
        from__lookup: Any,
        until: datetime.datetime,
        until_lookup: Any,
        calendar: Optional[str] = None,
        calendar_lookup: Any,
        fields: Optional[str] = None,
        fields_lookup: Any,
        limit: Optional[str] = "50",
        limit_lookup: Any,
        next_page: Optional[str] = None,
        next_page_lookup: Any,
        page_size: Optional[int] = None,
        page_size_lookup: Any,
        q: Optional[str] = None,
        q_lookup: Any,
        time_zone: Optional[str] = None,
        time_zone_lookup: Any,
    ) -> Optional[Union[DefaultError, list["ListCalendarEvent"]]]:
        return _list_calendar_event(
            client=self.client,
            from_=from_,
            from__lookup=from__lookup,
            until=until,
            until_lookup=until_lookup,
            calendar=calendar,
            calendar_lookup=calendar_lookup,
            fields=fields,
            fields_lookup=fields_lookup,
            limit=limit,
            limit_lookup=limit_lookup,
            next_page=next_page,
            next_page_lookup=next_page_lookup,
            page_size=page_size,
            page_size_lookup=page_size_lookup,
            q=q,
            q_lookup=q_lookup,
            time_zone=time_zone,
            time_zone_lookup=time_zone_lookup,
        )

    async def list_calendar_event_async(
        self,
        *,
        from_: datetime.datetime,
        from__lookup: Any,
        until: datetime.datetime,
        until_lookup: Any,
        calendar: Optional[str] = None,
        calendar_lookup: Any,
        fields: Optional[str] = None,
        fields_lookup: Any,
        limit: Optional[str] = "50",
        limit_lookup: Any,
        next_page: Optional[str] = None,
        next_page_lookup: Any,
        page_size: Optional[int] = None,
        page_size_lookup: Any,
        q: Optional[str] = None,
        q_lookup: Any,
        time_zone: Optional[str] = None,
        time_zone_lookup: Any,
    ) -> Optional[Union[DefaultError, list["ListCalendarEvent"]]]:
        return await _list_calendar_event_async(
            client=self.client,
            from_=from_,
            from__lookup=from__lookup,
            until=until,
            until_lookup=until_lookup,
            calendar=calendar,
            calendar_lookup=calendar_lookup,
            fields=fields,
            fields_lookup=fields_lookup,
            limit=limit,
            limit_lookup=limit_lookup,
            next_page=next_page,
            next_page_lookup=next_page_lookup,
            page_size=page_size,
            page_size_lookup=page_size_lookup,
            q=q,
            q_lookup=q_lookup,
            time_zone=time_zone,
            time_zone_lookup=time_zone_lookup,
        )

    def get_single_label_by_id(
        self,
        id: str,
        id_lookup: Any,
    ) -> Optional[Union[DefaultError, GetSingleLabelByIDResponse]]:
        return _get_single_label_by_id(
            client=self.client,
            id=id,
            id_lookup=id_lookup,
        )

    async def get_single_label_by_id_async(
        self,
        id: str,
        id_lookup: Any,
    ) -> Optional[Union[DefaultError, GetSingleLabelByIDResponse]]:
        return await _get_single_label_by_id_async(
            client=self.client,
            id=id,
            id_lookup=id_lookup,
        )

    def get_email_labels(
        self,
        *,
        fields: Optional[str] = None,
        fields_lookup: Any,
        next_page: Optional[str] = None,
        next_page_lookup: Any,
        page_size: Optional[int] = None,
        page_size_lookup: Any,
        parent_reference: Optional[str] = None,
        parent_reference_lookup: Any,
    ) -> Optional[Union[DefaultError, list["GetEmailLabels"]]]:
        return _get_email_labels(
            client=self.client,
            fields=fields,
            fields_lookup=fields_lookup,
            next_page=next_page,
            next_page_lookup=next_page_lookup,
            page_size=page_size,
            page_size_lookup=page_size_lookup,
            parent_reference=parent_reference,
            parent_reference_lookup=parent_reference_lookup,
        )

    async def get_email_labels_async(
        self,
        *,
        fields: Optional[str] = None,
        fields_lookup: Any,
        next_page: Optional[str] = None,
        next_page_lookup: Any,
        page_size: Optional[int] = None,
        page_size_lookup: Any,
        parent_reference: Optional[str] = None,
        parent_reference_lookup: Any,
    ) -> Optional[Union[DefaultError, list["GetEmailLabels"]]]:
        return await _get_email_labels_async(
            client=self.client,
            fields=fields,
            fields_lookup=fields_lookup,
            next_page=next_page,
            next_page_lookup=next_page_lookup,
            page_size=page_size,
            page_size_lookup=page_size_lookup,
            parent_reference=parent_reference,
            parent_reference_lookup=parent_reference_lookup,
        )

    def create_calendar_event(
        self,
        *,
        body: CreateCalendarEventRequest,
        add_conference_data: Optional[bool] = False,
        add_conference_data_lookup: Any,
        calendar: Optional[str] = None,
        calendar_lookup: Any,
        send_notifications: Optional[str] = None,
        send_notifications_lookup: Any,
    ) -> Optional[Union[CreateCalendarEventResponse, DefaultError]]:
        return _create_calendar_event(
            client=self.client,
            body=body,
            add_conference_data=add_conference_data,
            add_conference_data_lookup=add_conference_data_lookup,
            calendar=calendar,
            calendar_lookup=calendar_lookup,
            send_notifications=send_notifications,
            send_notifications_lookup=send_notifications_lookup,
        )

    async def create_calendar_event_async(
        self,
        *,
        body: CreateCalendarEventRequest,
        add_conference_data: Optional[bool] = False,
        add_conference_data_lookup: Any,
        calendar: Optional[str] = None,
        calendar_lookup: Any,
        send_notifications: Optional[str] = None,
        send_notifications_lookup: Any,
    ) -> Optional[Union[CreateCalendarEventResponse, DefaultError]]:
        return await _create_calendar_event_async(
            client=self.client,
            body=body,
            add_conference_data=add_conference_data,
            add_conference_data_lookup=add_conference_data_lookup,
            calendar=calendar,
            calendar_lookup=calendar_lookup,
            send_notifications=send_notifications,
            send_notifications_lookup=send_notifications_lookup,
        )

    def list_email(
        self,
        *,
        email_folder: str,
        email_folder_lookup: Any,
        additional_filters: Optional[str] = None,
        additional_filters_lookup: Any,
        fields: Optional[str] = None,
        fields_lookup: Any,
        important_only: Optional[bool] = None,
        important_only_lookup: Any,
        next_page: Optional[str] = None,
        next_page_lookup: Any,
        page_size: Optional[int] = None,
        page_size_lookup: Any,
        starred_only: Optional[bool] = None,
        starred_only_lookup: Any,
        unread_only: Optional[bool] = None,
        unread_only_lookup: Any,
        with_attachments_only: Optional[bool] = None,
        with_attachments_only_lookup: Any,
    ) -> Optional[Union[DefaultError, list["ListEmail"]]]:
        return _list_email(
            client=self.client,
            email_folder=email_folder,
            email_folder_lookup=email_folder_lookup,
            additional_filters=additional_filters,
            additional_filters_lookup=additional_filters_lookup,
            fields=fields,
            fields_lookup=fields_lookup,
            important_only=important_only,
            important_only_lookup=important_only_lookup,
            next_page=next_page,
            next_page_lookup=next_page_lookup,
            page_size=page_size,
            page_size_lookup=page_size_lookup,
            starred_only=starred_only,
            starred_only_lookup=starred_only_lookup,
            unread_only=unread_only,
            unread_only_lookup=unread_only_lookup,
            with_attachments_only=with_attachments_only,
            with_attachments_only_lookup=with_attachments_only_lookup,
        )

    async def list_email_async(
        self,
        *,
        email_folder: str,
        email_folder_lookup: Any,
        additional_filters: Optional[str] = None,
        additional_filters_lookup: Any,
        fields: Optional[str] = None,
        fields_lookup: Any,
        important_only: Optional[bool] = None,
        important_only_lookup: Any,
        next_page: Optional[str] = None,
        next_page_lookup: Any,
        page_size: Optional[int] = None,
        page_size_lookup: Any,
        starred_only: Optional[bool] = None,
        starred_only_lookup: Any,
        unread_only: Optional[bool] = None,
        unread_only_lookup: Any,
        with_attachments_only: Optional[bool] = None,
        with_attachments_only_lookup: Any,
    ) -> Optional[Union[DefaultError, list["ListEmail"]]]:
        return await _list_email_async(
            client=self.client,
            email_folder=email_folder,
            email_folder_lookup=email_folder_lookup,
            additional_filters=additional_filters,
            additional_filters_lookup=additional_filters_lookup,
            fields=fields,
            fields_lookup=fields_lookup,
            important_only=important_only,
            important_only_lookup=important_only_lookup,
            next_page=next_page,
            next_page_lookup=next_page_lookup,
            page_size=page_size,
            page_size_lookup=page_size_lookup,
            starred_only=starred_only,
            starred_only_lookup=starred_only_lookup,
            unread_only=unread_only,
            unread_only_lookup=unread_only_lookup,
            with_attachments_only=with_attachments_only,
            with_attachments_only_lookup=with_attachments_only_lookup,
        )

    def delete_email(
        self,
        *,
        permanently_delete: Optional[bool] = False,
        permanently_delete_lookup: Any,
        id: str,
        id_lookup: Any,
    ) -> Optional[Union[DefaultError, DeleteEmailResponse]]:
        return _delete_email(
            client=self.client,
            permanently_delete=permanently_delete,
            permanently_delete_lookup=permanently_delete_lookup,
            id=id,
            id_lookup=id_lookup,
        )

    async def delete_email_async(
        self,
        *,
        permanently_delete: Optional[bool] = False,
        permanently_delete_lookup: Any,
        id: str,
        id_lookup: Any,
    ) -> Optional[Union[DefaultError, DeleteEmailResponse]]:
        return await _delete_email_async(
            client=self.client,
            permanently_delete=permanently_delete,
            permanently_delete_lookup=permanently_delete_lookup,
            id=id,
            id_lookup=id_lookup,
        )

    def update_calendar_event(
        self,
        id: str,
        id_lookup: Any,
        *,
        body: UpdateCalendarEventRequest,
        add_conference_data: Optional[bool] = None,
        add_conference_data_lookup: Any,
        calendar: Optional[str] = None,
        calendar_lookup: Any,
        send_notifications: Optional[str] = "All",
        send_notifications_lookup: Any,
    ) -> Optional[Union[DefaultError, UpdateCalendarEventResponse]]:
        return _update_calendar_event(
            client=self.client,
            id=id,
            id_lookup=id_lookup,
            body=body,
            add_conference_data=add_conference_data,
            add_conference_data_lookup=add_conference_data_lookup,
            calendar=calendar,
            calendar_lookup=calendar_lookup,
            send_notifications=send_notifications,
            send_notifications_lookup=send_notifications_lookup,
        )

    async def update_calendar_event_async(
        self,
        id: str,
        id_lookup: Any,
        *,
        body: UpdateCalendarEventRequest,
        add_conference_data: Optional[bool] = None,
        add_conference_data_lookup: Any,
        calendar: Optional[str] = None,
        calendar_lookup: Any,
        send_notifications: Optional[str] = "All",
        send_notifications_lookup: Any,
    ) -> Optional[Union[DefaultError, UpdateCalendarEventResponse]]:
        return await _update_calendar_event_async(
            client=self.client,
            id=id,
            id_lookup=id_lookup,
            body=body,
            add_conference_data=add_conference_data,
            add_conference_data_lookup=add_conference_data_lookup,
            calendar=calendar,
            calendar_lookup=calendar_lookup,
            send_notifications=send_notifications,
            send_notifications_lookup=send_notifications_lookup,
        )

    def download_attachment(
        self,
        id: str,
        id_lookup: Any,
        *,
        exclude_inline_attachment: Optional[bool] = False,
        exclude_inline_attachment_lookup: Any,
        file_name: Optional[str] = None,
        file_name_lookup: Any,
    ) -> Optional[Union[Any, DefaultError]]:
        return _download_attachment(
            client=self.client,
            id=id,
            id_lookup=id_lookup,
            exclude_inline_attachment=exclude_inline_attachment,
            exclude_inline_attachment_lookup=exclude_inline_attachment_lookup,
            file_name=file_name,
            file_name_lookup=file_name_lookup,
        )

    async def download_attachment_async(
        self,
        id: str,
        id_lookup: Any,
        *,
        exclude_inline_attachment: Optional[bool] = False,
        exclude_inline_attachment_lookup: Any,
        file_name: Optional[str] = None,
        file_name_lookup: Any,
    ) -> Optional[Union[Any, DefaultError]]:
        return await _download_attachment_async(
            client=self.client,
            id=id,
            id_lookup=id_lookup,
            exclude_inline_attachment=exclude_inline_attachment,
            exclude_inline_attachment_lookup=exclude_inline_attachment_lookup,
            file_name=file_name,
            file_name_lookup=file_name_lookup,
        )

    def move_email(
        self,
        *,
        id: str,
        id_lookup: Any,
        add_label_id: str,
        add_label_id_lookup: Any,
    ) -> Optional[Union[DefaultError, MoveEmailResponse]]:
        return _move_email(
            client=self.client,
            id=id,
            id_lookup=id_lookup,
            add_label_id=add_label_id,
            add_label_id_lookup=add_label_id_lookup,
        )

    async def move_email_async(
        self,
        *,
        id: str,
        id_lookup: Any,
        add_label_id: str,
        add_label_id_lookup: Any,
    ) -> Optional[Union[DefaultError, MoveEmailResponse]]:
        return await _move_email_async(
            client=self.client,
            id=id,
            id_lookup=id_lookup,
            add_label_id=add_label_id,
            add_label_id_lookup=add_label_id_lookup,
        )

    def turn_on_automatic_replies(
        self,
        *,
        body: TurnOnAutomaticRepliesRequest,
    ) -> Optional[Union[DefaultError, TurnOnAutomaticRepliesResponse]]:
        return _turn_on_automatic_replies(
            client=self.client,
            body=body,
        )

    async def turn_on_automatic_replies_async(
        self,
        *,
        body: TurnOnAutomaticRepliesRequest,
    ) -> Optional[Union[DefaultError, TurnOnAutomaticRepliesResponse]]:
        return await _turn_on_automatic_replies_async(
            client=self.client,
            body=body,
        )
