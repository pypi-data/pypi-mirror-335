from enum import Enum


class ListWorkspacesComputeType(str, Enum):
    GRAPHICS = "GRAPHICS"
    GRAPHICSPRO = "GRAPHICSPRO"
    PERFORMANCE = "PERFORMANCE"
    POWER = "POWER"
    POWERPRO = "POWERPRO"
    STANDARD = "STANDARD"
    VALUE = "VALUE"

    def __str__(self) -> str:
        return str(self.value)
