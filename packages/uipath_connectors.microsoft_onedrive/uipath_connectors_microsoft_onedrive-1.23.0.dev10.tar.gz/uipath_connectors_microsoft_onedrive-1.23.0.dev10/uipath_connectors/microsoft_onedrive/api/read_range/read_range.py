from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response
from ... import errors

from ...models.default_error import DefaultError
from ...models.read_range import ReadRange


def _get_kwargs(
    *,
    reference_id: str,
    range_: str,
    read: Optional[str] = None,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["referenceID"] = reference_id

    params["range"] = range_

    params["read"] = read

    params = {k: v for k, v in params.items() if v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/readRange",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[DefaultError, list["ReadRange"]]]:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = ReadRange.from_dict(response_200_item_data)

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
) -> Response[Union[DefaultError, list["ReadRange"]]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    reference_id: str,
    reference_id_lookup: Any,
    range_: str,
    read: Optional[str] = None,
) -> Response[Union[DefaultError, list["ReadRange"]]]:
    """Read Range

     Reads data from a range of cells in a worksheet.

    Args:
        reference_id (str): Workbook
        range_ (str): Select the Range to read. A full A1 Range notation can be used eg
            'Sheet1!A1:C10'.
        read (Optional[str]): What to read

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[DefaultError, list['ReadRange']]]
    """

    if not reference_id and reference_id_lookup:
        lookup_response_raw = client.get_httpx_client().request(
            method="get",
            url="/EventFolderPicker?includeFiles=true&onlyExcelFiles=true",
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

        reference_id = found_items[0]["ReferenceID"]

    kwargs = _get_kwargs(
        reference_id=reference_id,
        range_=range_,
        read=read,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: Union[AuthenticatedClient, Client],
    reference_id: str,
    reference_id_lookup: Any,
    range_: str,
    read: Optional[str] = None,
) -> Optional[Union[DefaultError, list["ReadRange"]]]:
    """Read Range

     Reads data from a range of cells in a worksheet.

    Args:
        reference_id (str): Workbook
        range_ (str): Select the Range to read. A full A1 Range notation can be used eg
            'Sheet1!A1:C10'.
        read (Optional[str]): What to read

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[DefaultError, list['ReadRange']]
    """

    return sync_detailed(
        client=client,
        reference_id=reference_id,
        reference_id_lookup=reference_id_lookup,
        range_=range_,
        read=read,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    reference_id: str,
    reference_id_lookup: Any,
    range_: str,
    read: Optional[str] = None,
) -> Response[Union[DefaultError, list["ReadRange"]]]:
    """Read Range

     Reads data from a range of cells in a worksheet.

    Args:
        reference_id (str): Workbook
        range_ (str): Select the Range to read. A full A1 Range notation can be used eg
            'Sheet1!A1:C10'.
        read (Optional[str]): What to read

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[DefaultError, list['ReadRange']]]
    """

    if not reference_id and reference_id_lookup:
        lookup_response_raw = await client.get_async_httpx_client().request(
            method="get",
            url="/EventFolderPicker?includeFiles=true&onlyExcelFiles=true",
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

        reference_id = found_items[0]["ReferenceID"]

    kwargs = _get_kwargs(
        reference_id=reference_id,
        range_=range_,
        read=read,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    reference_id: str,
    reference_id_lookup: Any,
    range_: str,
    read: Optional[str] = None,
) -> Optional[Union[DefaultError, list["ReadRange"]]]:
    """Read Range

     Reads data from a range of cells in a worksheet.

    Args:
        reference_id (str): Workbook
        range_ (str): Select the Range to read. A full A1 Range notation can be used eg
            'Sheet1!A1:C10'.
        read (Optional[str]): What to read

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[DefaultError, list['ReadRange']]
    """

    return (
        await asyncio_detailed(
            client=client,
            reference_id=reference_id,
            reference_id_lookup=reference_id_lookup,
            range_=range_,
            read=read,
        )
    ).parsed
