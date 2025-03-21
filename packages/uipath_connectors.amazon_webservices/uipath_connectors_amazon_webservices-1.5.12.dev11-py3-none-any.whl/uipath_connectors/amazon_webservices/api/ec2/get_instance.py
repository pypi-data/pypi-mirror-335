from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response
from ... import errors

from ...models.default_error import DefaultError
from ...models.get_instance_response import GetInstanceResponse


def _get_kwargs(
    instance_id: str,
    *,
    service_name: Optional[str] = "ec2",
    action: Optional[str] = None,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["serviceName"] = service_name

    params["Action"] = action

    params = {k: v for k, v in params.items() if v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/ec2/{instance_id}".format(
            instance_id=instance_id,
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[DefaultError, GetInstanceResponse]]:
    if response.status_code == 200:
        response_200 = GetInstanceResponse.from_dict(response.json())

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
) -> Response[Union[DefaultError, GetInstanceResponse]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    instance_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    service_name: Optional[str] = "ec2",
    action: Optional[str] = None,
) -> Response[Union[DefaultError, GetInstanceResponse]]:
    """GetInstance

    Args:
        instance_id (str): InstanceId
        service_name (Optional[str]): Service name Default: 'ec2'.
        action (Optional[str]): The action

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[DefaultError, GetInstanceResponse]]
    """

    kwargs = _get_kwargs(
        instance_id=instance_id,
        service_name=service_name,
        action=action,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    instance_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    service_name: Optional[str] = "ec2",
    action: Optional[str] = None,
) -> Optional[Union[DefaultError, GetInstanceResponse]]:
    """GetInstance

    Args:
        instance_id (str): InstanceId
        service_name (Optional[str]): Service name Default: 'ec2'.
        action (Optional[str]): The action

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[DefaultError, GetInstanceResponse]
    """

    return sync_detailed(
        instance_id=instance_id,
        client=client,
        service_name=service_name,
        action=action,
    ).parsed


async def asyncio_detailed(
    instance_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    service_name: Optional[str] = "ec2",
    action: Optional[str] = None,
) -> Response[Union[DefaultError, GetInstanceResponse]]:
    """GetInstance

    Args:
        instance_id (str): InstanceId
        service_name (Optional[str]): Service name Default: 'ec2'.
        action (Optional[str]): The action

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[DefaultError, GetInstanceResponse]]
    """

    kwargs = _get_kwargs(
        instance_id=instance_id,
        service_name=service_name,
        action=action,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    instance_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    service_name: Optional[str] = "ec2",
    action: Optional[str] = None,
) -> Optional[Union[DefaultError, GetInstanceResponse]]:
    """GetInstance

    Args:
        instance_id (str): InstanceId
        service_name (Optional[str]): Service name Default: 'ec2'.
        action (Optional[str]): The action

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[DefaultError, GetInstanceResponse]
    """

    return (
        await asyncio_detailed(
            instance_id=instance_id,
            client=client,
            service_name=service_name,
            action=action,
        )
    ).parsed
