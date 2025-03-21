from .ebsattach_volume_to_instance import (
    attach_volume_to_instance as _attach_volume_to_instance,
    attach_volume_to_instance_async as _attach_volume_to_instance_async,
)
from ..models.attach_volume_to_instance import AttachVolumeToInstance
from ..models.default_error import DefaultError
from typing import cast
from .instancelaunch_using_launch_template import (
    create_instance_from_launch_template as _create_instance_from_launch_template,
    create_instance_from_launch_template_async as _create_instance_from_launch_template_async,
)
from ..models.create_instance_from_launch_template import (
    CreateInstanceFromLaunchTemplate,
)
from .ebscreate_volume import (
    create_volume as _create_volume,
    create_volume_async as _create_volume_async,
)
from ..models.create_volume import CreateVolume
from .ebscreate_volume_snapshot import (
    create_volume_snapshot as _create_volume_snapshot,
    create_volume_snapshot_async as _create_volume_snapshot_async,
)
from ..models.create_volume_snapshot import CreateVolumeSnapshot
from .workspace import (
    create_workspace as _create_workspace,
    create_workspace_async as _create_workspace_async,
    get_workspace_info as _get_workspace_info,
    get_workspace_info_async as _get_workspace_info_async,
    list_workspaces as _list_workspaces,
    list_workspaces_async as _list_workspaces_async,
)
from ..models.create_workspace_request import CreateWorkspaceRequest
from ..models.create_workspace_response import CreateWorkspaceResponse
from ..models.get_workspace_info_response import GetWorkspaceInfoResponse
from ..models.list_workspaces import ListWorkspaces
from .ebsdelete_volume_snapshot import (
    delete_snapshot as _delete_snapshot,
    delete_snapshot_async as _delete_snapshot_async,
)
from .ebsdelete_volume import (
    delete_volume as _delete_volume,
    delete_volume_async as _delete_volume_async,
)
from ..models.delete_volume import DeleteVolume
from .ec2detach_volume_from_instance import (
    detach_volume_from_instance as _detach_volume_from_instance,
    detach_volume_from_instance_async as _detach_volume_from_instance_async,
)
from ..models.detach_volume_from_instance import DetachVolumeFromInstance
from .ec2 import (
    get_instance as _get_instance,
    get_instance_async as _get_instance_async,
    get_instance_list as _get_instance_list,
    get_instance_list_async as _get_instance_list_async,
)
from ..models.get_instance_response import GetInstanceResponse
from ..models.get_instance_list import GetInstanceList
from .instance import (
    get_instance_by_id as _get_instance_by_id,
    get_instance_by_id_async as _get_instance_by_id_async,
)
from ..models.get_instance_by_id_response import GetInstanceByIdResponse
from .ec2instance_volume import (
    get_instance_volumes as _get_instance_volumes,
    get_instance_volumes_async as _get_instance_volumes_async,
)
from ..models.get_instance_volumes import GetInstanceVolumes
from .ebssnapshot import (
    get_snapshot as _get_snapshot,
    get_snapshot_async as _get_snapshot_async,
)
from ..models.get_snapshot import GetSnapshot
from .ebsvolume import (
    get_volume as _get_volume,
    get_volume_async as _get_volume_async,
    get_volume_list as _get_volume_list,
    get_volume_list_async as _get_volume_list_async,
)
from ..models.get_volume_response import GetVolumeResponse
from ..models.get_volume_list import GetVolumeList
from .workspacemigrate import (
    migrate_workspace as _migrate_workspace,
    migrate_workspace_async as _migrate_workspace_async,
)
from ..models.migrate_workspace_request import MigrateWorkspaceRequest
from .instancereboot import (
    reboot_instance as _reboot_instance,
    reboot_instance_async as _reboot_instance_async,
)
from .workspacereboot import (
    reboot_workspace as _reboot_workspace,
    reboot_workspace_async as _reboot_workspace_async,
)
from ..models.reboot_workspace_request import RebootWorkspaceRequest
from .workspacerebuild import (
    rebuild_workspace as _rebuild_workspace,
    rebuild_workspace_async as _rebuild_workspace_async,
)
from ..models.rebuild_workspace_request import RebuildWorkspaceRequest
from .workspaceremove import (
    remove_workspace as _remove_workspace,
    remove_workspace_async as _remove_workspace_async,
)
from ..models.remove_workspace_request import RemoveWorkspaceRequest
from .workspacerestore import (
    restore_workspace as _restore_workspace,
    restore_workspace_async as _restore_workspace_async,
)
from ..models.restore_workspace_request import RestoreWorkspaceRequest
from .instancestart import (
    start_instance as _start_instance,
    start_instance_async as _start_instance_async,
)
from .workspacestart import (
    start_workspace as _start_workspace,
    start_workspace_async as _start_workspace_async,
)
from ..models.start_workspace_request import StartWorkspaceRequest
from .instancestop import (
    stop_instance as _stop_instance,
    stop_instance_async as _stop_instance_async,
)
from .workspacestop import (
    stop_workspace as _stop_workspace,
    stop_workspace_async as _stop_workspace_async,
)
from ..models.stop_workspace_request import StopWorkspaceRequest
from .instanceterminate import (
    terminate_instance as _terminate_instance,
    terminate_instance_async as _terminate_instance_async,
)
from ..models.terminate_instance import TerminateInstance
from .workspaceupdate import (
    update_workspace as _update_workspace,
    update_workspace_async as _update_workspace_async,
)
from ..models.update_workspace_request import UpdateWorkspaceRequest
from ..models.update_workspace_response import UpdateWorkspaceResponse

