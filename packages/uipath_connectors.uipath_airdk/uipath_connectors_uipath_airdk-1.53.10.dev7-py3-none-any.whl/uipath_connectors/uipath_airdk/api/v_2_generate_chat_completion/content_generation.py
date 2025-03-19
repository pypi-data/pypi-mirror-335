from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response
from ... import errors

from ...models.content_generation_request import ContentGenerationRequest
from ...models.content_generation_response import ContentGenerationResponse
from ...models.default_error import DefaultError


def _get_kwargs(
    *,
    body: ContentGenerationRequest,
    model_name: str,
    folder_key: Optional[str] = None,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    params: dict[str, Any] = {}

    params["modelName"] = model_name

    params["folderKey"] = folder_key

    params = {k: v for k, v in params.items() if v is not None}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/v2/generateChatCompletion",
        "params": params,
    }

    _body = body.to_dict()

    _kwargs["json"] = _body
    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[ContentGenerationResponse, DefaultError]]:
    if response.status_code == 200:
        response_200 = ContentGenerationResponse.from_dict(response.json())

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
) -> Response[Union[ContentGenerationResponse, DefaultError]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: ContentGenerationRequest,
    model_name: str,
    model_name_lookup: Any,
    folder_key: Optional[str] = None,
    folder_key_lookup: Any,
) -> Response[Union[ContentGenerationResponse, DefaultError]]:
    """Content Generation

     Generate a chat response for the provided request using chat completion models

    Args:
        model_name (str):
        folder_key (Optional[str]):
        body (ContentGenerationRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ContentGenerationResponse, DefaultError]]
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
        model_name=model_name,
        folder_key=folder_key,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: Union[AuthenticatedClient, Client],
    body: ContentGenerationRequest,
    model_name: str,
    model_name_lookup: Any,
    folder_key: Optional[str] = None,
    folder_key_lookup: Any,
) -> Optional[Union[ContentGenerationResponse, DefaultError]]:
    """Content Generation

     Generate a chat response for the provided request using chat completion models

    Args:
        model_name (str):
        folder_key (Optional[str]):
        body (ContentGenerationRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ContentGenerationResponse, DefaultError]
    """

    return sync_detailed(
        client=client,
        body=body,
        model_name=model_name,
        model_name_lookup=model_name_lookup,
        folder_key=folder_key,
        folder_key_lookup=folder_key_lookup,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: ContentGenerationRequest,
    model_name: str,
    model_name_lookup: Any,
    folder_key: Optional[str] = None,
    folder_key_lookup: Any,
) -> Response[Union[ContentGenerationResponse, DefaultError]]:
    """Content Generation

     Generate a chat response for the provided request using chat completion models

    Args:
        model_name (str):
        folder_key (Optional[str]):
        body (ContentGenerationRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ContentGenerationResponse, DefaultError]]
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
        model_name=model_name,
        folder_key=folder_key,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    body: ContentGenerationRequest,
    model_name: str,
    model_name_lookup: Any,
    folder_key: Optional[str] = None,
    folder_key_lookup: Any,
) -> Optional[Union[ContentGenerationResponse, DefaultError]]:
    """Content Generation

     Generate a chat response for the provided request using chat completion models

    Args:
        model_name (str):
        folder_key (Optional[str]):
        body (ContentGenerationRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ContentGenerationResponse, DefaultError]
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
            model_name=model_name,
            model_name_lookup=model_name_lookup,
            folder_key=folder_key,
            folder_key_lookup=folder_key_lookup,
        )
    ).parsed
