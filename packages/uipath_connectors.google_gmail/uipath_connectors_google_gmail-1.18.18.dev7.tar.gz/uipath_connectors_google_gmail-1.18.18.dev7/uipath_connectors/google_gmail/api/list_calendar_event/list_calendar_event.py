from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response
from ... import errors

from ...models.default_error import DefaultError
from ...models.list_calendar_event import ListCalendarEvent
import datetime


def _get_kwargs(
    *,
    from_: datetime.datetime,
    until: datetime.datetime,
    calendar: Optional[str] = None,
    fields: Optional[str] = None,
    limit: Optional[str] = "50",
    next_page: Optional[str] = None,
    page_size: Optional[int] = None,
    q: Optional[str] = None,
    time_zone: Optional[str] = None,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_from_ = from_.isoformat()
    params["From"] = json_from_

    json_until = until.isoformat()
    params["Until"] = json_until

    params["Calendar"] = calendar

    params["fields"] = fields

    params["limit"] = limit

    params["nextPage"] = next_page

    params["pageSize"] = page_size

    params["q"] = q

    params["timeZone"] = time_zone

    params = {k: v for k, v in params.items() if v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/hubs/general/ListCalendarEvents",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[DefaultError, list["ListCalendarEvent"]]]:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for componentsschemas_list_calendar_event_list_item_data in _response_200:
            componentsschemas_list_calendar_event_list_item = (
                ListCalendarEvent.from_dict(
                    componentsschemas_list_calendar_event_list_item_data
                )
            )

            response_200.append(componentsschemas_list_calendar_event_list_item)

        return response_200
    if response.status_code == 400:
        response_400 = DefaultError.from_dict(response.json())

        return response_400
    if response.status_code == 401:
        response_401 = DefaultError.from_dict(response.json())

        return response_401
    if response.status_code == 403:
        response_403 = DefaultError.from_dict(response.json())

        return response_403
    if response.status_code == 404:
        response_404 = DefaultError.from_dict(response.json())

        return response_404
    if response.status_code == 405:
        response_405 = DefaultError.from_dict(response.json())

        return response_405
    if response.status_code == 406:
        response_406 = DefaultError.from_dict(response.json())

        return response_406
    if response.status_code == 409:
        response_409 = DefaultError.from_dict(response.json())

        return response_409
    if response.status_code == 415:
        response_415 = DefaultError.from_dict(response.json())

        return response_415
    if response.status_code == 500:
        response_500 = DefaultError.from_dict(response.json())

        return response_500
    if response.status_code == 402:
        response_402 = DefaultError.from_dict(response.json())

        return response_402
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[DefaultError, list["ListCalendarEvent"]]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
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
) -> Response[Union[DefaultError, list["ListCalendarEvent"]]]:
    """List Calendar Events

     Lists events according to filter criteria.

    Args:
        from_ (datetime.datetime):
        until (datetime.datetime):
        calendar (Optional[str]):
        fields (Optional[str]):
        limit (Optional[str]):  Default: '50'.
        next_page (Optional[str]):
        page_size (Optional[int]):
        q (Optional[str]):
        time_zone (Optional[str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[DefaultError, list['ListCalendarEvent']]]
    """

    if not calendar and calendar_lookup:
        lookup_response_raw = client.get_httpx_client().request(
            method="get", url="/hubs/general/CuratedCalendarList"
        )
        lookup_response = lookup_response_raw.json()

        found_items = []
        for item in lookup_response:
            if calendar_lookup in item["FullName"]:
                found_items.append(item)

        if not found_items:
            raise ValueError(
                "No matches found for calendar_lookup in CuratedCalendarList"
            )
        if len(found_items) > 1:
            print(
                "Warning: Multiple matches found for calendar_lookup in CuratedCalendarList. Using the first match."
            )

        calendar = found_items[0]["ID"]

    kwargs = _get_kwargs(
        from_=from_,
        until=until,
        calendar=calendar,
        fields=fields,
        limit=limit,
        next_page=next_page,
        page_size=page_size,
        q=q,
        time_zone=time_zone,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: Union[AuthenticatedClient, Client],
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
    """List Calendar Events

     Lists events according to filter criteria.

    Args:
        from_ (datetime.datetime):
        until (datetime.datetime):
        calendar (Optional[str]):
        fields (Optional[str]):
        limit (Optional[str]):  Default: '50'.
        next_page (Optional[str]):
        page_size (Optional[int]):
        q (Optional[str]):
        time_zone (Optional[str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[DefaultError, list['ListCalendarEvent']]
    """

    return sync_detailed(
        client=client,
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
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
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
) -> Response[Union[DefaultError, list["ListCalendarEvent"]]]:
    """List Calendar Events

     Lists events according to filter criteria.

    Args:
        from_ (datetime.datetime):
        until (datetime.datetime):
        calendar (Optional[str]):
        fields (Optional[str]):
        limit (Optional[str]):  Default: '50'.
        next_page (Optional[str]):
        page_size (Optional[int]):
        q (Optional[str]):
        time_zone (Optional[str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[DefaultError, list['ListCalendarEvent']]]
    """

    if not calendar and calendar_lookup:
        lookup_response_raw = await client.get_async_httpx_client().request(
            method="get", url="/hubs/general/CuratedCalendarList"
        )
        lookup_response = lookup_response_raw.json()

        found_items = []
        for item in lookup_response:
            if calendar_lookup in item["FullName"]:
                found_items.append(item)

        if not found_items:
            raise ValueError(
                "No matches found for calendar_lookup in CuratedCalendarList"
            )
        if len(found_items) > 1:
            print(
                "Warning: Multiple matches found for calendar_lookup in CuratedCalendarList. Using the first match."
            )

        calendar = found_items[0]["ID"]

    kwargs = _get_kwargs(
        from_=from_,
        until=until,
        calendar=calendar,
        fields=fields,
        limit=limit,
        next_page=next_page,
        page_size=page_size,
        q=q,
        time_zone=time_zone,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
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
    """List Calendar Events

     Lists events according to filter criteria.

    Args:
        from_ (datetime.datetime):
        until (datetime.datetime):
        calendar (Optional[str]):
        fields (Optional[str]):
        limit (Optional[str]):  Default: '50'.
        next_page (Optional[str]):
        page_size (Optional[int]):
        q (Optional[str]):
        time_zone (Optional[str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[DefaultError, list['ListCalendarEvent']]
    """

    return (
        await asyncio_detailed(
            client=client,
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
    ).parsed
