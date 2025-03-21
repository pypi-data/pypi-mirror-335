from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response
from ... import errors

from ...models.context_grounding_search_request import ContextGroundingSearchRequest
from ...models.context_grounding_search_response import ContextGroundingSearchResponse
from ...models.default_error import DefaultError


def _get_kwargs(
    *,
    body: ContextGroundingSearchRequest,
    folder_key: str,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    params: dict[str, Any] = {}

    params["folderKey"] = folder_key

    params = {k: v for k, v in params.items() if v is not None}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/ecs/search",
        "params": params,
    }

    _body = body.to_dict()

    _kwargs["json"] = _body
    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[ContextGroundingSearchResponse, DefaultError]]:
    if response.status_code == 200:
        response_200 = ContextGroundingSearchResponse.from_dict(response.json())

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
) -> Response[Union[ContextGroundingSearchResponse, DefaultError]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: ContextGroundingSearchRequest,
    folder_key: str,
    folder_key_lookup: Any,
) -> Response[Union[ContextGroundingSearchResponse, DefaultError]]:
    """Context Grounding Search

     Given a natural language input or query, retrieve similar context from Context Grounding indices or
    from files.  Note that you can also set this directly in the 'Content Generation' activity.  Use
    this activity if you need to extract similar context from a file or index based on some other text
    input instead of the prompt itself.

    Args:
        folder_key (str): Orchestrator folder containing the index to search with
        body (ContextGroundingSearchRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ContextGroundingSearchResponse, DefaultError]]
    """

    if not folder_key and folder_key_lookup:
        lookup_response_raw = client.get_httpx_client().request(
            method="get", url="/folders"
        )
        lookup_response = lookup_response_raw.json()

        found_items = []
        for item in lookup_response:
            if folder_key_lookup in item["FullyQualifiedName"]:
                found_items.append(item)

        if not found_items:
            raise ValueError("No matches found for folder_key_lookup in folders")
        if len(found_items) > 1:
            print(
                "Warning: Multiple matches found for folder_key_lookup in folders. Using the first match."
            )

        folder_key = found_items[0]["Key"]

    kwargs = _get_kwargs(
        body=body,
        folder_key=folder_key,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: Union[AuthenticatedClient, Client],
    body: ContextGroundingSearchRequest,
    folder_key: str,
    folder_key_lookup: Any,
) -> Optional[Union[ContextGroundingSearchResponse, DefaultError]]:
    """Context Grounding Search

     Given a natural language input or query, retrieve similar context from Context Grounding indices or
    from files.  Note that you can also set this directly in the 'Content Generation' activity.  Use
    this activity if you need to extract similar context from a file or index based on some other text
    input instead of the prompt itself.

    Args:
        folder_key (str): Orchestrator folder containing the index to search with
        body (ContextGroundingSearchRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ContextGroundingSearchResponse, DefaultError]
    """

    return sync_detailed(
        client=client,
        body=body,
        folder_key=folder_key,
        folder_key_lookup=folder_key_lookup,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: ContextGroundingSearchRequest,
    folder_key: str,
    folder_key_lookup: Any,
) -> Response[Union[ContextGroundingSearchResponse, DefaultError]]:
    """Context Grounding Search

     Given a natural language input or query, retrieve similar context from Context Grounding indices or
    from files.  Note that you can also set this directly in the 'Content Generation' activity.  Use
    this activity if you need to extract similar context from a file or index based on some other text
    input instead of the prompt itself.

    Args:
        folder_key (str): Orchestrator folder containing the index to search with
        body (ContextGroundingSearchRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ContextGroundingSearchResponse, DefaultError]]
    """

    if not folder_key and folder_key_lookup:
        lookup_response_raw = await client.get_async_httpx_client().request(
            method="get", url="/folders"
        )
        lookup_response = lookup_response_raw.json()

        found_items = []
        for item in lookup_response:
            if folder_key_lookup in item["FullyQualifiedName"]:
                found_items.append(item)

        if not found_items:
            raise ValueError("No matches found for folder_key_lookup in folders")
        if len(found_items) > 1:
            print(
                "Warning: Multiple matches found for folder_key_lookup in folders. Using the first match."
            )

        folder_key = found_items[0]["Key"]

    kwargs = _get_kwargs(
        body=body,
        folder_key=folder_key,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    body: ContextGroundingSearchRequest,
    folder_key: str,
    folder_key_lookup: Any,
) -> Optional[Union[ContextGroundingSearchResponse, DefaultError]]:
    """Context Grounding Search

     Given a natural language input or query, retrieve similar context from Context Grounding indices or
    from files.  Note that you can also set this directly in the 'Content Generation' activity.  Use
    this activity if you need to extract similar context from a file or index based on some other text
    input instead of the prompt itself.

    Args:
        folder_key (str): Orchestrator folder containing the index to search with
        body (ContextGroundingSearchRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ContextGroundingSearchResponse, DefaultError]
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
            folder_key=folder_key,
            folder_key_lookup=folder_key_lookup,
        )
    ).parsed