from pydantic import Field
from typing import Any, Optional, Union

from ..client import Client
import httpx


class AmazonWebservices:
    def __init__(self, *, instance_id: str, client: httpx.Client):
        base_url = str(client.base_url).rstrip("/")
        new_headers = {
            k: v for k, v in client.headers.items() if k not in ["content-type"]
        }
        new_client = httpx.Client(
            base_url=base_url + f"/elements_/v3/element/instances/{instance_id}",
            headers=new_headers,
            timeout=100,
        )
        new_client_async = httpx.AsyncClient(
            base_url=base_url + f"/elements_/v3/element/instances/{instance_id}",
            headers=new_headers,
            timeout=100,
        )
        self.client = (
            Client(
                base_url="",  # this will be overridden by the base_url in the Client constructor
            )
            .set_httpx_client(new_client)
            .set_async_httpx_client(new_client_async)
        )

    def attach_volume_to_instance(
        self,
        *,
        device: str,
        instance_id: str,
        volume_id: str,
    ) -> Optional[Union[DefaultError, list["AttachVolumeToInstance"]]]:
        return _attach_volume_to_instance(
            client=self.client,
            device=device,
            instance_id=instance_id,
            volume_id=volume_id,
        )

    async def attach_volume_to_instance_async(
        self,
        *,
        device: str,
        instance_id: str,
        volume_id: str,
    ) -> Optional[Union[DefaultError, list["AttachVolumeToInstance"]]]:
        return await _attach_volume_to_instance_async(
            client=self.client,
            device=device,
            instance_id=instance_id,
            volume_id=volume_id,
        )

    def create_instance_from_launch_template(
        self,
        *,
        tag_specification_1_resource_type: Optional[str] = None,
        tag_specification_1_tag_1_key: Optional[str] = None,
        instance_name: str,
        launch_template_id: str,
        max_count: Optional[int] = None,
        min_count: Optional[int] = None,
    ) -> Optional[Union[DefaultError, list["CreateInstanceFromLaunchTemplate"]]]:
        return _create_instance_from_launch_template(
            client=self.client,
            tag_specification_1_resource_type=tag_specification_1_resource_type,
            tag_specification_1_tag_1_key=tag_specification_1_tag_1_key,
            instance_name=instance_name,
            launch_template_id=launch_template_id,
            max_count=max_count,
            min_count=min_count,
        )

    async def create_instance_from_launch_template_async(
        self,
        *,
        tag_specification_1_resource_type: Optional[str] = None,
        tag_specification_1_tag_1_key: Optional[str] = None,
        instance_name: str,
        launch_template_id: str,
        max_count: Optional[int] = None,
        min_count: Optional[int] = None,
    ) -> Optional[Union[DefaultError, list["CreateInstanceFromLaunchTemplate"]]]:
        return await _create_instance_from_launch_template_async(
            client=self.client,
            tag_specification_1_resource_type=tag_specification_1_resource_type,
            tag_specification_1_tag_1_key=tag_specification_1_tag_1_key,
            instance_name=instance_name,
            launch_template_id=launch_template_id,
            max_count=max_count,
            min_count=min_count,
        )

    def create_volume(
        self,
        *,
        availability_zone: str,
        volume_type: str,
        encrypted: Optional[bool] = False,
        throughput: Optional[int] = None,
        iops: Optional[int] = None,
        size_in_gi_bs: int,
        snapshot_id: Optional[str] = None,
    ) -> Optional[Union[DefaultError, list["CreateVolume"]]]:
        return _create_volume(
            client=self.client,
            availability_zone=availability_zone,
            volume_type=volume_type,
            encrypted=encrypted,
            throughput=throughput,
            iops=iops,
            size_in_gi_bs=size_in_gi_bs,
            snapshot_id=snapshot_id,
        )

    async def create_volume_async(
        self,
        *,
        availability_zone: str,
        volume_type: str,
        encrypted: Optional[bool] = False,
        throughput: Optional[int] = None,
        iops: Optional[int] = None,
        size_in_gi_bs: int,
        snapshot_id: Optional[str] = None,
    ) -> Optional[Union[DefaultError, list["CreateVolume"]]]:
        return await _create_volume_async(
            client=self.client,
            availability_zone=availability_zone,
            volume_type=volume_type,
            encrypted=encrypted,
            throughput=throughput,
            iops=iops,
            size_in_gi_bs=size_in_gi_bs,
            snapshot_id=snapshot_id,
        )

    def create_volume_snapshot(
        self,
        *,
        volume_id: str,
        description: Optional[str] = None,
    ) -> Optional[Union[DefaultError, list["CreateVolumeSnapshot"]]]:
        return _create_volume_snapshot(
            client=self.client,
            volume_id=volume_id,
            description=description,
        )

    async def create_volume_snapshot_async(
        self,
        *,
        volume_id: str,
        description: Optional[str] = None,
    ) -> Optional[Union[DefaultError, list["CreateVolumeSnapshot"]]]:
        return await _create_volume_snapshot_async(
            client=self.client,
            volume_id=volume_id,
            description=description,
        )

    def create_workspace(
        self,
        *,
        body: CreateWorkspaceRequest,
    ) -> Optional[Union[CreateWorkspaceResponse, DefaultError]]:
        return _create_workspace(
            client=self.client,
            body=body,
        )

    async def create_workspace_async(
        self,
        *,
        body: CreateWorkspaceRequest,
    ) -> Optional[Union[CreateWorkspaceResponse, DefaultError]]:
        return await _create_workspace_async(
            client=self.client,
            body=body,
        )

    def get_workspace_info(
        self,
        id: str,
    ) -> Optional[Union[DefaultError, GetWorkspaceInfoResponse]]:
        return _get_workspace_info(
            client=self.client,
            id=id,
        )

    async def get_workspace_info_async(
        self,
        id: str,
    ) -> Optional[Union[DefaultError, GetWorkspaceInfoResponse]]:
        return await _get_workspace_info_async(
            client=self.client,
            id=id,
        )

    def list_workspaces(
        self,
    ) -> Optional[Union[DefaultError, list["ListWorkspaces"]]]:
        return _list_workspaces(
            client=self.client,
        )

    async def list_workspaces_async(
        self,
    ) -> Optional[Union[DefaultError, list["ListWorkspaces"]]]:
        return await _list_workspaces_async(
            client=self.client,
        )

    def delete_snapshot(
        self,
        *,
        snapshot_id: str,
    ) -> Optional[Union[Any, DefaultError]]:
        return _delete_snapshot(
            client=self.client,
            snapshot_id=snapshot_id,
        )

    async def delete_snapshot_async(
        self,
        *,
        snapshot_id: str,
    ) -> Optional[Union[Any, DefaultError]]:
        return await _delete_snapshot_async(
            client=self.client,
            snapshot_id=snapshot_id,
        )

    def delete_volume(
        self,
        *,
        volume_id: str,
    ) -> Optional[Union[DefaultError, list["DeleteVolume"]]]:
        return _delete_volume(
            client=self.client,
            volume_id=volume_id,
        )

    async def delete_volume_async(
        self,
        *,
        volume_id: str,
    ) -> Optional[Union[DefaultError, list["DeleteVolume"]]]:
        return await _delete_volume_async(
            client=self.client,
            volume_id=volume_id,
        )

    def detach_volume_from_instance(
        self,
        *,
        volume_id: str,
        instance_id: str,
    ) -> Optional[Union[DefaultError, list["DetachVolumeFromInstance"]]]:
        return _detach_volume_from_instance(
            client=self.client,
            volume_id=volume_id,
            instance_id=instance_id,
        )

    async def detach_volume_from_instance_async(
        self,
        *,
        volume_id: str,
        instance_id: str,
    ) -> Optional[Union[DefaultError, list["DetachVolumeFromInstance"]]]:
        return await _detach_volume_from_instance_async(
            client=self.client,
            volume_id=volume_id,
            instance_id=instance_id,
        )

    def get_instance(
        self,
        instance_id: str,
        *,
        service_name: Optional[str] = "ec2",
        action: Optional[str] = None,
    ) -> Optional[Union[DefaultError, GetInstanceResponse]]:
        return _get_instance(
            client=self.client,
            instance_id=instance_id,
            service_name=service_name,
            action=action,
        )

    async def get_instance_async(
        self,
        instance_id: str,
        *,
        service_name: Optional[str] = "ec2",
        action: Optional[str] = None,
    ) -> Optional[Union[DefaultError, GetInstanceResponse]]:
        return await _get_instance_async(
            client=self.client,
            instance_id=instance_id,
            service_name=service_name,
            action=action,
        )

    def get_instance_list(
        self,
        *,
        action: Optional[str] = "DescribeInstances",
        service_name: Optional[str] = "ec2",
    ) -> Optional[Union[DefaultError, list["GetInstanceList"]]]:
        return _get_instance_list(
            client=self.client,
            action=action,
            service_name=service_name,
        )

    async def get_instance_list_async(
        self,
        *,
        action: Optional[str] = "DescribeInstances",
        service_name: Optional[str] = "ec2",
    ) -> Optional[Union[DefaultError, list["GetInstanceList"]]]:
        return await _get_instance_list_async(
            client=self.client,
            action=action,
            service_name=service_name,
        )

    def get_instance_by_id(
        self,
        instance_id: str,
    ) -> Optional[Union[DefaultError, GetInstanceByIdResponse]]:
        return _get_instance_by_id(
            client=self.client,
            instance_id=instance_id,
        )

    async def get_instance_by_id_async(
        self,
        instance_id: str,
    ) -> Optional[Union[DefaultError, GetInstanceByIdResponse]]:
        return await _get_instance_by_id_async(
            client=self.client,
            instance_id=instance_id,
        )

    def get_instance_volumes(
        self,
        *,
        filter_1_name: Optional[str] = "attachment.instance-id",
        instance_id: str,
    ) -> Optional[Union[DefaultError, list["GetInstanceVolumes"]]]:
        return _get_instance_volumes(
            client=self.client,
            filter_1_name=filter_1_name,
            instance_id=instance_id,
        )

    async def get_instance_volumes_async(
        self,
        *,
        filter_1_name: Optional[str] = "attachment.instance-id",
        instance_id: str,
    ) -> Optional[Union[DefaultError, list["GetInstanceVolumes"]]]:
        return await _get_instance_volumes_async(
            client=self.client,
            filter_1_name=filter_1_name,
            instance_id=instance_id,
        )

    def get_snapshot(
        self,
        *,
        snapshot_id: str,
    ) -> Optional[Union[DefaultError, list["GetSnapshot"]]]:
        return _get_snapshot(
            client=self.client,
            snapshot_id=snapshot_id,
        )

    async def get_snapshot_async(
        self,
        *,
        snapshot_id: str,
    ) -> Optional[Union[DefaultError, list["GetSnapshot"]]]:
        return await _get_snapshot_async(
            client=self.client,
            snapshot_id=snapshot_id,
        )

    def get_volume(
        self,
        volume_id: str,
    ) -> Optional[Union[DefaultError, GetVolumeResponse]]:
        return _get_volume(
            client=self.client,
            volume_id=volume_id,
        )

    async def get_volume_async(
        self,
        volume_id: str,
    ) -> Optional[Union[DefaultError, GetVolumeResponse]]:
        return await _get_volume_async(
            client=self.client,
            volume_id=volume_id,
        )

    def get_volume_list(
        self,
    ) -> Optional[Union[DefaultError, list["GetVolumeList"]]]:
        return _get_volume_list(
            client=self.client,
        )

    async def get_volume_list_async(
        self,
    ) -> Optional[Union[DefaultError, list["GetVolumeList"]]]:
        return await _get_volume_list_async(
            client=self.client,
        )

    def migrate_workspace(
        self,
        *,
        body: MigrateWorkspaceRequest,
    ) -> Optional[Union[Any, DefaultError]]:
        return _migrate_workspace(
            client=self.client,
            body=body,
        )

    async def migrate_workspace_async(
        self,
        *,
        body: MigrateWorkspaceRequest,
    ) -> Optional[Union[Any, DefaultError]]:
        return await _migrate_workspace_async(
            client=self.client,
            body=body,
        )

    def reboot_instance(
        self,
        *,
        instance_id: str,
    ) -> Optional[Union[Any, DefaultError]]:
        return _reboot_instance(
            client=self.client,
            instance_id=instance_id,
        )

    async def reboot_instance_async(
        self,
        *,
        instance_id: str,
    ) -> Optional[Union[Any, DefaultError]]:
        return await _reboot_instance_async(
            client=self.client,
            instance_id=instance_id,
        )

    def reboot_workspace(
        self,
        *,
        body: RebootWorkspaceRequest,
    ) -> Optional[Union[Any, DefaultError]]:
        return _reboot_workspace(
            client=self.client,
            body=body,
        )

    async def reboot_workspace_async(
        self,
        *,
        body: RebootWorkspaceRequest,
    ) -> Optional[Union[Any, DefaultError]]:
        return await _reboot_workspace_async(
            client=self.client,
            body=body,
        )

    def rebuild_workspace(
        self,
        *,
        body: RebuildWorkspaceRequest,
    ) -> Optional[Union[Any, DefaultError]]:
        return _rebuild_workspace(
            client=self.client,
            body=body,
        )

    async def rebuild_workspace_async(
        self,
        *,
        body: RebuildWorkspaceRequest,
    ) -> Optional[Union[Any, DefaultError]]:
        return await _rebuild_workspace_async(
            client=self.client,
            body=body,
        )

    def remove_workspace(
        self,
        *,
        body: RemoveWorkspaceRequest,
    ) -> Optional[Union[Any, DefaultError]]:
        return _remove_workspace(
            client=self.client,
            body=body,
        )

    async def remove_workspace_async(
        self,
        *,
        body: RemoveWorkspaceRequest,
    ) -> Optional[Union[Any, DefaultError]]:
        return await _remove_workspace_async(
            client=self.client,
            body=body,
        )

    def restore_workspace(
        self,
        *,
        body: RestoreWorkspaceRequest,
    ) -> Optional[Union[Any, DefaultError]]:
        return _restore_workspace(
            client=self.client,
            body=body,
        )

    async def restore_workspace_async(
        self,
        *,
        body: RestoreWorkspaceRequest,
    ) -> Optional[Union[Any, DefaultError]]:
        return await _restore_workspace_async(
            client=self.client,
            body=body,
        )

    def start_instance(
        self,
        *,
        instance_id: str,
    ) -> Optional[Union[Any, DefaultError]]:
        return _start_instance(
            client=self.client,
            instance_id=instance_id,
        )

    async def start_instance_async(
        self,
        *,
        instance_id: str,
    ) -> Optional[Union[Any, DefaultError]]:
        return await _start_instance_async(
            client=self.client,
            instance_id=instance_id,
        )

    def start_workspace(
        self,
        *,
        body: StartWorkspaceRequest,
    ) -> Optional[Union[Any, DefaultError]]:
        return _start_workspace(
            client=self.client,
            body=body,
        )

    async def start_workspace_async(
        self,
        *,
        body: StartWorkspaceRequest,
    ) -> Optional[Union[Any, DefaultError]]:
        return await _start_workspace_async(
            client=self.client,
            body=body,
        )

    def stop_instance(
        self,
        *,
        instance_id: str,
    ) -> Optional[Union[Any, DefaultError]]:
        return _stop_instance(
            client=self.client,
            instance_id=instance_id,
        )

    async def stop_instance_async(
        self,
        *,
        instance_id: str,
    ) -> Optional[Union[Any, DefaultError]]:
        return await _stop_instance_async(
            client=self.client,
            instance_id=instance_id,
        )

    def stop_workspace(
        self,
        *,
        body: StopWorkspaceRequest,
    ) -> Optional[Union[Any, DefaultError]]:
        return _stop_workspace(
            client=self.client,
            body=body,
        )

    async def stop_workspace_async(
        self,
        *,
        body: StopWorkspaceRequest,
    ) -> Optional[Union[Any, DefaultError]]:
        return await _stop_workspace_async(
            client=self.client,
            body=body,
        )

    def terminate_instance(
        self,
        *,
        instance_id: str,
    ) -> Optional[Union[DefaultError, list["TerminateInstance"]]]:
        return _terminate_instance(
            client=self.client,
            instance_id=instance_id,
        )

    async def terminate_instance_async(
        self,
        *,
        instance_id: str,
    ) -> Optional[Union[DefaultError, list["TerminateInstance"]]]:
        return await _terminate_instance_async(
            client=self.client,
            instance_id=instance_id,
        )

    def update_workspace(
        self,
        *,
        body: UpdateWorkspaceRequest,
    ) -> Optional[Union[DefaultError, UpdateWorkspaceResponse]]:
        return _update_workspace(
            client=self.client,
            body=body,
        )

    async def update_workspace_async(
        self,
        *,
        body: UpdateWorkspaceRequest,
    ) -> Optional[Union[DefaultError, UpdateWorkspaceResponse]]:
        return await _update_workspace_async(
            client=self.client,
            body=body,
        )
