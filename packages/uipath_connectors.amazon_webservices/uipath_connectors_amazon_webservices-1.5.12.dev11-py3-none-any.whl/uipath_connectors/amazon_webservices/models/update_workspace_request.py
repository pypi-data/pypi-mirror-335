from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.update_workspace_request_compute_type import (
    UpdateWorkspaceRequestComputeType,
)
from ..models.update_workspace_request_intended_state import (
    UpdateWorkspaceRequestIntendedState,
)
from ..models.update_workspace_request_running_mode import (
    UpdateWorkspaceRequestRunningMode,
)
from ..models.update_workspace_request_update_action import (
    UpdateWorkspaceRequestUpdateAction,
)
from ..models.update_workspace_request_volume_to_resize import (
    UpdateWorkspaceRequestVolumeToResize,
)


class UpdateWorkspaceRequest(BaseModel):
    """
    Attributes:
        update_action (UpdateWorkspaceRequestUpdateAction): The update action to perform. Default:
                UpdateWorkspaceRequestUpdateAction.MODIFY_COMPUTE_TYPE.
        workspace_id (str): The identifier of the workSpace on which the operation needs to be performed. Example:
                ws-2384y.
        compute_type (Optional[UpdateWorkspaceRequestComputeType]): The compute type
        intended_state (Optional[UpdateWorkspaceRequestIntendedState]): The new state of the WorkSpace. To maintain a
                WorkSpace without being interrupted, set its state to 'AdminMaintenance'. Example: Available.
        running_mode (Optional[UpdateWorkspaceRequestRunningMode]): The running mode.
        running_mode_auto_step_timeout (Optional[int]): The number of minutes (in 60-minute intervals) after a user logs
                off when WorkSpace is automatically stopped. The value should be provided as 60-minute increments. Taken into
                consideration when RunningMode is set to `AutoStop'. Example: 1.0.
        volume_new_size (Optional[int]): The new size of the volume, in gigabytes. Example: 1.0.
        volume_to_resize (Optional[UpdateWorkspaceRequestVolumeToResize]): Specifies the volume to resize. Default:
                UpdateWorkspaceRequestVolumeToResize.USER_VOLUME.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    workspace_id: str = Field(alias="WorkspaceId")
    update_action: "UpdateWorkspaceRequestUpdateAction" = Field(
        alias="UpdateAction",
        default=UpdateWorkspaceRequestUpdateAction.MODIFY_COMPUTE_TYPE,
    )
    compute_type: Optional["UpdateWorkspaceRequestComputeType"] = Field(
        alias="ComputeType", default=None
    )
    intended_state: Optional["UpdateWorkspaceRequestIntendedState"] = Field(
        alias="IntendedState", default=None
    )
    running_mode: Optional["UpdateWorkspaceRequestRunningMode"] = Field(
        alias="RunningMode", default=None
    )
    running_mode_auto_step_timeout: Optional[int] = Field(
        alias="RunningModeAutoStepTimeout", default=None
    )
    volume_new_size: Optional[int] = Field(alias="VolumeNewSize", default=None)
    volume_to_resize: Optional["UpdateWorkspaceRequestVolumeToResize"] = Field(
        alias="VolumeToResize", default=UpdateWorkspaceRequestVolumeToResize.USER_VOLUME
    )

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["UpdateWorkspaceRequest"], src_dict: Dict[str, Any]):
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
