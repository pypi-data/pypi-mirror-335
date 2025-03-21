from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response
from ... import errors

from ...models.default_error import DefaultError
from ...models.get_volume_response import GetVolumeResponse


def _get_kwargs(
    volume_id: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/ebs/volume/{volume_id}".format(
            volume_id=volume_id,
        ),
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[DefaultError, GetVolumeResponse]]:
    if response.status_code == 200:
        response_200 = GetVolumeResponse.from_dict(response.json())

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
) -> Response[Union[DefaultError, GetVolumeResponse]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    volume_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[Union[DefaultError, GetVolumeResponse]]:
    """Get Volume

     Fetches a volume with given volume id.

    Args:
        volume_id (str): Identifier of a volume which needs to be fetch.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[DefaultError, GetVolumeResponse]]
    """

    kwargs = _get_kwargs(
        volume_id=volume_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    volume_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[Union[DefaultError, GetVolumeResponse]]:
    """Get Volume

     Fetches a volume with given volume id.

    Args:
        volume_id (str): Identifier of a volume which needs to be fetch.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[DefaultError, GetVolumeResponse]
    """

    return sync_detailed(
        volume_id=volume_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    volume_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[Union[DefaultError, GetVolumeResponse]]:
    """Get Volume

     Fetches a volume with given volume id.

    Args:
        volume_id (str): Identifier of a volume which needs to be fetch.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[DefaultError, GetVolumeResponse]]
    """

    kwargs = _get_kwargs(
        volume_id=volume_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    volume_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[Union[DefaultError, GetVolumeResponse]]:
    """Get Volume

     Fetches a volume with given volume id.

    Args:
        volume_id (str): Identifier of a volume which needs to be fetch.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[DefaultError, GetVolumeResponse]
    """

    return (
        await asyncio_detailed(
            volume_id=volume_id,
            client=client,
        )
    ).parsed
