from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response
from ... import errors

from ...models.default_error import DefaultError
from ...models.get_curated_file_and_folders import GetCuratedFileAndFolders


def _get_kwargs(
    *,
    drive_id: Optional[str] = None,
    fields: Optional[str] = None,
    id: Optional[str] = None,
    next_page: Optional[str] = None,
    page_size: Optional[int] = None,
    path: Optional[str] = None,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["driveID"] = drive_id

    params["fields"] = fields

    params["id"] = id

    params["nextPage"] = next_page

    params["pageSize"] = page_size

    params["path"] = path

    params = {k: v for k, v in params.items() if v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/CuratedFileAndFolders",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[DefaultError, list["GetCuratedFileAndFolders"]]]:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for (
            componentsschemasget_curated_file_and_folders_list_item_data
        ) in _response_200:
            componentsschemasget_curated_file_and_folders_list_item = (
                GetCuratedFileAndFolders.from_dict(
                    componentsschemasget_curated_file_and_folders_list_item_data
                )
            )

            response_200.append(componentsschemasget_curated_file_and_folders_list_item)

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
) -> Response[Union[DefaultError, list["GetCuratedFileAndFolders"]]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    drive_id: Optional[str] = None,
    drive_id_lookup: Any,
    fields: Optional[str] = None,
    fields_lookup: Any,
    id: Optional[str] = None,
    id_lookup: Any,
    next_page: Optional[str] = None,
    next_page_lookup: Any,
    page_size: Optional[int] = None,
    page_size_lookup: Any,
    path: Optional[str] = None,
    path_lookup: Any,
) -> Response[Union[DefaultError, list["GetCuratedFileAndFolders"]]]:
    """Get a list of CuratedFileAndFolders that are contained within a specified folder by path or ID.

    Args:
        drive_id (Optional[str]):
        fields (Optional[str]):
        id (Optional[str]):
        next_page (Optional[str]):
        page_size (Optional[int]):
        path (Optional[str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[DefaultError, list['GetCuratedFileAndFolders']]]
    """

    kwargs = _get_kwargs(
        drive_id=drive_id,
        fields=fields,
        id=id,
        next_page=next_page,
        page_size=page_size,
        path=path,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: Union[AuthenticatedClient, Client],
    drive_id: Optional[str] = None,
    drive_id_lookup: Any,
    fields: Optional[str] = None,
    fields_lookup: Any,
    id: Optional[str] = None,
    id_lookup: Any,
    next_page: Optional[str] = None,
    next_page_lookup: Any,
    page_size: Optional[int] = None,
    page_size_lookup: Any,
    path: Optional[str] = None,
    path_lookup: Any,
) -> Optional[Union[DefaultError, list["GetCuratedFileAndFolders"]]]:
    """Get a list of CuratedFileAndFolders that are contained within a specified folder by path or ID.

    Args:
        drive_id (Optional[str]):
        fields (Optional[str]):
        id (Optional[str]):
        next_page (Optional[str]):
        page_size (Optional[int]):
        path (Optional[str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[DefaultError, list['GetCuratedFileAndFolders']]
    """

    return sync_detailed(
        client=client,
        drive_id=drive_id,
        drive_id_lookup=drive_id_lookup,
        fields=fields,
        fields_lookup=fields_lookup,
        id=id,
        id_lookup=id_lookup,
        next_page=next_page,
        next_page_lookup=next_page_lookup,
        page_size=page_size,
        page_size_lookup=page_size_lookup,
        path=path,
        path_lookup=path_lookup,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    drive_id: Optional[str] = None,
    drive_id_lookup: Any,
    fields: Optional[str] = None,
    fields_lookup: Any,
    id: Optional[str] = None,
    id_lookup: Any,
    next_page: Optional[str] = None,
    next_page_lookup: Any,
    page_size: Optional[int] = None,
    page_size_lookup: Any,
    path: Optional[str] = None,
    path_lookup: Any,
) -> Response[Union[DefaultError, list["GetCuratedFileAndFolders"]]]:
    """Get a list of CuratedFileAndFolders that are contained within a specified folder by path or ID.

    Args:
        drive_id (Optional[str]):
        fields (Optional[str]):
        id (Optional[str]):
        next_page (Optional[str]):
        page_size (Optional[int]):
        path (Optional[str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[DefaultError, list['GetCuratedFileAndFolders']]]
    """

    kwargs = _get_kwargs(
        drive_id=drive_id,
        fields=fields,
        id=id,
        next_page=next_page,
        page_size=page_size,
        path=path,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    drive_id: Optional[str] = None,
    drive_id_lookup: Any,
    fields: Optional[str] = None,
    fields_lookup: Any,
    id: Optional[str] = None,
    id_lookup: Any,
    next_page: Optional[str] = None,
    next_page_lookup: Any,
    page_size: Optional[int] = None,
    page_size_lookup: Any,
    path: Optional[str] = None,
    path_lookup: Any,
) -> Optional[Union[DefaultError, list["GetCuratedFileAndFolders"]]]:
    """Get a list of CuratedFileAndFolders that are contained within a specified folder by path or ID.

    Args:
        drive_id (Optional[str]):
        fields (Optional[str]):
        id (Optional[str]):
        next_page (Optional[str]):
        page_size (Optional[int]):
        path (Optional[str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[DefaultError, list['GetCuratedFileAndFolders']]
    """

    return (
        await asyncio_detailed(
            client=client,
            drive_id=drive_id,
            drive_id_lookup=drive_id_lookup,
            fields=fields,
            fields_lookup=fields_lookup,
            id=id,
            id_lookup=id_lookup,
            next_page=next_page,
            next_page_lookup=next_page_lookup,
            page_size=page_size,
            page_size_lookup=page_size_lookup,
            path=path,
            path_lookup=path_lookup,
        )
    ).parsed
