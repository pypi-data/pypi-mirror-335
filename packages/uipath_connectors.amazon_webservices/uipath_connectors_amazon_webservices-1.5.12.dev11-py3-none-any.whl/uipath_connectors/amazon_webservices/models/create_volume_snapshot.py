from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

import datetime


class CreateVolumeSnapshot(BaseModel):
    """
    Attributes:
        xmlns (Optional[str]): The namespace URI used for XML-based API responses. Example:
                http://ec2.amazonaws.com/doc/2016-11-15/.
        encrypted (Optional[bool]): Indicates whether the snapshot is encrypted.
        owner_id (Optional[int]): The AWS account ID of the snapshot's owner. Example: 616128032092.0.
        request_id (Optional[str]): A unique identifier for the API request. Example:
                5216f3a3-a53c-43d6-9cab-2cad4b1492ca.
        snapshot_id (Optional[str]): A unique identifier for the EBS snapshot. Example: snap-0ef4ca030829dda0e.
        start_time (Optional[datetime.datetime]): The date and time when the snapshot process started. Example:
                2024-08-22T10:22:12.794Z.
        status (Optional[str]): The current state of the snapshot, such as 'pending' or 'completed'. Example: pending.
        volume_id (Optional[str]): A unique identifier for the EBS volume associated with the snapshot. Example:
                vol-0838f7769d5c269a3.
        volume_size (Optional[int]): The size of the EBS volume from which the snapshot was created, in GiB. Example:
                30.0.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    xmlns: Optional[str] = Field(alias="@xmlns", default=None)
    encrypted: Optional[bool] = Field(alias="encrypted", default=None)
    owner_id: Optional[int] = Field(alias="ownerId", default=None)
    request_id: Optional[str] = Field(alias="requestId", default=None)
    snapshot_id: Optional[str] = Field(alias="snapshotId", default=None)
    start_time: Optional[datetime.datetime] = Field(alias="startTime", default=None)
    status: Optional[str] = Field(alias="status", default=None)
    volume_id: Optional[str] = Field(alias="volumeId", default=None)
    volume_size: Optional[int] = Field(alias="volumeSize", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["CreateVolumeSnapshot"], src_dict: Dict[str, Any]):
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
