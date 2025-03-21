from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

import datetime


class GetInstanceVolumes(BaseModel):
    """
    Attributes:
        availability_zone (Optional[str]): The AWS region's specific availability zone where the volume is stored.
                Example: eu-west-3a.
        creation_date (Optional[datetime.datetime]): The date and time when the volume was created. Example:
                2024-02-29T09:24:29.236Z.
        encrypted (Optional[bool]): Indicates whether the volume is encrypted.
        iops (Optional[int]): The number of input/output operations per second the volume can perform. Example: 3000.0.
        size (Optional[int]): The size of the volume in gibibytes (GiB). Example: 64.0.
        snapshot_id (Optional[str]): The ID of the snapshot used to create the volume. Example: snap-01751a172cee08699.
        throughput (Optional[int]): The throughput of the volume measured in megabytes per second. Example: 125.0.
        volume_id (Optional[str]): The unique identifier for the EBS volume. Example: vol-05d6bfd1f15036c7c.
        volume_state (Optional[str]): The operational state of the volume (e.g., creating, available, in-use). Example:
                in-use.
        volume_type (Optional[str]): The category of the EBS volume based on performance. Example: gp3.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    availability_zone: Optional[str] = Field(alias="AvailabilityZone", default=None)
    creation_date: Optional[datetime.datetime] = Field(
        alias="CreationDate", default=None
    )
    encrypted: Optional[bool] = Field(alias="Encrypted", default=None)
    iops: Optional[int] = Field(alias="IOPS", default=None)
    size: Optional[int] = Field(alias="Size", default=None)
    snapshot_id: Optional[str] = Field(alias="SnapshotId", default=None)
    throughput: Optional[int] = Field(alias="Throughput", default=None)
    volume_id: Optional[str] = Field(alias="VolumeId", default=None)
    volume_state: Optional[str] = Field(alias="VolumeState", default=None)
    volume_type: Optional[str] = Field(alias="VolumeType", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["GetInstanceVolumes"], src_dict: Dict[str, Any]):
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
