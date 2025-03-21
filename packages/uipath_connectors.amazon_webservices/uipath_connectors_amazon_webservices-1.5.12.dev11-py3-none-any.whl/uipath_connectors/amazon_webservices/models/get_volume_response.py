from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

import datetime


class GetVolumeResponse(BaseModel):
    """
    Attributes:
        availability_zone (Optional[str]): The AWS region's specific zone where the volume is stored. Example: eu-
                west-3c.
        creation_date (Optional[datetime.datetime]): The date and time when the EBS volume was created. Example:
                2024-03-20T21:48:33.850Z.
        encrypted (Optional[bool]): Indicates whether the volume is encrypted for security.
        iops (Optional[int]): The number of I/O operations per second the volume supports. Example: 300.0.
        size (Optional[int]): The storage size of the volume in Gibibytes (GiB). Example: 100.0.
        volume_state (Optional[str]): The operational state of the volume, such as 'available' or 'in-use'. Example:
                available.
        volume_type (Optional[str]): The category of the EBS volume based on performance. Example: gp2.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    availability_zone: Optional[str] = Field(alias="AvailabilityZone", default=None)
    creation_date: Optional[datetime.datetime] = Field(
        alias="CreationDate", default=None
    )
    encrypted: Optional[bool] = Field(alias="Encrypted", default=None)
    iops: Optional[int] = Field(alias="IOPS", default=None)
    size: Optional[int] = Field(alias="Size", default=None)
    volume_state: Optional[str] = Field(alias="VolumeState", default=None)
    volume_type: Optional[str] = Field(alias="VolumeType", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["GetVolumeResponse"], src_dict: Dict[str, Any]):
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
