from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response
from ... import errors

from ...models.create_volume import CreateVolume
from ...models.default_error import DefaultError


def _get_kwargs(
    *,
    availability_zone: str,
    volume_type: str,
    encrypted: Optional[bool] = False,
    throughput: Optional[int] = None,
    iops: Optional[int] = None,
    size_in_gi_bs: int,
    snapshot_id: Optional[str] = None,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["AvailabilityZone"] = availability_zone

    params["VolumeType"] = volume_type

    params["Encrypted"] = encrypted

    params["Throughput"] = throughput

    params["Iops"] = iops

    params["SizeInGiBs"] = size_in_gi_bs

    params["SnapshotId"] = snapshot_id

    params = {k: v for k, v in params.items() if v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/ebs/create_volume",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[DefaultError, list["CreateVolume"]]]:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = CreateVolume.from_dict(response_200_item_data)

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
) -> Response[Union[DefaultError, list["CreateVolume"]]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    availability_zone: str,
    volume_type: str,
    encrypted: Optional[bool] = False,
    throughput: Optional[int] = None,
    iops: Optional[int] = None,
    size_in_gi_bs: int,
    snapshot_id: Optional[str] = None,
) -> Response[Union[DefaultError, list["CreateVolume"]]]:
    """Create Volume

     Creates a storage volume inside Elastic Block Storage in AWS.

    Args:
        availability_zone (str): The Availability Zone in which to create the volume. After you
            create the volume, you can only attach it to instances that are in the same Availability
            Zone.
        volume_type (str): Type of a storage volume.
        encrypted (Optional[bool]): Amazon EBS encryption is an encryption solution for your EBS
            volumes. Amazon EBS encryption uses AWS KMS key to encrypt volumes. Default: False.
        throughput (Optional[int]): The throughput performance that the volume can support. This
            is a performance measure in MiB/s.
        iops (Optional[int]): The requested number of I/O operations per second that the volume
            can support.
        size_in_gi_bs (int): Storage Volume Size in GiBs
        snapshot_id (Optional[str]): The snapshot from which to create the volume.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[DefaultError, list['CreateVolume']]]
    """

    kwargs = _get_kwargs(
        availability_zone=availability_zone,
        volume_type=volume_type,
        encrypted=encrypted,
        throughput=throughput,
        iops=iops,
        size_in_gi_bs=size_in_gi_bs,
        snapshot_id=snapshot_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: Union[AuthenticatedClient, Client],
    availability_zone: str,
    volume_type: str,
    encrypted: Optional[bool] = False,
    throughput: Optional[int] = None,
    iops: Optional[int] = None,
    size_in_gi_bs: int,
    snapshot_id: Optional[str] = None,
) -> Optional[Union[DefaultError, list["CreateVolume"]]]:
    """Create Volume

     Creates a storage volume inside Elastic Block Storage in AWS.

    Args:
        availability_zone (str): The Availability Zone in which to create the volume. After you
            create the volume, you can only attach it to instances that are in the same Availability
            Zone.
        volume_type (str): Type of a storage volume.
        encrypted (Optional[bool]): Amazon EBS encryption is an encryption solution for your EBS
            volumes. Amazon EBS encryption uses AWS KMS key to encrypt volumes. Default: False.
        throughput (Optional[int]): The throughput performance that the volume can support. This
            is a performance measure in MiB/s.
        iops (Optional[int]): The requested number of I/O operations per second that the volume
            can support.
        size_in_gi_bs (int): Storage Volume Size in GiBs
        snapshot_id (Optional[str]): The snapshot from which to create the volume.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[DefaultError, list['CreateVolume']]
    """

    return sync_detailed(
        client=client,
        availability_zone=availability_zone,
        volume_type=volume_type,
        encrypted=encrypted,
        throughput=throughput,
        iops=iops,
        size_in_gi_bs=size_in_gi_bs,
        snapshot_id=snapshot_id,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    availability_zone: str,
    volume_type: str,
    encrypted: Optional[bool] = False,
    throughput: Optional[int] = None,
    iops: Optional[int] = None,
    size_in_gi_bs: int,
    snapshot_id: Optional[str] = None,
) -> Response[Union[DefaultError, list["CreateVolume"]]]:
    """Create Volume

     Creates a storage volume inside Elastic Block Storage in AWS.

    Args:
        availability_zone (str): The Availability Zone in which to create the volume. After you
            create the volume, you can only attach it to instances that are in the same Availability
            Zone.
        volume_type (str): Type of a storage volume.
        encrypted (Optional[bool]): Amazon EBS encryption is an encryption solution for your EBS
            volumes. Amazon EBS encryption uses AWS KMS key to encrypt volumes. Default: False.
        throughput (Optional[int]): The throughput performance that the volume can support. This
            is a performance measure in MiB/s.
        iops (Optional[int]): The requested number of I/O operations per second that the volume
            can support.
        size_in_gi_bs (int): Storage Volume Size in GiBs
        snapshot_id (Optional[str]): The snapshot from which to create the volume.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[DefaultError, list['CreateVolume']]]
    """

    kwargs = _get_kwargs(
        availability_zone=availability_zone,
        volume_type=volume_type,
        encrypted=encrypted,
        throughput=throughput,
        iops=iops,
        size_in_gi_bs=size_in_gi_bs,
        snapshot_id=snapshot_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    availability_zone: str,
    volume_type: str,
    encrypted: Optional[bool] = False,
    throughput: Optional[int] = None,
    iops: Optional[int] = None,
    size_in_gi_bs: int,
    snapshot_id: Optional[str] = None,
) -> Optional[Union[DefaultError, list["CreateVolume"]]]:
    """Create Volume

     Creates a storage volume inside Elastic Block Storage in AWS.

    Args:
        availability_zone (str): The Availability Zone in which to create the volume. After you
            create the volume, you can only attach it to instances that are in the same Availability
            Zone.
        volume_type (str): Type of a storage volume.
        encrypted (Optional[bool]): Amazon EBS encryption is an encryption solution for your EBS
            volumes. Amazon EBS encryption uses AWS KMS key to encrypt volumes. Default: False.
        throughput (Optional[int]): The throughput performance that the volume can support. This
            is a performance measure in MiB/s.
        iops (Optional[int]): The requested number of I/O operations per second that the volume
            can support.
        size_in_gi_bs (int): Storage Volume Size in GiBs
        snapshot_id (Optional[str]): The snapshot from which to create the volume.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[DefaultError, list['CreateVolume']]
    """

    return (
        await asyncio_detailed(
            client=client,
            availability_zone=availability_zone,
            volume_type=volume_type,
            encrypted=encrypted,
            throughput=throughput,
            iops=iops,
            size_in_gi_bs=size_in_gi_bs,
            snapshot_id=snapshot_id,
        )
    ).parsed
