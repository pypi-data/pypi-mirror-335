from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response
from ... import errors

from ...models.default_error import DefaultError
from ...models.search import Search
import datetime


def _get_kwargs(
    *,
    size_range: Optional[int] = None,
    page_size: Optional[int] = None,
    query: str,
    mdfilters: Optional[str] = None,
    fields: Optional[str] = None,
    content_types: Optional[str] = None,
    type_: Optional[str] = None,
    scope: Optional[str] = None,
    created_at_range_start_date: Optional[datetime.datetime] = None,
    created_at_range_end_date: Optional[datetime.datetime] = None,
    updated_at_range_start_date: Optional[datetime.datetime] = None,
    updated_at_range_end_date: Optional[datetime.datetime] = None,
    direction: Optional[str] = None,
    file_extensions: Optional[str] = None,
    include_recent_shared_links: Optional[bool] = None,
    ancestor_folder_ids: Optional[str] = None,
    owner_user_ids: Optional[str] = None,
    trash_content: Optional[str] = None,
    sort: Optional[str] = None,
    where: Optional[str] = None,
    next_page: Optional[str] = None,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["size_range"] = size_range

    params["pageSize"] = page_size

    params["query"] = query

    params["mdfilters"] = mdfilters

    params["fields"] = fields

    params["content_types"] = content_types

    params["type"] = type_

    params["scope"] = scope

    json_created_at_range_start_date: Optional[str] = None
    if created_at_range_start_date is not None:
        json_created_at_range_start_date = created_at_range_start_date.isoformat()
    params["created_at_range_start_date"] = json_created_at_range_start_date

    json_created_at_range_end_date: Optional[str] = None
    if created_at_range_end_date is not None:
        json_created_at_range_end_date = created_at_range_end_date.isoformat()
    params["created_at_range_end_date"] = json_created_at_range_end_date

    json_updated_at_range_start_date: Optional[str] = None
    if updated_at_range_start_date is not None:
        json_updated_at_range_start_date = updated_at_range_start_date.isoformat()
    params["updated_at_range_start_date"] = json_updated_at_range_start_date

    json_updated_at_range_end_date: Optional[str] = None
    if updated_at_range_end_date is not None:
        json_updated_at_range_end_date = updated_at_range_end_date.isoformat()
    params["updated_at_range_end_date"] = json_updated_at_range_end_date

    params["direction"] = direction

    params["file_extensions"] = file_extensions

    params["include_recent_shared_links"] = include_recent_shared_links

    params["ancestor_folder_ids"] = ancestor_folder_ids

    params["owner_user_ids"] = owner_user_ids

    params["trash_content"] = trash_content

    params["sort"] = sort

    params["where"] = where

    params["nextPage"] = next_page

    params = {k: v for k, v in params.items() if v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/search",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[DefaultError, list["Search"]]]:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_data in _response_200:
            response_200 = Search.from_dict(response_200_data)

            response_200.append(response_200)

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
) -> Response[Union[DefaultError, list["Search"]]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    size_range: Optional[int] = None,
    page_size: Optional[int] = None,
    query: str,
    mdfilters: Optional[str] = None,
    fields: Optional[str] = None,
    content_types: Optional[str] = None,
    type_: Optional[str] = None,
    scope: Optional[str] = None,
    created_at_range_start_date: Optional[datetime.datetime] = None,
    created_at_range_end_date: Optional[datetime.datetime] = None,
    updated_at_range_start_date: Optional[datetime.datetime] = None,
    updated_at_range_end_date: Optional[datetime.datetime] = None,
    direction: Optional[str] = None,
    file_extensions: Optional[str] = None,
    include_recent_shared_links: Optional[bool] = None,
    ancestor_folder_ids: Optional[str] = None,
    ancestor_folder_ids_lookup: Any,
    owner_user_ids: Optional[str] = None,
    trash_content: Optional[str] = None,
    sort: Optional[str] = None,
    where: Optional[str] = None,
    next_page: Optional[str] = None,
) -> Response[Union[DefaultError, list["Search"]]]:
    """Search for Content

     Searches for content in Box based on the filters specified

    Args:
        size_range (Optional[int]): Limits the search results to any items with a size within a
            given file size range. This applied to files and folders. example: 1000000,5000000
        page_size (Optional[int]): The number of resources to return in a given page
        query (str): The string to search for. This query is matched against item names,
            descriptions, text content of files, and various other fields of the different item types.
            Please see developer reference for operators.
        mdfilters (Optional[str]): A list of metadata templates to filter the search results
            by.Required unless query parameter is defined.
            [{"scope":"enterprise","templateKey":"contract","filters":{"category":"online"}}]
        fields (Optional[str]): A comma-separated list of attributes to include in the response.
            This can be used to request fields that are not normally returned in a standard respons
        content_types (Optional[str]): Limits the search results to any items that match the
            search query for a specific part of the file, for example the file description.Content
            types are defined as a comma separated lists of Box recognized content types
        type_ (Optional[str]): Limits the search results to any items of this type. This parameter
            only takes one value. By default the API returns items that match any of these types.
        scope (Optional[str]): Limits the search results to either the files that the user has
            access to, or to files available to the entire enterprise.
        created_at_range_start_date (Optional[datetime.datetime]): Limits the search results to
            any items created at or after this date and time
        created_at_range_end_date (Optional[datetime.datetime]): The end date and time range to
            search for items. If the start date and time is omitted, anything updated before this date
            will be returned.
        updated_at_range_start_date (Optional[datetime.datetime]): Limits the search results to
            any items modified at or after this date and time
        updated_at_range_end_date (Optional[datetime.datetime]):  The end date and time range to
            search for items. If the start date and time is omitted, anything updated before this date
            will be returned.
        direction (Optional[str]): Defines the direction in which search results are ordered. This
            API defaults to returning items in descending (DESC) order unless this parameter is
            explicitly specified.
        file_extensions (Optional[str]): Limits the search results to any files that match any of
            the provided file extensions. This list is a comma-separated list of file extensions
            without the dots.

        include_recent_shared_links (Optional[bool]): Defines whether the search results should
            include any items that the user recently accessed through a shared link.
        ancestor_folder_ids (Optional[str]): Limits the search results to items within the given
            list of folders, defined as a comma separated lists of folder IDs.
        owner_user_ids (Optional[str]): Limits the search results to any items that are owned by
            the given list of owners, defined as a list of comma separated user IDs.
        trash_content (Optional[str]): Determines if the search should look in the trash for
            items.By default, this API only returns search results for items not currently in the
            trash (non_trashed_only).
        sort (Optional[str]): Defines the order in which search results are returned. This API
            defaults to returning items by relevance unless this parameter is explicitly specified.
        where (Optional[str]): The CEQL search expression
        next_page (Optional[str]): The page token from the next page token of the previous page

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[DefaultError, list['Search']]]
    """

    if not ancestor_folder_ids and ancestor_folder_ids_lookup:
        lookup_response_raw = client.get_httpx_client().request(
            method="get", url="/folder_picker_folder"
        )
        lookup_response = lookup_response_raw.json()

        found_items = []
        for item in lookup_response:
            if ancestor_folder_ids_lookup in item["FullName"]:
                found_items.append(item)

        if not found_items:
            raise ValueError(
                "No matches found for ancestor_folder_ids_lookup in folder_picker_folder"
            )
        if len(found_items) > 1:
            print(
                "Warning: Multiple matches found for ancestor_folder_ids_lookup in folder_picker_folder. Using the first match."
            )

        ancestor_folder_ids = found_items[0]["ReferenceID"]

    kwargs = _get_kwargs(
        size_range=size_range,
        page_size=page_size,
        query=query,
        mdfilters=mdfilters,
        fields=fields,
        content_types=content_types,
        type_=type_,
        scope=scope,
        created_at_range_start_date=created_at_range_start_date,
        created_at_range_end_date=created_at_range_end_date,
        updated_at_range_start_date=updated_at_range_start_date,
        updated_at_range_end_date=updated_at_range_end_date,
        direction=direction,
        file_extensions=file_extensions,
        include_recent_shared_links=include_recent_shared_links,
        ancestor_folder_ids=ancestor_folder_ids,
        owner_user_ids=owner_user_ids,
        trash_content=trash_content,
        sort=sort,
        where=where,
        next_page=next_page,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: Union[AuthenticatedClient, Client],
    size_range: Optional[int] = None,
    page_size: Optional[int] = None,
    query: str,
    mdfilters: Optional[str] = None,
    fields: Optional[str] = None,
    content_types: Optional[str] = None,
    type_: Optional[str] = None,
    scope: Optional[str] = None,
    created_at_range_start_date: Optional[datetime.datetime] = None,
    created_at_range_end_date: Optional[datetime.datetime] = None,
    updated_at_range_start_date: Optional[datetime.datetime] = None,
    updated_at_range_end_date: Optional[datetime.datetime] = None,
    direction: Optional[str] = None,
    file_extensions: Optional[str] = None,
    include_recent_shared_links: Optional[bool] = None,
    ancestor_folder_ids: Optional[str] = None,
    ancestor_folder_ids_lookup: Any,
    owner_user_ids: Optional[str] = None,
    trash_content: Optional[str] = None,
    sort: Optional[str] = None,
    where: Optional[str] = None,
    next_page: Optional[str] = None,
) -> Optional[Union[DefaultError, list["Search"]]]:
    """Search for Content

     Searches for content in Box based on the filters specified

    Args:
        size_range (Optional[int]): Limits the search results to any items with a size within a
            given file size range. This applied to files and folders. example: 1000000,5000000
        page_size (Optional[int]): The number of resources to return in a given page
        query (str): The string to search for. This query is matched against item names,
            descriptions, text content of files, and various other fields of the different item types.
            Please see developer reference for operators.
        mdfilters (Optional[str]): A list of metadata templates to filter the search results
            by.Required unless query parameter is defined.
            [{"scope":"enterprise","templateKey":"contract","filters":{"category":"online"}}]
        fields (Optional[str]): A comma-separated list of attributes to include in the response.
            This can be used to request fields that are not normally returned in a standard respons
        content_types (Optional[str]): Limits the search results to any items that match the
            search query for a specific part of the file, for example the file description.Content
            types are defined as a comma separated lists of Box recognized content types
        type_ (Optional[str]): Limits the search results to any items of this type. This parameter
            only takes one value. By default the API returns items that match any of these types.
        scope (Optional[str]): Limits the search results to either the files that the user has
            access to, or to files available to the entire enterprise.
        created_at_range_start_date (Optional[datetime.datetime]): Limits the search results to
            any items created at or after this date and time
        created_at_range_end_date (Optional[datetime.datetime]): The end date and time range to
            search for items. If the start date and time is omitted, anything updated before this date
            will be returned.
        updated_at_range_start_date (Optional[datetime.datetime]): Limits the search results to
            any items modified at or after this date and time
        updated_at_range_end_date (Optional[datetime.datetime]):  The end date and time range to
            search for items. If the start date and time is omitted, anything updated before this date
            will be returned.
        direction (Optional[str]): Defines the direction in which search results are ordered. This
            API defaults to returning items in descending (DESC) order unless this parameter is
            explicitly specified.
        file_extensions (Optional[str]): Limits the search results to any files that match any of
            the provided file extensions. This list is a comma-separated list of file extensions
            without the dots.

        include_recent_shared_links (Optional[bool]): Defines whether the search results should
            include any items that the user recently accessed through a shared link.
        ancestor_folder_ids (Optional[str]): Limits the search results to items within the given
            list of folders, defined as a comma separated lists of folder IDs.
        owner_user_ids (Optional[str]): Limits the search results to any items that are owned by
            the given list of owners, defined as a list of comma separated user IDs.
        trash_content (Optional[str]): Determines if the search should look in the trash for
            items.By default, this API only returns search results for items not currently in the
            trash (non_trashed_only).
        sort (Optional[str]): Defines the order in which search results are returned. This API
            defaults to returning items by relevance unless this parameter is explicitly specified.
        where (Optional[str]): The CEQL search expression
        next_page (Optional[str]): The page token from the next page token of the previous page

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[DefaultError, list['Search']]
    """

    return sync_detailed(
        client=client,
        size_range=size_range,
        page_size=page_size,
        query=query,
        mdfilters=mdfilters,
        fields=fields,
        content_types=content_types,
        type_=type_,
        scope=scope,
        created_at_range_start_date=created_at_range_start_date,
        created_at_range_end_date=created_at_range_end_date,
        updated_at_range_start_date=updated_at_range_start_date,
        updated_at_range_end_date=updated_at_range_end_date,
        direction=direction,
        file_extensions=file_extensions,
        include_recent_shared_links=include_recent_shared_links,
        ancestor_folder_ids=ancestor_folder_ids,
        ancestor_folder_ids_lookup=ancestor_folder_ids_lookup,
        owner_user_ids=owner_user_ids,
        trash_content=trash_content,
        sort=sort,
        where=where,
        next_page=next_page,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    size_range: Optional[int] = None,
    page_size: Optional[int] = None,
    query: str,
    mdfilters: Optional[str] = None,
    fields: Optional[str] = None,
    content_types: Optional[str] = None,
    type_: Optional[str] = None,
    scope: Optional[str] = None,
    created_at_range_start_date: Optional[datetime.datetime] = None,
    created_at_range_end_date: Optional[datetime.datetime] = None,
    updated_at_range_start_date: Optional[datetime.datetime] = None,
    updated_at_range_end_date: Optional[datetime.datetime] = None,
    direction: Optional[str] = None,
    file_extensions: Optional[str] = None,
    include_recent_shared_links: Optional[bool] = None,
    ancestor_folder_ids: Optional[str] = None,
    ancestor_folder_ids_lookup: Any,
    owner_user_ids: Optional[str] = None,
    trash_content: Optional[str] = None,
    sort: Optional[str] = None,
    where: Optional[str] = None,
    next_page: Optional[str] = None,
) -> Response[Union[DefaultError, list["Search"]]]:
    """Search for Content

     Searches for content in Box based on the filters specified

    Args:
        size_range (Optional[int]): Limits the search results to any items with a size within a
            given file size range. This applied to files and folders. example: 1000000,5000000
        page_size (Optional[int]): The number of resources to return in a given page
        query (str): The string to search for. This query is matched against item names,
            descriptions, text content of files, and various other fields of the different item types.
            Please see developer reference for operators.
        mdfilters (Optional[str]): A list of metadata templates to filter the search results
            by.Required unless query parameter is defined.
            [{"scope":"enterprise","templateKey":"contract","filters":{"category":"online"}}]
        fields (Optional[str]): A comma-separated list of attributes to include in the response.
            This can be used to request fields that are not normally returned in a standard respons
        content_types (Optional[str]): Limits the search results to any items that match the
            search query for a specific part of the file, for example the file description.Content
            types are defined as a comma separated lists of Box recognized content types
        type_ (Optional[str]): Limits the search results to any items of this type. This parameter
            only takes one value. By default the API returns items that match any of these types.
        scope (Optional[str]): Limits the search results to either the files that the user has
            access to, or to files available to the entire enterprise.
        created_at_range_start_date (Optional[datetime.datetime]): Limits the search results to
            any items created at or after this date and time
        created_at_range_end_date (Optional[datetime.datetime]): The end date and time range to
            search for items. If the start date and time is omitted, anything updated before this date
            will be returned.
        updated_at_range_start_date (Optional[datetime.datetime]): Limits the search results to
            any items modified at or after this date and time
        updated_at_range_end_date (Optional[datetime.datetime]):  The end date and time range to
            search for items. If the start date and time is omitted, anything updated before this date
            will be returned.
        direction (Optional[str]): Defines the direction in which search results are ordered. This
            API defaults to returning items in descending (DESC) order unless this parameter is
            explicitly specified.
        file_extensions (Optional[str]): Limits the search results to any files that match any of
            the provided file extensions. This list is a comma-separated list of file extensions
            without the dots.

        include_recent_shared_links (Optional[bool]): Defines whether the search results should
            include any items that the user recently accessed through a shared link.
        ancestor_folder_ids (Optional[str]): Limits the search results to items within the given
            list of folders, defined as a comma separated lists of folder IDs.
        owner_user_ids (Optional[str]): Limits the search results to any items that are owned by
            the given list of owners, defined as a list of comma separated user IDs.
        trash_content (Optional[str]): Determines if the search should look in the trash for
            items.By default, this API only returns search results for items not currently in the
            trash (non_trashed_only).
        sort (Optional[str]): Defines the order in which search results are returned. This API
            defaults to returning items by relevance unless this parameter is explicitly specified.
        where (Optional[str]): The CEQL search expression
        next_page (Optional[str]): The page token from the next page token of the previous page

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[DefaultError, list['Search']]]
    """

    if not ancestor_folder_ids and ancestor_folder_ids_lookup:
        lookup_response_raw = await client.get_async_httpx_client().request(
            method="get", url="/folder_picker_folder"
        )
        lookup_response = lookup_response_raw.json()

        found_items = []
        for item in lookup_response:
            if ancestor_folder_ids_lookup in item["FullName"]:
                found_items.append(item)

        if not found_items:
            raise ValueError(
                "No matches found for ancestor_folder_ids_lookup in folder_picker_folder"
            )
        if len(found_items) > 1:
            print(
                "Warning: Multiple matches found for ancestor_folder_ids_lookup in folder_picker_folder. Using the first match."
            )

        ancestor_folder_ids = found_items[0]["ReferenceID"]

    kwargs = _get_kwargs(
        size_range=size_range,
        page_size=page_size,
        query=query,
        mdfilters=mdfilters,
        fields=fields,
        content_types=content_types,
        type_=type_,
        scope=scope,
        created_at_range_start_date=created_at_range_start_date,
        created_at_range_end_date=created_at_range_end_date,
        updated_at_range_start_date=updated_at_range_start_date,
        updated_at_range_end_date=updated_at_range_end_date,
        direction=direction,
        file_extensions=file_extensions,
        include_recent_shared_links=include_recent_shared_links,
        ancestor_folder_ids=ancestor_folder_ids,
        owner_user_ids=owner_user_ids,
        trash_content=trash_content,
        sort=sort,
        where=where,
        next_page=next_page,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    size_range: Optional[int] = None,
    page_size: Optional[int] = None,
    query: str,
    mdfilters: Optional[str] = None,
    fields: Optional[str] = None,
    content_types: Optional[str] = None,
    type_: Optional[str] = None,
    scope: Optional[str] = None,
    created_at_range_start_date: Optional[datetime.datetime] = None,
    created_at_range_end_date: Optional[datetime.datetime] = None,
    updated_at_range_start_date: Optional[datetime.datetime] = None,
    updated_at_range_end_date: Optional[datetime.datetime] = None,
    direction: Optional[str] = None,
    file_extensions: Optional[str] = None,
    include_recent_shared_links: Optional[bool] = None,
    ancestor_folder_ids: Optional[str] = None,
    ancestor_folder_ids_lookup: Any,
    owner_user_ids: Optional[str] = None,
    trash_content: Optional[str] = None,
    sort: Optional[str] = None,
    where: Optional[str] = None,
    next_page: Optional[str] = None,
) -> Optional[Union[DefaultError, list["Search"]]]:
    """Search for Content

     Searches for content in Box based on the filters specified

    Args:
        size_range (Optional[int]): Limits the search results to any items with a size within a
            given file size range. This applied to files and folders. example: 1000000,5000000
        page_size (Optional[int]): The number of resources to return in a given page
        query (str): The string to search for. This query is matched against item names,
            descriptions, text content of files, and various other fields of the different item types.
            Please see developer reference for operators.
        mdfilters (Optional[str]): A list of metadata templates to filter the search results
            by.Required unless query parameter is defined.
            [{"scope":"enterprise","templateKey":"contract","filters":{"category":"online"}}]
        fields (Optional[str]): A comma-separated list of attributes to include in the response.
            This can be used to request fields that are not normally returned in a standard respons
        content_types (Optional[str]): Limits the search results to any items that match the
            search query for a specific part of the file, for example the file description.Content
            types are defined as a comma separated lists of Box recognized content types
        type_ (Optional[str]): Limits the search results to any items of this type. This parameter
            only takes one value. By default the API returns items that match any of these types.
        scope (Optional[str]): Limits the search results to either the files that the user has
            access to, or to files available to the entire enterprise.
        created_at_range_start_date (Optional[datetime.datetime]): Limits the search results to
            any items created at or after this date and time
        created_at_range_end_date (Optional[datetime.datetime]): The end date and time range to
            search for items. If the start date and time is omitted, anything updated before this date
            will be returned.
        updated_at_range_start_date (Optional[datetime.datetime]): Limits the search results to
            any items modified at or after this date and time
        updated_at_range_end_date (Optional[datetime.datetime]):  The end date and time range to
            search for items. If the start date and time is omitted, anything updated before this date
            will be returned.
        direction (Optional[str]): Defines the direction in which search results are ordered. This
            API defaults to returning items in descending (DESC) order unless this parameter is
            explicitly specified.
        file_extensions (Optional[str]): Limits the search results to any files that match any of
            the provided file extensions. This list is a comma-separated list of file extensions
            without the dots.

        include_recent_shared_links (Optional[bool]): Defines whether the search results should
            include any items that the user recently accessed through a shared link.
        ancestor_folder_ids (Optional[str]): Limits the search results to items within the given
            list of folders, defined as a comma separated lists of folder IDs.
        owner_user_ids (Optional[str]): Limits the search results to any items that are owned by
            the given list of owners, defined as a list of comma separated user IDs.
        trash_content (Optional[str]): Determines if the search should look in the trash for
            items.By default, this API only returns search results for items not currently in the
            trash (non_trashed_only).
        sort (Optional[str]): Defines the order in which search results are returned. This API
            defaults to returning items by relevance unless this parameter is explicitly specified.
        where (Optional[str]): The CEQL search expression
        next_page (Optional[str]): The page token from the next page token of the previous page

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[DefaultError, list['Search']]
    """

    return (
        await asyncio_detailed(
            client=client,
            size_range=size_range,
            page_size=page_size,
            query=query,
            mdfilters=mdfilters,
            fields=fields,
            content_types=content_types,
            type_=type_,
            scope=scope,
            created_at_range_start_date=created_at_range_start_date,
            created_at_range_end_date=created_at_range_end_date,
            updated_at_range_start_date=updated_at_range_start_date,
            updated_at_range_end_date=updated_at_range_end_date,
            direction=direction,
            file_extensions=file_extensions,
            include_recent_shared_links=include_recent_shared_links,
            ancestor_folder_ids=ancestor_folder_ids,
            ancestor_folder_ids_lookup=ancestor_folder_ids_lookup,
            owner_user_ids=owner_user_ids,
            trash_content=trash_content,
            sort=sort,
            where=where,
            next_page=next_page,
        )
    ).parsed
