from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response
from ... import errors

from ...models.default_error import DefaultError
from ...models.get_email_by_id_format import GetEmailByIDFormat
from ...models.get_email_by_id_response import GetEmailByIDResponse


def _get_kwargs(
    id: str,
    *,
    format_: Optional[GetEmailByIDFormat] = None,
    metadata_headers: Optional[str] = None,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_format_: Optional[str] = None
    if format_ is not None:
        json_format_ = format_.value

    params["format"] = json_format_

    params["metadataHeaders[]"] = metadata_headers

    params = {k: v for k, v in params.items() if v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/message/{id}".format(
            id=id,
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[DefaultError, GetEmailByIDResponse]]:
    if response.status_code == 200:
        response_200 = GetEmailByIDResponse.from_dict(response.json())

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
) -> Response[Union[DefaultError, GetEmailByIDResponse]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    id: str,
    id_lookup: Any,
    *,
    client: Union[AuthenticatedClient, Client],
    format_: Optional[GetEmailByIDFormat] = None,
    format__lookup: Any,
    metadata_headers: Optional[str] = None,
    metadata_headers_lookup: Any,
) -> Response[Union[DefaultError, GetEmailByIDResponse]]:
    """Get Email by ID

     Fetch an email based on ID

    Args:
        id (str):
        format_ (Optional[GetEmailByIDFormat]):
        metadata_headers (Optional[str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[DefaultError, GetEmailByIDResponse]]
    """

    kwargs = _get_kwargs(
        id=id,
        format_=format_,
        metadata_headers=metadata_headers,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    id: str,
    id_lookup: Any,
    *,
    client: Union[AuthenticatedClient, Client],
    format_: Optional[GetEmailByIDFormat] = None,
    format__lookup: Any,
    metadata_headers: Optional[str] = None,
    metadata_headers_lookup: Any,
) -> Optional[Union[DefaultError, GetEmailByIDResponse]]:
    """Get Email by ID

     Fetch an email based on ID

    Args:
        id (str):
        format_ (Optional[GetEmailByIDFormat]):
        metadata_headers (Optional[str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[DefaultError, GetEmailByIDResponse]
    """

    return sync_detailed(
        id=id,
        id_lookup=id_lookup,
        client=client,
        format_=format_,
        format__lookup=format__lookup,
        metadata_headers=metadata_headers,
        metadata_headers_lookup=metadata_headers_lookup,
    ).parsed


async def asyncio_detailed(
    id: str,
    id_lookup: Any,
    *,
    client: Union[AuthenticatedClient, Client],
    format_: Optional[GetEmailByIDFormat] = None,
    format__lookup: Any,
    metadata_headers: Optional[str] = None,
    metadata_headers_lookup: Any,
) -> Response[Union[DefaultError, GetEmailByIDResponse]]:
    """Get Email by ID

     Fetch an email based on ID

    Args:
        id (str):
        format_ (Optional[GetEmailByIDFormat]):
        metadata_headers (Optional[str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[DefaultError, GetEmailByIDResponse]]
    """

    kwargs = _get_kwargs(
        id=id,
        format_=format_,
        metadata_headers=metadata_headers,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    id: str,
    id_lookup: Any,
    *,
    client: Union[AuthenticatedClient, Client],
    format_: Optional[GetEmailByIDFormat] = None,
    format__lookup: Any,
    metadata_headers: Optional[str] = None,
    metadata_headers_lookup: Any,
) -> Optional[Union[DefaultError, GetEmailByIDResponse]]:
    """Get Email by ID

     Fetch an email based on ID

    Args:
        id (str):
        format_ (Optional[GetEmailByIDFormat]):
        metadata_headers (Optional[str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[DefaultError, GetEmailByIDResponse]
    """

    return (
        await asyncio_detailed(
            id=id,
            id_lookup=id_lookup,
            client=client,
            format_=format_,
            format__lookup=format__lookup,
            metadata_headers=metadata_headers,
            metadata_headers_lookup=metadata_headers_lookup,
        )
    ).parsed
