from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response
from ... import errors

from ...models.default_error import DefaultError
from ...models.upload_file_body import UploadFileBody
from ...models.upload_file_response import UploadFileResponse


def _get_kwargs(
    *,
    body: UploadFileBody,
    fields: Optional[str] = None,
    elements_vendor_headers: Optional[str] = None,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if elements_vendor_headers is not None:
        headers["elements-vendor-headers"] = elements_vendor_headers

    params: dict[str, Any] = {}

    params["fields"] = fields

    params = {k: v for k, v in params.items() if v is not None}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/upload_file",
        "params": params,
    }

    _body = body.to_multipart()

    _kwargs["files"] = _body

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[DefaultError, UploadFileResponse]]:
    if response.status_code == 200:
        response_200 = UploadFileResponse.from_dict(response.json())

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
) -> Response[Union[DefaultError, UploadFileResponse]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: UploadFileBody,
    fields: Optional[str] = None,
    fields_lookup: Any,
    elements_vendor_headers: Optional[str] = None,
    elements_vendor_headers_lookup: Any,
) -> Response[Union[DefaultError, UploadFileResponse]]:
    """Upload File

     Uploads a file

    Args:
        fields (Optional[str]):
        elements_vendor_headers (Optional[str]):
        body (UploadFileBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[DefaultError, UploadFileResponse]]
    """

    kwargs = _get_kwargs(
        body=body,
        fields=fields,
        elements_vendor_headers=elements_vendor_headers,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: Union[AuthenticatedClient, Client],
    body: UploadFileBody,
    fields: Optional[str] = None,
    fields_lookup: Any,
    elements_vendor_headers: Optional[str] = None,
    elements_vendor_headers_lookup: Any,
) -> Optional[Union[DefaultError, UploadFileResponse]]:
    """Upload File

     Uploads a file

    Args:
        fields (Optional[str]):
        elements_vendor_headers (Optional[str]):
        body (UploadFileBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[DefaultError, UploadFileResponse]
    """

    return sync_detailed(
        client=client,
        body=body,
        fields=fields,
        fields_lookup=fields_lookup,
        elements_vendor_headers=elements_vendor_headers,
        elements_vendor_headers_lookup=elements_vendor_headers_lookup,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: UploadFileBody,
    fields: Optional[str] = None,
    fields_lookup: Any,
    elements_vendor_headers: Optional[str] = None,
    elements_vendor_headers_lookup: Any,
) -> Response[Union[DefaultError, UploadFileResponse]]:
    """Upload File

     Uploads a file

    Args:
        fields (Optional[str]):
        elements_vendor_headers (Optional[str]):
        body (UploadFileBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[DefaultError, UploadFileResponse]]
    """

    kwargs = _get_kwargs(
        body=body,
        fields=fields,
        elements_vendor_headers=elements_vendor_headers,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    body: UploadFileBody,
    fields: Optional[str] = None,
    fields_lookup: Any,
    elements_vendor_headers: Optional[str] = None,
    elements_vendor_headers_lookup: Any,
) -> Optional[Union[DefaultError, UploadFileResponse]]:
    """Upload File

     Uploads a file

    Args:
        fields (Optional[str]):
        elements_vendor_headers (Optional[str]):
        body (UploadFileBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[DefaultError, UploadFileResponse]
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
            fields=fields,
            fields_lookup=fields_lookup,
            elements_vendor_headers=elements_vendor_headers,
            elements_vendor_headers_lookup=elements_vendor_headers_lookup,
        )
    ).parsed
