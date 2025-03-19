from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response
from ... import errors

from ...models.copy_file_request import CopyFileRequest
from ...models.copy_file_response import CopyFileResponse
from ...models.default_error import DefaultError


def _get_kwargs(
    file_id: str,
    *,
    body: CopyFileRequest,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/files/{file_id}/copy".format(
            file_id=file_id,
        ),
    }

    _body = body.to_dict()

    _kwargs["json"] = _body
    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[CopyFileResponse, DefaultError]]:
    if response.status_code == 200:
        response_200 = CopyFileResponse.from_dict(response.json())

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
) -> Response[Union[CopyFileResponse, DefaultError]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    file_id: str,
    file_id_lookup: Any,
    *,
    client: Union[AuthenticatedClient, Client],
    body: CopyFileRequest,
) -> Response[Union[CopyFileResponse, DefaultError]]:
    """Copy File

      Creates a copy of an existing file in Box

    Args:
        file_id (str):
        body (CopyFileRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[CopyFileResponse, DefaultError]]
    """

    if not file_id and file_id_lookup:
        lookup_response_raw = client.get_httpx_client().request(
            method="get", url="/folder_picker_folder"
        )
        lookup_response = lookup_response_raw.json()

        found_items = []
        for item in lookup_response:
            if file_id_lookup in item["FullName"]:
                found_items.append(item)

        if not found_items:
            raise ValueError(
                "No matches found for file_id_lookup in folder_picker_folder"
            )
        if len(found_items) > 1:
            print(
                "Warning: Multiple matches found for file_id_lookup in folder_picker_folder. Using the first match."
            )

        file_id = found_items[0]["ReferenceID"]

    kwargs = _get_kwargs(
        file_id=file_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    file_id: str,
    file_id_lookup: Any,
    *,
    client: Union[AuthenticatedClient, Client],
    body: CopyFileRequest,
) -> Optional[Union[CopyFileResponse, DefaultError]]:
    """Copy File

      Creates a copy of an existing file in Box

    Args:
        file_id (str):
        body (CopyFileRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[CopyFileResponse, DefaultError]
    """

    return sync_detailed(
        file_id=file_id,
        file_id_lookup=file_id_lookup,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    file_id: str,
    file_id_lookup: Any,
    *,
    client: Union[AuthenticatedClient, Client],
    body: CopyFileRequest,
) -> Response[Union[CopyFileResponse, DefaultError]]:
    """Copy File

      Creates a copy of an existing file in Box

    Args:
        file_id (str):
        body (CopyFileRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[CopyFileResponse, DefaultError]]
    """

    if not file_id and file_id_lookup:
        lookup_response_raw = await client.get_async_httpx_client().request(
            method="get", url="/folder_picker_folder"
        )
        lookup_response = lookup_response_raw.json()

        found_items = []
        for item in lookup_response:
            if file_id_lookup in item["FullName"]:
                found_items.append(item)

        if not found_items:
            raise ValueError(
                "No matches found for file_id_lookup in folder_picker_folder"
            )
        if len(found_items) > 1:
            print(
                "Warning: Multiple matches found for file_id_lookup in folder_picker_folder. Using the first match."
            )

        file_id = found_items[0]["ReferenceID"]

    kwargs = _get_kwargs(
        file_id=file_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    file_id: str,
    file_id_lookup: Any,
    *,
    client: Union[AuthenticatedClient, Client],
    body: CopyFileRequest,
) -> Optional[Union[CopyFileResponse, DefaultError]]:
    """Copy File

      Creates a copy of an existing file in Box

    Args:
        file_id (str):
        body (CopyFileRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[CopyFileResponse, DefaultError]
    """

    return (
        await asyncio_detailed(
            file_id=file_id,
            file_id_lookup=file_id_lookup,
            client=client,
            body=body,
        )
    ).parsed
