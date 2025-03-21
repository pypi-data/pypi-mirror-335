from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.terminate_instance_terminate_instances_response_instances_set import (
    TerminateInstanceTerminateInstancesResponseInstancesSet,
)


class TerminateInstanceTerminateInstancesResponse(BaseModel):
    """
    Attributes:
        xmlns (Optional[str]): The XML namespace used in the termination response. Example:
                http://ec2.amazonaws.com/doc/2016-11-15/.
        instances_set (Optional[TerminateInstanceTerminateInstancesResponseInstancesSet]):
        request_id (Optional[str]): The unique identifier for the termination request. Example:
                6224745e-d8ac-45a3-ab3b-4c9b63735721.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    xmlns: Optional[str] = Field(alias="@xmlns", default=None)
    instances_set: Optional[
        "TerminateInstanceTerminateInstancesResponseInstancesSet"
    ] = Field(alias="instancesSet", default=None)
    request_id: Optional[str] = Field(alias="requestId", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(
        cls: Type["TerminateInstanceTerminateInstancesResponse"],
        src_dict: Dict[str, Any],
    ):
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
