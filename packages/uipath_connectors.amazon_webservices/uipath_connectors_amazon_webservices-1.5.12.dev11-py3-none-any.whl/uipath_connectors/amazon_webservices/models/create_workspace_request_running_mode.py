from enum import Enum


class CreateWorkspaceRequestRunningMode(str, Enum):
    ALWAYSON = "ALWAYS_ON"
    AUTOSTOP = "AUTO_STOP"

    def __str__(self) -> str:
        return str(self.value)
