from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response
from ... import errors

from ...models.default_error import DefaultError
from ...models.delete_column_request import DeleteColumnRequest


def _get_kwargs(
    *,
    body: DeleteColumnRequest,
    reference_id: str,
    has_headers: bool = False,
    range_: str,
    column_position: str,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    params: dict[str, Any] = {}

    params["referenceID"] = reference_id

    params["hasHeaders"] = has_headers

    params["range"] = range_

    params["columnPosition"] = column_position

    params = {k: v for k, v in params.items() if v is not None}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/DeleteColumn",
        "params": params,
    }

    _body = body.to_dict()

    _kwargs["json"] = _body
    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Any, DefaultError]]:
    if response.status_code == 200:
        response_200 = cast(Any, None)
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
) -> Response[Union[Any, DefaultError]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: DeleteColumnRequest,
    reference_id: str,
    reference_id_lookup: Any,
    has_headers: bool = False,
    range_: str,
    column_position: str,
) -> Response[Union[Any, DefaultError]]:
    """Delete Column

     Deletes a column from a worksheet in workbook.

    Args:
        reference_id (str): Workbook
        has_headers (bool): Has headers Default: False.
        range_ (str): Indicates the range where to delete the column. For example: Sheet1!A1:A14.
        column_position (str): Specify column position to delete
        body (DeleteColumnRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, DefaultError]]
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
        body=body,
        reference_id=reference_id,
        has_headers=has_headers,
        range_=range_,
        column_position=column_position,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: Union[AuthenticatedClient, Client],
    body: DeleteColumnRequest,
    reference_id: str,
    reference_id_lookup: Any,
    has_headers: bool = False,
    range_: str,
    column_position: str,
) -> Optional[Union[Any, DefaultError]]:
    """Delete Column

     Deletes a column from a worksheet in workbook.

    Args:
        reference_id (str): Workbook
        has_headers (bool): Has headers Default: False.
        range_ (str): Indicates the range where to delete the column. For example: Sheet1!A1:A14.
        column_position (str): Specify column position to delete
        body (DeleteColumnRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, DefaultError]
    """

    return sync_detailed(
        client=client,
        body=body,
        reference_id=reference_id,
        reference_id_lookup=reference_id_lookup,
        has_headers=has_headers,
        range_=range_,
        column_position=column_position,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: DeleteColumnRequest,
    reference_id: str,
    reference_id_lookup: Any,
    has_headers: bool = False,
    range_: str,
    column_position: str,
) -> Response[Union[Any, DefaultError]]:
    """Delete Column

     Deletes a column from a worksheet in workbook.

    Args:
        reference_id (str): Workbook
        has_headers (bool): Has headers Default: False.
        range_ (str): Indicates the range where to delete the column. For example: Sheet1!A1:A14.
        column_position (str): Specify column position to delete
        body (DeleteColumnRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, DefaultError]]
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
        body=body,
        reference_id=reference_id,
        has_headers=has_headers,
        range_=range_,
        column_position=column_position,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    body: DeleteColumnRequest,
    reference_id: str,
    reference_id_lookup: Any,
    has_headers: bool = False,
    range_: str,
    column_position: str,
) -> Optional[Union[Any, DefaultError]]:
    """Delete Column

     Deletes a column from a worksheet in workbook.

    Args:
        reference_id (str): Workbook
        has_headers (bool): Has headers Default: False.
        range_ (str): Indicates the range where to delete the column. For example: Sheet1!A1:A14.
        column_position (str): Specify column position to delete
        body (DeleteColumnRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, DefaultError]
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
            reference_id=reference_id,
            reference_id_lookup=reference_id_lookup,
            has_headers=has_headers,
            range_=range_,
            column_position=column_position,
        )
    ).parsed
