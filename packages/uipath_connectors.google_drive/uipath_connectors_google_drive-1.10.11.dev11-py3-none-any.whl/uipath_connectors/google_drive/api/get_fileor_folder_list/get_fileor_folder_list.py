from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response
from ... import errors

from ...models.default_error import DefaultError
from ...models.get_fileor_folder_list import GetFileorFolderList


def _get_kwargs(
    *,
    page_size: Optional[int] = None,
    next_page: Optional[str] = None,
    starred_only: Optional[bool] = False,
    what_to_return: Optional[str] = "files",
    parent_id: str,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["pageSize"] = page_size

    params["nextPage"] = next_page

    params["starredOnly"] = starred_only

    params["whatToReturn"] = what_to_return

    params["parentID"] = parent_id

    params = {k: v for k, v in params.items() if v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/getFileorFolderList",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[DefaultError, list["GetFileorFolderList"]]]:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = GetFileorFolderList.from_dict(response_200_item_data)

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
) -> Response[Union[DefaultError, list["GetFileorFolderList"]]]:
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
    starred_only: Optional[bool] = False,
    what_to_return: Optional[str] = "files",
    parent_id: str,
    parent_id_lookup: Any,
) -> Response[Union[DefaultError, list["GetFileorFolderList"]]]:
    """Get File or Folder List

     Get File or Folder List

    Args:
        page_size (Optional[int]): The number of resources to return in a given page
        next_page (Optional[str]): The next page token
        starred_only (Optional[bool]): Starred only Default: False.
        what_to_return (Optional[str]): What to return Default: 'files'.
        parent_id (str): Folder Id

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[DefaultError, list['GetFileorFolderList']]]
    """

    if not parent_id and parent_id_lookup:
        lookup_response_raw = client.get_httpx_client().request(
            method="get", url="/EventFolderPicker"
        )
        lookup_response = lookup_response_raw.json()

        found_items = []
        for item in lookup_response:
            if parent_id_lookup in item["FullName"]:
                found_items.append(item)

        if not found_items:
            raise ValueError(
                "No matches found for parent_id_lookup in EventFolderPicker"
            )
        if len(found_items) > 1:
            print(
                "Warning: Multiple matches found for parent_id_lookup in EventFolderPicker. Using the first match."
            )

        parent_id = found_items[0]["ID"]

    kwargs = _get_kwargs(
        page_size=page_size,
        next_page=next_page,
        starred_only=starred_only,
        what_to_return=what_to_return,
        parent_id=parent_id,
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
    starred_only: Optional[bool] = False,
    what_to_return: Optional[str] = "files",
    parent_id: str,
    parent_id_lookup: Any,
) -> Optional[Union[DefaultError, list["GetFileorFolderList"]]]:
    """Get File or Folder List

     Get File or Folder List

    Args:
        page_size (Optional[int]): The number of resources to return in a given page
        next_page (Optional[str]): The next page token
        starred_only (Optional[bool]): Starred only Default: False.
        what_to_return (Optional[str]): What to return Default: 'files'.
        parent_id (str): Folder Id

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[DefaultError, list['GetFileorFolderList']]
    """

    return sync_detailed(
        client=client,
        page_size=page_size,
        next_page=next_page,
        starred_only=starred_only,
        what_to_return=what_to_return,
        parent_id=parent_id,
        parent_id_lookup=parent_id_lookup,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    page_size: Optional[int] = None,
    next_page: Optional[str] = None,
    starred_only: Optional[bool] = False,
    what_to_return: Optional[str] = "files",
    parent_id: str,
    parent_id_lookup: Any,
) -> Response[Union[DefaultError, list["GetFileorFolderList"]]]:
    """Get File or Folder List

     Get File or Folder List

    Args:
        page_size (Optional[int]): The number of resources to return in a given page
        next_page (Optional[str]): The next page token
        starred_only (Optional[bool]): Starred only Default: False.
        what_to_return (Optional[str]): What to return Default: 'files'.
        parent_id (str): Folder Id

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[DefaultError, list['GetFileorFolderList']]]
    """

    if not parent_id and parent_id_lookup:
        lookup_response_raw = await client.get_async_httpx_client().request(
            method="get", url="/EventFolderPicker"
        )
        lookup_response = lookup_response_raw.json()

        found_items = []
        for item in lookup_response:
            if parent_id_lookup in item["FullName"]:
                found_items.append(item)

        if not found_items:
            raise ValueError(
                "No matches found for parent_id_lookup in EventFolderPicker"
            )
        if len(found_items) > 1:
            print(
                "Warning: Multiple matches found for parent_id_lookup in EventFolderPicker. Using the first match."
            )

        parent_id = found_items[0]["ID"]

    kwargs = _get_kwargs(
        page_size=page_size,
        next_page=next_page,
        starred_only=starred_only,
        what_to_return=what_to_return,
        parent_id=parent_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    page_size: Optional[int] = None,
    next_page: Optional[str] = None,
    starred_only: Optional[bool] = False,
    what_to_return: Optional[str] = "files",
    parent_id: str,
    parent_id_lookup: Any,
) -> Optional[Union[DefaultError, list["GetFileorFolderList"]]]:
    """Get File or Folder List

     Get File or Folder List

    Args:
        page_size (Optional[int]): The number of resources to return in a given page
        next_page (Optional[str]): The next page token
        starred_only (Optional[bool]): Starred only Default: False.
        what_to_return (Optional[str]): What to return Default: 'files'.
        parent_id (str): Folder Id

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[DefaultError, list['GetFileorFolderList']]
    """

    return (
        await asyncio_detailed(
            client=client,
            page_size=page_size,
            next_page=next_page,
            starred_only=starred_only,
            what_to_return=what_to_return,
            parent_id=parent_id,
            parent_id_lookup=parent_id_lookup,
        )
    ).parsed
