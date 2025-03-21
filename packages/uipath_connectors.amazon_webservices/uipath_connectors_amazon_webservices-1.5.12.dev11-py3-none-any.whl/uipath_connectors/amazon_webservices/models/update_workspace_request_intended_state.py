from enum import Enum


class UpdateWorkspaceRequestIntendedState(str, Enum):
    ADMINMAINTENANCE = "ADMIN_MAINTENANCE"
    AVAILABLE = "AVAILABLE"

    def __str__(self) -> str:
        return str(self.value)
