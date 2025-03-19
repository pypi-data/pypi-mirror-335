from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response
from ... import errors

from ...models.default_error import DefaultError
from ...models.get_conversation_info_response import GetConversationInfoResponse


def _get_kwargs(
    conversations_info_id: str,
    *,
    include_locale: Optional[bool] = None,
    include_num_members: Optional[bool] = None,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["include_locale"] = include_locale

    params["include_num_members"] = include_num_members

    params = {k: v for k, v in params.items() if v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/ConversationsInfo/{conversations_info_id}".format(
            conversations_info_id=conversations_info_id,
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[DefaultError, GetConversationInfoResponse]]:
    if response.status_code == 200:
        response_200 = GetConversationInfoResponse.from_dict(response.json())

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
) -> Response[Union[DefaultError, GetConversationInfoResponse]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    conversations_info_id: str,
    conversations_info_id_lookup: Any,
    *,
    client: Union[AuthenticatedClient, Client],
    include_locale: Optional[bool] = None,
    include_locale_lookup: Any,
    include_num_members: Optional[bool] = None,
    include_num_members_lookup: Any,
) -> Response[Union[DefaultError, GetConversationInfoResponse]]:
    """Get Channel Info

     Retrieve the information of a public or private channel

    Args:
        conversations_info_id (str):
        include_locale (Optional[bool]):
        include_num_members (Optional[bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[DefaultError, GetConversationInfoResponse]]
    """

    if not conversations_info_id and conversations_info_id_lookup:
        lookup_response_raw = client.get_httpx_client().request(
            method="get", url="/curated_channels?fields=id,name"
        )
        lookup_response = lookup_response_raw.json()

        found_items = []
        for item in lookup_response:
            if (
                conversations_info_id_lookup in item["name"]
                or conversations_info_id_lookup in item["id"]
            ):
                found_items.append(item)

        if not found_items:
            raise ValueError(
                "No matches found for conversations_info_id_lookup in curated_channels"
            )
        if len(found_items) > 1:
            print(
                "Warning: Multiple matches found for conversations_info_id_lookup in curated_channels. Using the first match."
            )

        conversations_info_id = found_items[0]["id"]

    kwargs = _get_kwargs(
        conversations_info_id=conversations_info_id,
        include_locale=include_locale,
        include_num_members=include_num_members,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    conversations_info_id: str,
    conversations_info_id_lookup: Any,
    *,
    client: Union[AuthenticatedClient, Client],
    include_locale: Optional[bool] = None,
    include_locale_lookup: Any,
    include_num_members: Optional[bool] = None,
    include_num_members_lookup: Any,
) -> Optional[Union[DefaultError, GetConversationInfoResponse]]:
    """Get Channel Info

     Retrieve the information of a public or private channel

    Args:
        conversations_info_id (str):
        include_locale (Optional[bool]):
        include_num_members (Optional[bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[DefaultError, GetConversationInfoResponse]
    """

    return sync_detailed(
        conversations_info_id=conversations_info_id,
        conversations_info_id_lookup=conversations_info_id_lookup,
        client=client,
        include_locale=include_locale,
        include_locale_lookup=include_locale_lookup,
        include_num_members=include_num_members,
        include_num_members_lookup=include_num_members_lookup,
    ).parsed


async def asyncio_detailed(
    conversations_info_id: str,
    conversations_info_id_lookup: Any,
    *,
    client: Union[AuthenticatedClient, Client],
    include_locale: Optional[bool] = None,
    include_locale_lookup: Any,
    include_num_members: Optional[bool] = None,
    include_num_members_lookup: Any,
) -> Response[Union[DefaultError, GetConversationInfoResponse]]:
    """Get Channel Info

     Retrieve the information of a public or private channel

    Args:
        conversations_info_id (str):
        include_locale (Optional[bool]):
        include_num_members (Optional[bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[DefaultError, GetConversationInfoResponse]]
    """

    if not conversations_info_id and conversations_info_id_lookup:
        lookup_response_raw = await client.get_async_httpx_client().request(
            method="get", url="/curated_channels?fields=id,name"
        )
        lookup_response = lookup_response_raw.json()

        found_items = []
        for item in lookup_response:
            if (
                conversations_info_id_lookup in item["name"]
                or conversations_info_id_lookup in item["id"]
            ):
                found_items.append(item)

        if not found_items:
            raise ValueError(
                "No matches found for conversations_info_id_lookup in curated_channels"
            )
        if len(found_items) > 1:
            print(
                "Warning: Multiple matches found for conversations_info_id_lookup in curated_channels. Using the first match."
            )

        conversations_info_id = found_items[0]["id"]

    kwargs = _get_kwargs(
        conversations_info_id=conversations_info_id,
        include_locale=include_locale,
        include_num_members=include_num_members,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    conversations_info_id: str,
    conversations_info_id_lookup: Any,
    *,
    client: Union[AuthenticatedClient, Client],
    include_locale: Optional[bool] = None,
    include_locale_lookup: Any,
    include_num_members: Optional[bool] = None,
    include_num_members_lookup: Any,
) -> Optional[Union[DefaultError, GetConversationInfoResponse]]:
    """Get Channel Info

     Retrieve the information of a public or private channel

    Args:
        conversations_info_id (str):
        include_locale (Optional[bool]):
        include_num_members (Optional[bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[DefaultError, GetConversationInfoResponse]
    """

    return (
        await asyncio_detailed(
            conversations_info_id=conversations_info_id,
            conversations_info_id_lookup=conversations_info_id_lookup,
            client=client,
            include_locale=include_locale,
            include_locale_lookup=include_locale_lookup,
            include_num_members=include_num_members,
            include_num_members_lookup=include_num_members_lookup,
        )
    ).parsed
