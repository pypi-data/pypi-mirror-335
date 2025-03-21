from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response
from ... import errors

from ...models.default_error import DefaultError
from ...models.generate_email_request import GenerateEmailRequest
from ...models.generate_email_response import GenerateEmailResponse


def _get_kwargs(
    *,
    body: GenerateEmailRequest,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/generateEmail",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body
    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[DefaultError, GenerateEmailResponse]]:
    if response.status_code == 200:
        response_200 = GenerateEmailResponse.from_dict(response.json())

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
) -> Response[Union[DefaultError, GenerateEmailResponse]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: GenerateEmailRequest,
) -> Response[Union[DefaultError, GenerateEmailResponse]]:
    """Generate Email

     This activity will be to enable users to have a draft of an email composed meeting a specific style
    elected by the user.  This activity could be used in a wide variety of use cases including: building
    a marketing campaign, sending out company wide notifications, community outreach/product launches,
    etc.

    Args:
        body (GenerateEmailRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[DefaultError, GenerateEmailResponse]]
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
    body: GenerateEmailRequest,
) -> Optional[Union[DefaultError, GenerateEmailResponse]]:
    """Generate Email

     This activity will be to enable users to have a draft of an email composed meeting a specific style
    elected by the user.  This activity could be used in a wide variety of use cases including: building
    a marketing campaign, sending out company wide notifications, community outreach/product launches,
    etc.

    Args:
        body (GenerateEmailRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[DefaultError, GenerateEmailResponse]
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: GenerateEmailRequest,
) -> Response[Union[DefaultError, GenerateEmailResponse]]:
    """Generate Email

     This activity will be to enable users to have a draft of an email composed meeting a specific style
    elected by the user.  This activity could be used in a wide variety of use cases including: building
    a marketing campaign, sending out company wide notifications, community outreach/product launches,
    etc.

    Args:
        body (GenerateEmailRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[DefaultError, GenerateEmailResponse]]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    body: GenerateEmailRequest,
) -> Optional[Union[DefaultError, GenerateEmailResponse]]:
    """Generate Email

     This activity will be to enable users to have a draft of an email composed meeting a specific style
    elected by the user.  This activity could be used in a wide variety of use cases including: building
    a marketing campaign, sending out company wide notifications, community outreach/product launches,
    etc.

    Args:
        body (GenerateEmailRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[DefaultError, GenerateEmailResponse]
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
