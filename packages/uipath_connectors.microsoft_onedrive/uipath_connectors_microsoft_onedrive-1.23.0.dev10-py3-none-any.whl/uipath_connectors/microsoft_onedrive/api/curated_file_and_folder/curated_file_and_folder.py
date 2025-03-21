from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response
from ... import errors

from ...models.curated_file_and_folder import CuratedFileAndFolder
from ...models.default_error import DefaultError


def _get_kwargs(
    *,
    page_size: Optional[int] = None,
    next_page: Optional[str] = None,
    drive_id: Optional[str] = None,
    path: Optional[str] = None,
    id: Optional[str] = None,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["pageSize"] = page_size

    params["nextPage"] = next_page

    params["driveID"] = drive_id

    params["path"] = path

    params["id"] = id

    params = {k: v for k, v in params.items() if v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/CuratedFileAndFolders",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[DefaultError, list["CuratedFileAndFolder"]]]:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = CuratedFileAndFolder.from_dict(response_200_item_data)

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
) -> Response[Union[DefaultError, list["CuratedFileAndFolder"]]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    page_size: Optional[int] = None,
    next_page: Optional[str] = None,
    drive_id: Optional[str] = None,
    path: Optional[str] = None,
    id: Optional[str] = None,
) -> Response[Union[DefaultError, list["CuratedFileAndFolder"]]]:
    """Curated file and folders

     Get a list of CuratedFileAndFolders that are contained within a specified folder by path or ID.

    Args:
        page_size (Optional[int]): The number of resources to return in a given page
        next_page (Optional[str]): The next page token, taken from the response headers 'elements-
            next-page-token'
        drive_id (Optional[str]): The drive ID. Provide when we want to fetch file/folder from a
            specific drive.
        path (Optional[str]): The full path of the parent folder (e.g. /Documents)
        id (Optional[str]): The item ID of the parent folder (e.g. 123!abc)

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[DefaultError, list['CuratedFileAndFolder']]]
    """

    kwargs = _get_kwargs(
        page_size=page_size,
        next_page=next_page,
        drive_id=drive_id,
        path=path,
        id=id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: Union[AuthenticatedClient, Client],
    page_size: Optional[int] = None,
    next_page: Optional[str] = None,
    drive_id: Optional[str] = None,
    path: Optional[str] = None,
    id: Optional[str] = None,
) -> Optional[Union[DefaultError, list["CuratedFileAndFolder"]]]:
    """Curated file and folders

     Get a list of CuratedFileAndFolders that are contained within a specified folder by path or ID.

    Args:
        page_size (Optional[int]): The number of resources to return in a given page
        next_page (Optional[str]): The next page token, taken from the response headers 'elements-
            next-page-token'
        drive_id (Optional[str]): The drive ID. Provide when we want to fetch file/folder from a
            specific drive.
        path (Optional[str]): The full path of the parent folder (e.g. /Documents)
        id (Optional[str]): The item ID of the parent folder (e.g. 123!abc)

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[DefaultError, list['CuratedFileAndFolder']]
    """

    return sync_detailed(
        client=client,
        page_size=page_size,
        next_page=next_page,
        drive_id=drive_id,
        path=path,
        id=id,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    page_size: Optional[int] = None,
    next_page: Optional[str] = None,
    drive_id: Optional[str] = None,
    path: Optional[str] = None,
    id: Optional[str] = None,
) -> Response[Union[DefaultError, list["CuratedFileAndFolder"]]]:
    """Curated file and folders

     Get a list of CuratedFileAndFolders that are contained within a specified folder by path or ID.

    Args:
        page_size (Optional[int]): The number of resources to return in a given page
        next_page (Optional[str]): The next page token, taken from the response headers 'elements-
            next-page-token'
        drive_id (Optional[str]): The drive ID. Provide when we want to fetch file/folder from a
            specific drive.
        path (Optional[str]): The full path of the parent folder (e.g. /Documents)
        id (Optional[str]): The item ID of the parent folder (e.g. 123!abc)

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[DefaultError, list['CuratedFileAndFolder']]]
    """

    kwargs = _get_kwargs(
        page_size=page_size,
        next_page=next_page,
        drive_id=drive_id,
        path=path,
        id=id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    page_size: Optional[int] = None,
    next_page: Optional[str] = None,
    drive_id: Optional[str] = None,
    path: Optional[str] = None,
    id: Optional[str] = None,
) -> Optional[Union[DefaultError, list["CuratedFileAndFolder"]]]:
    """Curated file and folders

     Get a list of CuratedFileAndFolders that are contained within a specified folder by path or ID.

    Args:
        page_size (Optional[int]): The number of resources to return in a given page
        next_page (Optional[str]): The next page token, taken from the response headers 'elements-
            next-page-token'
        drive_id (Optional[str]): The drive ID. Provide when we want to fetch file/folder from a
            specific drive.
        path (Optional[str]): The full path of the parent folder (e.g. /Documents)
        id (Optional[str]): The item ID of the parent folder (e.g. 123!abc)

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[DefaultError, list['CuratedFileAndFolder']]
    """

    return (
        await asyncio_detailed(
            client=client,
            page_size=page_size,
            next_page=next_page,
            drive_id=drive_id,
            path=path,
            id=id,
        )
    ).parsed
