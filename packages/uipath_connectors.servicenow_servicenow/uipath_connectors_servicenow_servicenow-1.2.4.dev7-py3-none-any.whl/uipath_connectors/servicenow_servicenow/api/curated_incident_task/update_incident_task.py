from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response
from ... import errors

from ...models.default_error import DefaultError
from ...models.update_incident_task_request import UpdateIncidentTaskRequest
from ...models.update_incident_task_response import UpdateIncidentTaskResponse


def _get_kwargs(
    curated_incident_task_id: str,
    *,
    body: UpdateIncidentTaskRequest,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "patch",
        "url": "/curated_incident_task/{curated_incident_task_id}".format(
            curated_incident_task_id=curated_incident_task_id,
        ),
    }

    _body = body.to_dict()

    _kwargs["json"] = _body
    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[DefaultError, UpdateIncidentTaskResponse]]:
    if response.status_code == 200:
        response_200 = UpdateIncidentTaskResponse.from_dict(response.json())

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
) -> Response[Union[DefaultError, UpdateIncidentTaskResponse]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    curated_incident_task_id: str,
    curated_incident_task_id_lookup: Any,
    *,
    client: Union[AuthenticatedClient, Client],
    body: UpdateIncidentTaskRequest,
) -> Response[Union[DefaultError, UpdateIncidentTaskResponse]]:
    """Update Incident Task

     Update an incident task.

    Args:
        curated_incident_task_id (str):
        body (UpdateIncidentTaskRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[DefaultError, UpdateIncidentTaskResponse]]
    """

    if not curated_incident_task_id and curated_incident_task_id_lookup:
        filter = curated_incident_task_id_lookup
        lookup_response_raw = client.get_httpx_client().request(
            method="get", url=f"/incident_task?where=number like '{filter}'"
        )
        lookup_response = lookup_response_raw.json()

        found_items = lookup_response

        if not found_items:
            raise ValueError(
                "No matches found for curated_incident_task_id_lookup in incident_task"
            )
        if len(found_items) > 1:
            print(
                "Warning: Multiple matches found for curated_incident_task_id_lookup in incident_task. Using the first match."
            )

        curated_incident_task_id = found_items[0]["sys_id"]

    kwargs = _get_kwargs(
        curated_incident_task_id=curated_incident_task_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    curated_incident_task_id: str,
    curated_incident_task_id_lookup: Any,
    *,
    client: Union[AuthenticatedClient, Client],
    body: UpdateIncidentTaskRequest,
) -> Optional[Union[DefaultError, UpdateIncidentTaskResponse]]:
    """Update Incident Task

     Update an incident task.

    Args:
        curated_incident_task_id (str):
        body (UpdateIncidentTaskRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[DefaultError, UpdateIncidentTaskResponse]
    """

    return sync_detailed(
        curated_incident_task_id=curated_incident_task_id,
        curated_incident_task_id_lookup=curated_incident_task_id_lookup,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    curated_incident_task_id: str,
    curated_incident_task_id_lookup: Any,
    *,
    client: Union[AuthenticatedClient, Client],
    body: UpdateIncidentTaskRequest,
) -> Response[Union[DefaultError, UpdateIncidentTaskResponse]]:
    """Update Incident Task

     Update an incident task.

    Args:
        curated_incident_task_id (str):
        body (UpdateIncidentTaskRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[DefaultError, UpdateIncidentTaskResponse]]
    """

    if not curated_incident_task_id and curated_incident_task_id_lookup:
        filter = curated_incident_task_id_lookup
        lookup_response_raw = await client.get_async_httpx_client().request(
            method="get", url=f"/incident_task?where=number like '{filter}'"
        )
        lookup_response = lookup_response_raw.json()

        found_items = lookup_response

        if not found_items:
            raise ValueError(
                "No matches found for curated_incident_task_id_lookup in incident_task"
            )
        if len(found_items) > 1:
            print(
                "Warning: Multiple matches found for curated_incident_task_id_lookup in incident_task. Using the first match."
            )

        curated_incident_task_id = found_items[0]["sys_id"]

    kwargs = _get_kwargs(
        curated_incident_task_id=curated_incident_task_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    curated_incident_task_id: str,
    curated_incident_task_id_lookup: Any,
    *,
    client: Union[AuthenticatedClient, Client],
    body: UpdateIncidentTaskRequest,
) -> Optional[Union[DefaultError, UpdateIncidentTaskResponse]]:
    """Update Incident Task

     Update an incident task.

    Args:
        curated_incident_task_id (str):
        body (UpdateIncidentTaskRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[DefaultError, UpdateIncidentTaskResponse]
    """

    return (
        await asyncio_detailed(
            curated_incident_task_id=curated_incident_task_id,
            curated_incident_task_id_lookup=curated_incident_task_id_lookup,
            client=client,
            body=body,
        )
    ).parsed
