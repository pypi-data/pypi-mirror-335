from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response
from ... import errors

from ...models.default_error import DefaultError
from ...models.web_summary_request import WebSummaryRequest
from ...models.web_summary_response import WebSummaryResponse


def _get_kwargs(
    *,
    body: WebSummaryRequest,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/v1/webSummary",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body
    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[DefaultError, WebSummaryResponse]]:
    if response.status_code == 200:
        response_200 = WebSummaryResponse.from_dict(response.json())

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
) -> Response[Union[DefaultError, WebSummaryResponse]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: WebSummaryRequest,
) -> Response[Union[DefaultError, WebSummaryResponse]]:
    """Web Summary

     Web summary provides an AI-generated summary of search results, synthesizing key insights from
    multiple sources and including citations. The summary and source citations are available in the
    output. Web summary offers near-real time search results, but certain time sensitive data like stock
    prices or weather will not consistently be current. There could be a few days lag. Be sure to pass
    in date/time and/or location as arguments in the query if required.

    Args:
        body (WebSummaryRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[DefaultError, WebSummaryResponse]]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: Union[AuthenticatedClient, Client],
    body: WebSummaryRequest,
) -> Optional[Union[DefaultError, WebSummaryResponse]]:
    """Web Summary

     Web summary provides an AI-generated summary of search results, synthesizing key insights from
    multiple sources and including citations. The summary and source citations are available in the
    output. Web summary offers near-real time search results, but certain time sensitive data like stock
    prices or weather will not consistently be current. There could be a few days lag. Be sure to pass
    in date/time and/or location as arguments in the query if required.

    Args:
        body (WebSummaryRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[DefaultError, WebSummaryResponse]
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: WebSummaryRequest,
) -> Response[Union[DefaultError, WebSummaryResponse]]:
    """Web Summary

     Web summary provides an AI-generated summary of search results, synthesizing key insights from
    multiple sources and including citations. The summary and source citations are available in the
    output. Web summary offers near-real time search results, but certain time sensitive data like stock
    prices or weather will not consistently be current. There could be a few days lag. Be sure to pass
    in date/time and/or location as arguments in the query if required.

    Args:
        body (WebSummaryRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[DefaultError, WebSummaryResponse]]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    body: WebSummaryRequest,
) -> Optional[Union[DefaultError, WebSummaryResponse]]:
    """Web Summary

     Web summary provides an AI-generated summary of search results, synthesizing key insights from
    multiple sources and including citations. The summary and source citations are available in the
    output. Web summary offers near-real time search results, but certain time sensitive data like stock
    prices or weather will not consistently be current. There could be a few days lag. Be sure to pass
    in date/time and/or location as arguments in the query if required.

    Args:
        body (WebSummaryRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[DefaultError, WebSummaryResponse]
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
