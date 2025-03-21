from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response
from ... import errors

from ...models.default_error import DefaultError
from ...models.get_folder_items import GetFolderItems


def _get_kwargs(
    folder_id: str,
    *,
    where: Optional[str] = None,
    page_size: Optional[int] = None,
    type_: Optional[str] = "Files and Folders",
    next_page: Optional[str] = None,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["where"] = where

    params["pageSize"] = page_size

    params["type"] = type_

    params["nextPage"] = next_page

    params = {k: v for k, v in params.items() if v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/folders/{folder_id}/items".format(
            folder_id=folder_id,
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[DefaultError, list["GetFolderItems"]]]:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = GetFolderItems.from_dict(response_200_item_data)

            response_200.append(response_200_item)

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
) -> Response[Union[DefaultError, list["GetFolderItems"]]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    folder_id: str,
    folder_id_lookup: Any,
    *,
    client: Union[AuthenticatedClient, Client],
    where: Optional[str] = None,
    page_size: Optional[int] = None,
    type_: Optional[str] = "Files and Folders",
    next_page: Optional[str] = None,
) -> Response[Union[DefaultError, list["GetFolderItems"]]]:
    """Get Folder Items

     Lists items contained in a parent folder in Box

    Args:
        folder_id (str): The folder_id
        where (Optional[str]): The CEQL search expression
        page_size (Optional[int]): The number of resources to return in a given page
        type_ (Optional[str]): content type Default: 'Files and Folders'.
        next_page (Optional[str]): The next page cursor, taken from the response header:
            `elements-next-page-token`

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[DefaultError, list['GetFolderItems']]]
    """

    if not folder_id and folder_id_lookup:
        lookup_response_raw = client.get_httpx_client().request(
            method="get", url="/folder_picker_folder"
        )
        lookup_response = lookup_response_raw.json()

        found_items = []
        for item in lookup_response:
            if folder_id_lookup in item["FullName"]:
                found_items.append(item)

        if not found_items:
            raise ValueError(
                "No matches found for folder_id_lookup in folder_picker_folder"
            )
        if len(found_items) > 1:
            print(
                "Warning: Multiple matches found for folder_id_lookup in folder_picker_folder. Using the first match."
            )

        folder_id = found_items[0]["ReferenceID"]

    kwargs = _get_kwargs(
        folder_id=folder_id,
        where=where,
        page_size=page_size,
        type_=type_,
        next_page=next_page,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    folder_id: str,
    folder_id_lookup: Any,
    *,
    client: Union[AuthenticatedClient, Client],
    where: Optional[str] = None,
    page_size: Optional[int] = None,
    type_: Optional[str] = "Files and Folders",
    next_page: Optional[str] = None,
) -> Optional[Union[DefaultError, list["GetFolderItems"]]]:
    """Get Folder Items

     Lists items contained in a parent folder in Box

    Args:
        folder_id (str): The folder_id
        where (Optional[str]): The CEQL search expression
        page_size (Optional[int]): The number of resources to return in a given page
        type_ (Optional[str]): content type Default: 'Files and Folders'.
        next_page (Optional[str]): The next page cursor, taken from the response header:
            `elements-next-page-token`

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[DefaultError, list['GetFolderItems']]
    """

    return sync_detailed(
        folder_id=folder_id,
        folder_id_lookup=folder_id_lookup,
        client=client,
        where=where,
        page_size=page_size,
        type_=type_,
        next_page=next_page,
    ).parsed


async def asyncio_detailed(
    folder_id: str,
    folder_id_lookup: Any,
    *,
    client: Union[AuthenticatedClient, Client],
    where: Optional[str] = None,
    page_size: Optional[int] = None,
    type_: Optional[str] = "Files and Folders",
    next_page: Optional[str] = None,
) -> Response[Union[DefaultError, list["GetFolderItems"]]]:
    """Get Folder Items

     Lists items contained in a parent folder in Box

    Args:
        folder_id (str): The folder_id
        where (Optional[str]): The CEQL search expression
        page_size (Optional[int]): The number of resources to return in a given page
        type_ (Optional[str]): content type Default: 'Files and Folders'.
        next_page (Optional[str]): The next page cursor, taken from the response header:
            `elements-next-page-token`

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[DefaultError, list['GetFolderItems']]]
    """

    if not folder_id and folder_id_lookup:
        lookup_response_raw = await client.get_async_httpx_client().request(
            method="get", url="/folder_picker_folder"
        )
        lookup_response = lookup_response_raw.json()

        found_items = []
        for item in lookup_response:
            if folder_id_lookup in item["FullName"]:
                found_items.append(item)

        if not found_items:
            raise ValueError(
                "No matches found for folder_id_lookup in folder_picker_folder"
            )
        if len(found_items) > 1:
            print(
                "Warning: Multiple matches found for folder_id_lookup in folder_picker_folder. Using the first match."
            )

        folder_id = found_items[0]["ReferenceID"]

    kwargs = _get_kwargs(
        folder_id=folder_id,
        where=where,
        page_size=page_size,
        type_=type_,
        next_page=next_page,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    folder_id: str,
    folder_id_lookup: Any,
    *,
    client: Union[AuthenticatedClient, Client],
    where: Optional[str] = None,
    page_size: Optional[int] = None,
    type_: Optional[str] = "Files and Folders",
    next_page: Optional[str] = None,
) -> Optional[Union[DefaultError, list["GetFolderItems"]]]:
    """Get Folder Items

     Lists items contained in a parent folder in Box

    Args:
        folder_id (str): The folder_id
        where (Optional[str]): The CEQL search expression
        page_size (Optional[int]): The number of resources to return in a given page
        type_ (Optional[str]): content type Default: 'Files and Folders'.
        next_page (Optional[str]): The next page cursor, taken from the response header:
            `elements-next-page-token`

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[DefaultError, list['GetFolderItems']]
    """

    return (
        await asyncio_detailed(
            folder_id=folder_id,
            folder_id_lookup=folder_id_lookup,
            client=client,
            where=where,
            page_size=page_size,
            type_=type_,
            next_page=next_page,
        )
    ).parsed
