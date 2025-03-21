from enum import Enum


class UpdateWorkspaceRequestVolumeToResize(str, Enum):
    ROOT_VOLUME = "RootVolume"
    USER_VOLUME = "UserVolume"

    def __str__(self) -> str:
        return str(self.value)
