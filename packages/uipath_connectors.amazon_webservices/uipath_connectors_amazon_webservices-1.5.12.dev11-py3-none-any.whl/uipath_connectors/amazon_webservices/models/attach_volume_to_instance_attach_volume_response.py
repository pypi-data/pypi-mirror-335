from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

import datetime


class AttachVolumeToInstanceAttachVolumeResponse(BaseModel):
    """
    Attributes:
        xmlns (Optional[str]): The XML namespace associated with the response. Example:
                http://ec2.amazonaws.com/doc/2016-11-15/.
        attach_time (Optional[datetime.datetime]): The timestamp when the volume was attached to the instance. Example:
                2024-08-22T10:42:09.943Z.
        device (Optional[str]): The system device name where the volume is attached. Example: xvdb.
        instance_id (Optional[str]): The unique identifier of the instance to which the volume is attached. Example:
                i-0a97b6b85b5319c2c.
        request_id (Optional[str]): The identifier of the API request for tracking purposes. Example:
                60d2e9c5-7753-4e4f-8775-0c09584abc3e.
        status (Optional[str]): The current status of the volume attachment process. Example: attaching.
        volume_id (Optional[str]): The unique identifier of the EBS volume. Example: vol-0d7d4edda6d305221.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    xmlns: Optional[str] = Field(alias="@xmlns", default=None)
    attach_time: Optional[datetime.datetime] = Field(alias="attachTime", default=None)
    device: Optional[str] = Field(alias="device", default=None)
    instance_id: Optional[str] = Field(alias="instanceId", default=None)
    request_id: Optional[str] = Field(alias="requestId", default=None)
    status: Optional[str] = Field(alias="status", default=None)
    volume_id: Optional[str] = Field(alias="volumeId", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(
        cls: Type["AttachVolumeToInstanceAttachVolumeResponse"],
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
