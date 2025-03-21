from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.create_workspace_request_compute_type import (
    CreateWorkspaceRequestComputeType,
)
from ..models.create_workspace_request_running_mode import (
    CreateWorkspaceRequestRunningMode,
)


class CreateWorkspaceRequest(BaseModel):
    """
    Attributes:
        bundle_id (str): The bundle for the WorkSpace. Example: wsb-362t3gdrt.
        directory_id (str): The AWS Directory Service directory for the WorkSpace. Example: d-92670a5e5e.
        user_name (str): The user name for the WorkSpace. It must exist in the AWS Directory Service directory
                associated with the WorkSpace. Example: itautomation-rebuild.
        compute_type (Optional[CreateWorkspaceRequestComputeType]): The compute type Default:
                CreateWorkspaceRequestComputeType.STANDARD.
        computer_name (Optional[str]): Computer name
        ip_address (Optional[str]): Ip address
        root_volume_encryption_enabled (Optional[bool]): Indicates whether the data stored on the root volume is
                encrypted.
        root_volume_size_gb (Optional[int]): The size of the root volume, in gigabytes.
        root_volume_size_gib (Optional[int]): The size of the root volume, in gigabytes.
        running_mode (Optional[CreateWorkspaceRequestRunningMode]): The running mode Default:
                CreateWorkspaceRequestRunningMode.AUTOSTOP.
        running_mode_auto_stop_timeout (Optional[int]): Running mode auto stop timeout
        running_mode_auto_stop_timeout_in_minutes (Optional[int]): The number of minutes (in 60-minute intervals) after
                a user logs off when WorkSpace is automatically stopped. The value should be provided as 60-minute increments.
                Taken into consideration when RunningMode is set to `AutoStop'.
        state (Optional[str]): State
        subnet_id (Optional[str]): Subnet id
        user_volume_encryption_enabled (Optional[bool]): Indicates whether the data stored on the user volume is
                encrypted.
        user_volume_size_gb (Optional[int]): The size of the user storage, in gigabytes.
        user_volume_size_gib (Optional[int]): The size of the user storage, in gigabytes.
        volume_encryption_key (Optional[str]): The symmetric AWS KMS customer master key used to encrypt data stored on
                the WorkSpace. This field is mandatory when the encryption for at least one of user volume or root volume is
                enabled.
        workspace_id (Optional[str]): The workspace id.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    bundle_id: str = Field(alias="BundleId")
    directory_id: str = Field(alias="DirectoryId")
    user_name: str = Field(alias="UserName")
    compute_type: Optional["CreateWorkspaceRequestComputeType"] = Field(
        alias="ComputeType", default=CreateWorkspaceRequestComputeType.STANDARD
    )
    computer_name: Optional[str] = Field(alias="ComputerName", default=None)
    ip_address: Optional[str] = Field(alias="IpAddress", default=None)
    root_volume_encryption_enabled: Optional[bool] = Field(
        alias="RootVolumeEncryptionEnabled", default=None
    )
    root_volume_size_gb: Optional[int] = Field(alias="RootVolumeSizeGb", default=None)
    root_volume_size_gib: Optional[int] = Field(alias="RootVolumeSizeGib", default=None)
    running_mode: Optional["CreateWorkspaceRequestRunningMode"] = Field(
        alias="RunningMode", default=CreateWorkspaceRequestRunningMode.AUTOSTOP
    )
    running_mode_auto_stop_timeout: Optional[int] = Field(
        alias="RunningModeAutoStopTimeout", default=None
    )
    running_mode_auto_stop_timeout_in_minutes: Optional[int] = Field(
        alias="RunningModeAutoStopTimeoutInMinutes", default=None
    )
    state: Optional[str] = Field(alias="State", default=None)
    subnet_id: Optional[str] = Field(alias="SubnetId", default=None)
    user_volume_encryption_enabled: Optional[bool] = Field(
        alias="UserVolumeEncryptionEnabled", default=None
    )
    user_volume_size_gb: Optional[int] = Field(alias="UserVolumeSizeGb", default=None)
    user_volume_size_gib: Optional[int] = Field(alias="UserVolumeSizeGib", default=None)
    volume_encryption_key: Optional[str] = Field(
        alias="VolumeEncryptionKey", default=None
    )
    workspace_id: Optional[str] = Field(alias="WorkspaceId", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["CreateWorkspaceRequest"], src_dict: Dict[str, Any]):
        return cls.model_validate(src_dict)

    @property
    def additional_keys(self) -> list[str]:
        base_fields = self.model_fields.keys()
        return [k for k in self.__dict__ if k not in base_fields]

    def __getitem__(self, key: str) -> Any:
        if key in self.__dict__:
            return self.__dict__[key]
        raise KeyError(key)

    def __setitem__(self, key: str, value: Any) -> None:
        self.__dict__[key] = value

    def __delitem__(self, key: str) -> None:
        if key in self.__dict__:
            del self.__dict__[key]
        else:
            raise KeyError(key)

    def __contains__(self, key: str) -> bool:
        return key in self.__dict__
