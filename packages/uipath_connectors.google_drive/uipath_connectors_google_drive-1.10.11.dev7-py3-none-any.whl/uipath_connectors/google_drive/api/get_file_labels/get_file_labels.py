from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response
from ... import errors

from ...models.default_error import DefaultError
from ...models.get_file_labels import GetFileLabels


def _get_kwargs(
    *,
    file_id: str,
    fields: Optional[str] = None,
    next_page: Optional[str] = None,
    page_size: Optional[int] = None,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["fileId"] = file_id

    params["fields"] = fields

    params["nextPage"] = next_page

    params["pageSize"] = page_size

    params = {k: v for k, v in params.items() if v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/GetFileLabels",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[DefaultError, list["GetFileLabels"]]]:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for componentsschemas_get_file_labels_list_item_data in _response_200:
            componentsschemas_get_file_labels_list_item = GetFileLabels.from_dict(
                componentsschemas_get_file_labels_list_item_data
            )

            response_200.append(componentsschemas_get_file_labels_list_item)

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
) -> Response[Union[DefaultError, list["GetFileLabels"]]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    file_id: str,
    file_id_lookup: Any,
    fields: Optional[str] = None,
    fields_lookup: Any,
    next_page: Optional[str] = None,
    next_page_lookup: Any,
    page_size: Optional[int] = None,
    page_size_lookup: Any,
) -> Response[Union[DefaultError, list["GetFileLabels"]]]:
    """Get File Labels

     Get File Labels

    Args:
        file_id (str):
        fields (Optional[str]):
        next_page (Optional[str]):
        page_size (Optional[int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[DefaultError, list['GetFileLabels']]]
    """

    if not file_id and file_id_lookup:
        lookup_response_raw = client.get_httpx_client().request(
            method="get", url="/EventFolderPicker"
        )
        lookup_response = lookup_response_raw.json()

        found_items = []
        for item in lookup_response:
            if file_id_lookup in item["FullName"]:
                found_items.append(item)

        if not found_items:
            raise ValueError(
                "No matches found for file_id_lookup in EventFolderPicker"
            )
        if len(found_items) > 1:
            print(
                "Warning: Multiple matches found for file_id_lookup in EventFolderPicker. Using the first match."
            )

        file_id = found_items[0]["ID"]

    kwargs = _get_kwargs(
        file_id=file_id,
        fields=fields,
        next_page=next_page,
        page_size=page_size,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: Union[AuthenticatedClient, Client],
    file_id: str,
    file_id_lookup: Any,
    fields: Optional[str] = None,
    fields_lookup: Any,
    next_page: Optional[str] = None,
    next_page_lookup: Any,
    page_size: Optional[int] = None,
    page_size_lookup: Any,
) -> Optional[Union[DefaultError, list["GetFileLabels"]]]:
    """Get File Labels

     Get File Labels

    Args:
        file_id (str):
        fields (Optional[str]):
        next_page (Optional[str]):
        page_size (Optional[int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[DefaultError, list['GetFileLabels']]
    """

    return sync_detailed(
        client=client,
        file_id=file_id,
        file_id_lookup=file_id_lookup,
        fields=fields,
        fields_lookup=fields_lookup,
        next_page=next_page,
        next_page_lookup=next_page_lookup,
        page_size=page_size,
        page_size_lookup=page_size_lookup,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    file_id: str,
    file_id_lookup: Any,
    fields: Optional[str] = None,
    fields_lookup: Any,
    next_page: Optional[str] = None,
    next_page_lookup: Any,
    page_size: Optional[int] = None,
    page_size_lookup: Any,
) -> Response[Union[DefaultError, list["GetFileLabels"]]]:
    """Get File Labels

     Get File Labels

    Args:
        file_id (str):
        fields (Optional[str]):
        next_page (Optional[str]):
        page_size (Optional[int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[DefaultError, list['GetFileLabels']]]
    """

    if not file_id and file_id_lookup:
        lookup_response_raw = await client.get_async_httpx_client().request(
            method="get", url="/EventFolderPicker"
        )
        lookup_response = lookup_response_raw.json()

        found_items = []
        for item in lookup_response:
            if file_id_lookup in item["FullName"]:
                found_items.append(item)

        if not found_items:
            raise ValueError(
                "No matches found for file_id_lookup in EventFolderPicker"
            )
        if len(found_items) > 1:
            print(
                "Warning: Multiple matches found for file_id_lookup in EventFolderPicker. Using the first match."
            )

        file_id = found_items[0]["ID"]

    kwargs = _get_kwargs(
        file_id=file_id,
        fields=fields,
        next_page=next_page,
        page_size=page_size,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    file_id: str,
    file_id_lookup: Any,
    fields: Optional[str] = None,
    fields_lookup: Any,
    next_page: Optional[str] = None,
    next_page_lookup: Any,
    page_size: Optional[int] = None,
    page_size_lookup: Any,
) -> Optional[Union[DefaultError, list["GetFileLabels"]]]:
    """Get File Labels

     Get File Labels

    Args:
        file_id (str):
        fields (Optional[str]):
        next_page (Optional[str]):
        page_size (Optional[int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[DefaultError, list['GetFileLabels']]
    """

    return (
        await asyncio_detailed(
            client=client,
            file_id=file_id,
            file_id_lookup=file_id_lookup,
            fields=fields,
            fields_lookup=fields_lookup,
            next_page=next_page,
            next_page_lookup=next_page_lookup,
            page_size=page_size,
            page_size_lookup=page_size_lookup,
        )
    ).parsed
