from enum import Enum


class UpdateWorkspaceRequestUpdateAction(str, Enum):
    MODIFY_COMPUTE_TYPE = "Modify Compute Type"
    MODIFY_RUNNING_MODE = "Modify Running Mode"
    MODIFY_STATE = "Modify State"
    MODIFY_TAGS = "Modify Tags"
    MODIFY_VOLUME_SIZE = "Modify Volume Size"

    def __str__(self) -> str:
        return str(self.value)
