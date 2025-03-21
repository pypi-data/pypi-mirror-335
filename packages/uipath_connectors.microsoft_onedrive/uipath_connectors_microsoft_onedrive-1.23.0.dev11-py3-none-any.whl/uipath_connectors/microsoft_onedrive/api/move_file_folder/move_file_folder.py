from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response
from ... import errors

from ...models.default_error import DefaultError
from ...models.move_file_folder_request import MoveFileFolderRequest
from ...models.move_file_folder_response import MoveFileFolderResponse


def _get_kwargs(
    *,
    body: MoveFileFolderRequest,
    conflict_behavior: Optional[str] = None,
    reference_folder_id: str,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    params: dict[str, Any] = {}

    params["conflictBehavior"] = conflict_behavior

    params["referenceFolderID"] = reference_folder_id

    params = {k: v for k, v in params.items() if v is not None}

    _kwargs: dict[str, Any] = {
        "method": "patch",
        "url": "/hubs/general/MoveFileFolder",
        "params": params,
    }

    _body = body.to_dict()

    _kwargs["json"] = _body
    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[DefaultError, MoveFileFolderResponse]]:
    if response.status_code == 200:
        response_200 = MoveFileFolderResponse.from_dict(response.json())

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
) -> Response[Union[DefaultError, MoveFileFolderResponse]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: MoveFileFolderRequest,
    conflict_behavior: Optional[str] = None,
    reference_folder_id: str,
    reference_folder_id_lookup: Any,
) -> Response[Union[DefaultError, MoveFileFolderResponse]]:
    """Move File or Folder

     Moves a file or folder to the specified destination folder in OneDrive or SharePoint

    Args:
        conflict_behavior (Optional[str]): If file or folder already exists
        reference_folder_id (str): File or folder ID
        body (MoveFileFolderRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[DefaultError, MoveFileFolderResponse]]
    """

    if not reference_folder_id and reference_folder_id_lookup:
        lookup_response_raw = client.get_httpx_client().request(
            method="get", url="/EventFolderPicker?includeFiles=true"
        )
        lookup_response = lookup_response_raw.json()

        found_items = []
        for item in lookup_response:
            if reference_folder_id_lookup in item["FullName"]:
                found_items.append(item)

        if not found_items:
            raise ValueError(
                "No matches found for reference_folder_id_lookup in EventFolderPicker"
            )
        if len(found_items) > 1:
            print(
                "Warning: Multiple matches found for reference_folder_id_lookup in EventFolderPicker. Using the first match."
            )

        reference_folder_id = found_items[0]["ID"]

    kwargs = _get_kwargs(
        body=body,
        conflict_behavior=conflict_behavior,
        reference_folder_id=reference_folder_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: Union[AuthenticatedClient, Client],
    body: MoveFileFolderRequest,
    conflict_behavior: Optional[str] = None,
    reference_folder_id: str,
    reference_folder_id_lookup: Any,
) -> Optional[Union[DefaultError, MoveFileFolderResponse]]:
    """Move File or Folder

     Moves a file or folder to the specified destination folder in OneDrive or SharePoint

    Args:
        conflict_behavior (Optional[str]): If file or folder already exists
        reference_folder_id (str): File or folder ID
        body (MoveFileFolderRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[DefaultError, MoveFileFolderResponse]
    """

    return sync_detailed(
        client=client,
        body=body,
        conflict_behavior=conflict_behavior,
        reference_folder_id=reference_folder_id,
        reference_folder_id_lookup=reference_folder_id_lookup,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: MoveFileFolderRequest,
    conflict_behavior: Optional[str] = None,
    reference_folder_id: str,
    reference_folder_id_lookup: Any,
) -> Response[Union[DefaultError, MoveFileFolderResponse]]:
    """Move File or Folder

     Moves a file or folder to the specified destination folder in OneDrive or SharePoint

    Args:
        conflict_behavior (Optional[str]): If file or folder already exists
        reference_folder_id (str): File or folder ID
        body (MoveFileFolderRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[DefaultError, MoveFileFolderResponse]]
    """

    if not reference_folder_id and reference_folder_id_lookup:
        lookup_response_raw = await client.get_async_httpx_client().request(
            method="get", url="/EventFolderPicker?includeFiles=true"
        )
        lookup_response = lookup_response_raw.json()

        found_items = []
        for item in lookup_response:
            if reference_folder_id_lookup in item["FullName"]:
                found_items.append(item)

        if not found_items:
            raise ValueError(
                "No matches found for reference_folder_id_lookup in EventFolderPicker"
            )
        if len(found_items) > 1:
            print(
                "Warning: Multiple matches found for reference_folder_id_lookup in EventFolderPicker. Using the first match."
            )

        reference_folder_id = found_items[0]["ID"]

    kwargs = _get_kwargs(
        body=body,
        conflict_behavior=conflict_behavior,
        reference_folder_id=reference_folder_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    body: MoveFileFolderRequest,
    conflict_behavior: Optional[str] = None,
    reference_folder_id: str,
    reference_folder_id_lookup: Any,
) -> Optional[Union[DefaultError, MoveFileFolderResponse]]:
    """Move File or Folder

     Moves a file or folder to the specified destination folder in OneDrive or SharePoint

    Args:
        conflict_behavior (Optional[str]): If file or folder already exists
        reference_folder_id (str): File or folder ID
        body (MoveFileFolderRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[DefaultError, MoveFileFolderResponse]
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
            conflict_behavior=conflict_behavior,
            reference_folder_id=reference_folder_id,
            reference_folder_id_lookup=reference_folder_id_lookup,
        )
    ).parsed
