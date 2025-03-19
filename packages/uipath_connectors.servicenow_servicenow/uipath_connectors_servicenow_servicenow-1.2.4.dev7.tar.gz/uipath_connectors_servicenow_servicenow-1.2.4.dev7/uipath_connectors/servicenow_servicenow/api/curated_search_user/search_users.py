from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response
from ... import errors

from ...models.default_error import DefaultError
from ...models.search_users import SearchUsers


def _get_kwargs(
    *,
    page: Optional[str] = None,
    email: Optional[str] = None,
    fields: Optional[str] = None,
    next_page: Optional[str] = None,
    page_size: Optional[int] = None,
    user_name: Optional[str] = None,
    where: Optional[str] = None,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["Page"] = page

    params["email"] = email

    params["fields"] = fields

    params["nextPage"] = next_page

    params["pageSize"] = page_size

    params["user_name"] = user_name

    params["where"] = where

    params = {k: v for k, v in params.items() if v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/curated_search_user",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[DefaultError, list["SearchUsers"]]]:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for componentsschemas_search_users_list_item_data in _response_200:
            componentsschemas_search_users_list_item = SearchUsers.from_dict(
                componentsschemas_search_users_list_item_data
            )

            response_200.append(componentsschemas_search_users_list_item)

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
) -> Response[Union[DefaultError, list["SearchUsers"]]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    page: Optional[str] = None,
    page_lookup: Any,
    email: Optional[str] = None,
    email_lookup: Any,
    fields: Optional[str] = None,
    fields_lookup: Any,
    next_page: Optional[str] = None,
    next_page_lookup: Any,
    page_size: Optional[int] = None,
    page_size_lookup: Any,
    user_name: Optional[str] = None,
    user_name_lookup: Any,
    where: Optional[str] = None,
    where_lookup: Any,
) -> Response[Union[DefaultError, list["SearchUsers"]]]:
    """Search Users by Email or Name

     Search Users by Email or Name

    Args:
        page (Optional[str]):
        email (Optional[str]):
        fields (Optional[str]):
        next_page (Optional[str]):
        page_size (Optional[int]):
        user_name (Optional[str]):
        where (Optional[str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[DefaultError, list['SearchUsers']]]
    """

    kwargs = _get_kwargs(
        page=page,
        email=email,
        fields=fields,
        next_page=next_page,
        page_size=page_size,
        user_name=user_name,
        where=where,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: Union[AuthenticatedClient, Client],
    page: Optional[str] = None,
    page_lookup: Any,
    email: Optional[str] = None,
    email_lookup: Any,
    fields: Optional[str] = None,
    fields_lookup: Any,
    next_page: Optional[str] = None,
    next_page_lookup: Any,
    page_size: Optional[int] = None,
    page_size_lookup: Any,
    user_name: Optional[str] = None,
    user_name_lookup: Any,
    where: Optional[str] = None,
    where_lookup: Any,
) -> Optional[Union[DefaultError, list["SearchUsers"]]]:
    """Search Users by Email or Name

     Search Users by Email or Name

    Args:
        page (Optional[str]):
        email (Optional[str]):
        fields (Optional[str]):
        next_page (Optional[str]):
        page_size (Optional[int]):
        user_name (Optional[str]):
        where (Optional[str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[DefaultError, list['SearchUsers']]
    """

    return sync_detailed(
        client=client,
        page=page,
        page_lookup=page_lookup,
        email=email,
        email_lookup=email_lookup,
        fields=fields,
        fields_lookup=fields_lookup,
        next_page=next_page,
        next_page_lookup=next_page_lookup,
        page_size=page_size,
        page_size_lookup=page_size_lookup,
        user_name=user_name,
        user_name_lookup=user_name_lookup,
        where=where,
        where_lookup=where_lookup,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    page: Optional[str] = None,
    page_lookup: Any,
    email: Optional[str] = None,
    email_lookup: Any,
    fields: Optional[str] = None,
    fields_lookup: Any,
    next_page: Optional[str] = None,
    next_page_lookup: Any,
    page_size: Optional[int] = None,
    page_size_lookup: Any,
    user_name: Optional[str] = None,
    user_name_lookup: Any,
    where: Optional[str] = None,
    where_lookup: Any,
) -> Response[Union[DefaultError, list["SearchUsers"]]]:
    """Search Users by Email or Name

     Search Users by Email or Name

    Args:
        page (Optional[str]):
        email (Optional[str]):
        fields (Optional[str]):
        next_page (Optional[str]):
        page_size (Optional[int]):
        user_name (Optional[str]):
        where (Optional[str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[DefaultError, list['SearchUsers']]]
    """

    kwargs = _get_kwargs(
        page=page,
        email=email,
        fields=fields,
        next_page=next_page,
        page_size=page_size,
        user_name=user_name,
        where=where,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    page: Optional[str] = None,
    page_lookup: Any,
    email: Optional[str] = None,
    email_lookup: Any,
    fields: Optional[str] = None,
    fields_lookup: Any,
    next_page: Optional[str] = None,
    next_page_lookup: Any,
    page_size: Optional[int] = None,
    page_size_lookup: Any,
    user_name: Optional[str] = None,
    user_name_lookup: Any,
    where: Optional[str] = None,
    where_lookup: Any,
) -> Optional[Union[DefaultError, list["SearchUsers"]]]:
    """Search Users by Email or Name

     Search Users by Email or Name

    Args:
        page (Optional[str]):
        email (Optional[str]):
        fields (Optional[str]):
        next_page (Optional[str]):
        page_size (Optional[int]):
        user_name (Optional[str]):
        where (Optional[str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[DefaultError, list['SearchUsers']]
    """

    return (
        await asyncio_detailed(
            client=client,
            page=page,
            page_lookup=page_lookup,
            email=email,
            email_lookup=email_lookup,
            fields=fields,
            fields_lookup=fields_lookup,
            next_page=next_page,
            next_page_lookup=next_page_lookup,
            page_size=page_size,
            page_size_lookup=page_size_lookup,
            user_name=user_name,
            user_name_lookup=user_name_lookup,
            where=where,
            where_lookup=where_lookup,
        )
    ).parsed
