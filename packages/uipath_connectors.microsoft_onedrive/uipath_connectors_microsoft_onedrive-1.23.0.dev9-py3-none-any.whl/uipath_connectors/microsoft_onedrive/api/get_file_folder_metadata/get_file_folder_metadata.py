from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response
from ... import errors

from ...models.default_error import DefaultError
from ...models.get_file_folder_metadata_response import GetFileFolderMetadataResponse


def _get_kwargs(
    reference_id: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/GetFileFolderMetadata/{reference_id}".format(
            reference_id=reference_id,
        ),
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[DefaultError, GetFileFolderMetadataResponse]]:
    if response.status_code == 200:
        response_200 = GetFileFolderMetadataResponse.from_dict(response.json())

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
) -> Response[Union[DefaultError, GetFileFolderMetadataResponse]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    reference_id: str,
    reference_id_lookup: Any,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[Union[DefaultError, GetFileFolderMetadataResponse]]:
    """Get File or Folder Metadata

     Fetch metadata for a file from OneDrive & SharePoint

    Args:
        reference_id (str): File of folder to get metadata

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[DefaultError, GetFileFolderMetadataResponse]]
    """

    if not reference_id and reference_id_lookup:
        lookup_response_raw = client.get_httpx_client().request(
            method="get", url="/EventFolderPicker?includeFiles=true"
        )
        lookup_response = lookup_response_raw.json()

        found_items = []
        for item in lookup_response:
            if reference_id_lookup in item["FullName"]:
                found_items.append(item)

        if not found_items:
            raise ValueError(
                "No matches found for reference_id_lookup in EventFolderPicker"
            )
        if len(found_items) > 1:
            print(
                "Warning: Multiple matches found for reference_id_lookup in EventFolderPicker. Using the first match."
            )

        reference_id = found_items[0]["ID"]

    kwargs = _get_kwargs(
        reference_id=reference_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    reference_id: str,
    reference_id_lookup: Any,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[Union[DefaultError, GetFileFolderMetadataResponse]]:
    """Get File or Folder Metadata

     Fetch metadata for a file from OneDrive & SharePoint

    Args:
        reference_id (str): File of folder to get metadata

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[DefaultError, GetFileFolderMetadataResponse]
    """

    return sync_detailed(
        reference_id=reference_id,
        reference_id_lookup=reference_id_lookup,
        client=client,
    ).parsed


async def asyncio_detailed(
    reference_id: str,
    reference_id_lookup: Any,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[Union[DefaultError, GetFileFolderMetadataResponse]]:
    """Get File or Folder Metadata

     Fetch metadata for a file from OneDrive & SharePoint

    Args:
        reference_id (str): File of folder to get metadata

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[DefaultError, GetFileFolderMetadataResponse]]
    """

    if not reference_id and reference_id_lookup:
        lookup_response_raw = await client.get_async_httpx_client().request(
            method="get", url="/EventFolderPicker?includeFiles=true"
        )
        lookup_response = lookup_response_raw.json()

        found_items = []
        for item in lookup_response:
            if reference_id_lookup in item["FullName"]:
                found_items.append(item)

        if not found_items:
            raise ValueError(
                "No matches found for reference_id_lookup in EventFolderPicker"
            )
        if len(found_items) > 1:
            print(
                "Warning: Multiple matches found for reference_id_lookup in EventFolderPicker. Using the first match."
            )

        reference_id = found_items[0]["ID"]

    kwargs = _get_kwargs(
        reference_id=reference_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    reference_id: str,
    reference_id_lookup: Any,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[Union[DefaultError, GetFileFolderMetadataResponse]]:
    """Get File or Folder Metadata

     Fetch metadata for a file from OneDrive & SharePoint

    Args:
        reference_id (str): File of folder to get metadata

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[DefaultError, GetFileFolderMetadataResponse]
    """

    return (
        await asyncio_detailed(
            reference_id=reference_id,
            reference_id_lookup=reference_id_lookup,
            client=client,
        )
    ).parsed
