from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response
from ... import errors

from ...models.default_error import DefaultError
from ...models.get_user_by_email_response import GetUserByEmailResponse


def _get_kwargs(
    users_by_email_id: str,
    *,
    include_locale: Optional[bool] = None,
    user_id: Optional[str] = None,
    by: str = "Email",
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["include_locale"] = include_locale

    params["UserID"] = user_id

    params["By"] = by

    params = {k: v for k, v in params.items() if v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/UsersByEmail/{users_by_email_id}".format(
            users_by_email_id=users_by_email_id,
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[DefaultError, GetUserByEmailResponse]]:
    if response.status_code == 200:
        response_200 = GetUserByEmailResponse.from_dict(response.json())

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
) -> Response[Union[DefaultError, GetUserByEmailResponse]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    users_by_email_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    include_locale: Optional[bool] = None,
    user_id: Optional[str] = None,
    by: str = "Email",
) -> Response[Union[DefaultError, GetUserByEmailResponse]]:
    """Get User

     Get the information of a user in the workspace by providing the email address or user id.

    Args:
        users_by_email_id (str): The email address of the user to retrieve
        include_locale (Optional[bool]): Set this to `true` to receive the locale for this user.
            Defaults to `false`
        user_id (Optional[str]): User ID
        by (str): Get by Default: 'Email'.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[DefaultError, GetUserByEmailResponse]]
    """

    kwargs = _get_kwargs(
        users_by_email_id=users_by_email_id,
        include_locale=include_locale,
        user_id=user_id,
        by=by,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    users_by_email_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    include_locale: Optional[bool] = None,
    user_id: Optional[str] = None,
    by: str = "Email",
) -> Optional[Union[DefaultError, GetUserByEmailResponse]]:
    """Get User

     Get the information of a user in the workspace by providing the email address or user id.

    Args:
        users_by_email_id (str): The email address of the user to retrieve
        include_locale (Optional[bool]): Set this to `true` to receive the locale for this user.
            Defaults to `false`
        user_id (Optional[str]): User ID
        by (str): Get by Default: 'Email'.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[DefaultError, GetUserByEmailResponse]
    """

    return sync_detailed(
        users_by_email_id=users_by_email_id,
        client=client,
        include_locale=include_locale,
        user_id=user_id,
        by=by,
    ).parsed


async def asyncio_detailed(
    users_by_email_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    include_locale: Optional[bool] = None,
    user_id: Optional[str] = None,
    by: str = "Email",
) -> Response[Union[DefaultError, GetUserByEmailResponse]]:
    """Get User

     Get the information of a user in the workspace by providing the email address or user id.

    Args:
        users_by_email_id (str): The email address of the user to retrieve
        include_locale (Optional[bool]): Set this to `true` to receive the locale for this user.
            Defaults to `false`
        user_id (Optional[str]): User ID
        by (str): Get by Default: 'Email'.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[DefaultError, GetUserByEmailResponse]]
    """

    kwargs = _get_kwargs(
        users_by_email_id=users_by_email_id,
        include_locale=include_locale,
        user_id=user_id,
        by=by,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    users_by_email_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    include_locale: Optional[bool] = None,
    user_id: Optional[str] = None,
    by: str = "Email",
) -> Optional[Union[DefaultError, GetUserByEmailResponse]]:
    """Get User

     Get the information of a user in the workspace by providing the email address or user id.

    Args:
        users_by_email_id (str): The email address of the user to retrieve
        include_locale (Optional[bool]): Set this to `true` to receive the locale for this user.
            Defaults to `false`
        user_id (Optional[str]): User ID
        by (str): Get by Default: 'Email'.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[DefaultError, GetUserByEmailResponse]
    """

    return (
        await asyncio_detailed(
            users_by_email_id=users_by_email_id,
            client=client,
            include_locale=include_locale,
            user_id=user_id,
            by=by,
        )
    ).parsed
