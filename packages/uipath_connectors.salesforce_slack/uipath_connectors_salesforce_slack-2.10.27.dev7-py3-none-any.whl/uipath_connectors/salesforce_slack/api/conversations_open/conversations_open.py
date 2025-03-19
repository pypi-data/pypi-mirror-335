from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response
from ... import errors

from ...models.conversations_open_request import ConversationsOpenRequest
from ...models.conversations_open_response import ConversationsOpenResponse
from ...models.default_error import DefaultError


def _get_kwargs(
    *,
    body: ConversationsOpenRequest,
    send_as: str = "bot",
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    params: dict[str, Any] = {}

    params["send_as"] = send_as

    params = {k: v for k, v in params.items() if v is not None}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/conversations_open",
        "params": params,
    }

    _body = body.to_dict()

    _kwargs["json"] = _body
    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[ConversationsOpenResponse, DefaultError]]:
    if response.status_code == 200:
        response_200 = ConversationsOpenResponse.from_dict(response.json())

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
) -> Response[Union[ConversationsOpenResponse, DefaultError]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: ConversationsOpenRequest,
    send_as: str = "bot",
    send_as_lookup: Any,
) -> Response[Union[ConversationsOpenResponse, DefaultError]]:
    """Create Group Direct Message

     Create a group direct message. The output of this activity must be passed as input to 'Send Message
    to Channel' activity for sending messages

    Args:
        send_as (str):  Default: 'bot'.
        body (ConversationsOpenRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ConversationsOpenResponse, DefaultError]]
    """

    if not send_as and send_as_lookup:
        lookup_response_raw = client.get_httpx_client().request(
            method="get", url="/available_tokens"
        )
        lookup_response = lookup_response_raw.json()

        found_items = []
        for item in lookup_response:
            if send_as_lookup in item["name"] or send_as_lookup in item["value"]:
                found_items.append(item)

        if not found_items:
            raise ValueError("No matches found for send_as_lookup in available_tokens")
        if len(found_items) > 1:
            print(
                "Warning: Multiple matches found for send_as_lookup in available_tokens. Using the first match."
            )

        send_as = found_items[0]["value"]

    kwargs = _get_kwargs(
        body=body,
        send_as=send_as,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: Union[AuthenticatedClient, Client],
    body: ConversationsOpenRequest,
    send_as: str = "bot",
    send_as_lookup: Any,
) -> Optional[Union[ConversationsOpenResponse, DefaultError]]:
    """Create Group Direct Message

     Create a group direct message. The output of this activity must be passed as input to 'Send Message
    to Channel' activity for sending messages

    Args:
        send_as (str):  Default: 'bot'.
        body (ConversationsOpenRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ConversationsOpenResponse, DefaultError]
    """

    return sync_detailed(
        client=client,
        body=body,
        send_as=send_as,
        send_as_lookup=send_as_lookup,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: ConversationsOpenRequest,
    send_as: str = "bot",
    send_as_lookup: Any,
) -> Response[Union[ConversationsOpenResponse, DefaultError]]:
    """Create Group Direct Message

     Create a group direct message. The output of this activity must be passed as input to 'Send Message
    to Channel' activity for sending messages

    Args:
        send_as (str):  Default: 'bot'.
        body (ConversationsOpenRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ConversationsOpenResponse, DefaultError]]
    """

    if not send_as and send_as_lookup:
        lookup_response_raw = await client.get_async_httpx_client().request(
            method="get", url="/available_tokens"
        )
        lookup_response = lookup_response_raw.json()

        found_items = []
        for item in lookup_response:
            if send_as_lookup in item["name"] or send_as_lookup in item["value"]:
                found_items.append(item)

        if not found_items:
            raise ValueError("No matches found for send_as_lookup in available_tokens")
        if len(found_items) > 1:
            print(
                "Warning: Multiple matches found for send_as_lookup in available_tokens. Using the first match."
            )

        send_as = found_items[0]["value"]

    kwargs = _get_kwargs(
        body=body,
        send_as=send_as,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    body: ConversationsOpenRequest,
    send_as: str = "bot",
    send_as_lookup: Any,
) -> Optional[Union[ConversationsOpenResponse, DefaultError]]:
    """Create Group Direct Message

     Create a group direct message. The output of this activity must be passed as input to 'Send Message
    to Channel' activity for sending messages

    Args:
        send_as (str):  Default: 'bot'.
        body (ConversationsOpenRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ConversationsOpenResponse, DefaultError]
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
            send_as=send_as,
            send_as_lookup=send_as_lookup,
        )
    ).parsed
