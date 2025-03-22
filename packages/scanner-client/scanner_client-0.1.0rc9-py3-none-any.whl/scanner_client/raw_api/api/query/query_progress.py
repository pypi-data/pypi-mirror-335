from http import HTTPStatus
from typing import Any, Optional, Union
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.ad_hoc_query_progress_response import AdHocQueryProgressResponse
from ...types import Response


def _get_kwargs(
    qr_id: UUID,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/v1/query_progress/{qr_id}",
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[AdHocQueryProgressResponse]:
    if response.status_code == 200:
        response_200 = AdHocQueryProgressResponse.from_dict(response.json())

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[AdHocQueryProgressResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    qr_id: UUID,
    *,
    client: AuthenticatedClient,
) -> Response[AdHocQueryProgressResponse]:
    """Retrieve the state and current result set of a previously-started query.

    Args:
        qr_id (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[AdHocQueryProgressResponse]
    """

    kwargs = _get_kwargs(
        qr_id=qr_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    qr_id: UUID,
    *,
    client: AuthenticatedClient,
) -> Optional[AdHocQueryProgressResponse]:
    """Retrieve the state and current result set of a previously-started query.

    Args:
        qr_id (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        AdHocQueryProgressResponse
    """

    return sync_detailed(
        qr_id=qr_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    qr_id: UUID,
    *,
    client: AuthenticatedClient,
) -> Response[AdHocQueryProgressResponse]:
    """Retrieve the state and current result set of a previously-started query.

    Args:
        qr_id (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[AdHocQueryProgressResponse]
    """

    kwargs = _get_kwargs(
        qr_id=qr_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    qr_id: UUID,
    *,
    client: AuthenticatedClient,
) -> Optional[AdHocQueryProgressResponse]:
    """Retrieve the state and current result set of a previously-started query.

    Args:
        qr_id (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        AdHocQueryProgressResponse
    """

    return (
        await asyncio_detailed(
            qr_id=qr_id,
            client=client,
        )
    ).parsed
