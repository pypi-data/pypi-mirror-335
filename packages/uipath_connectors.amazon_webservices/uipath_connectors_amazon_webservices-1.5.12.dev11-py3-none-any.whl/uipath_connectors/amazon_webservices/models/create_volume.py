from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

import datetime


class CreateVolume(BaseModel):
    """
    Attributes:
        xmlns (Optional[str]): Defines the XML namespace for the API response. Example:
                http://ec2.amazonaws.com/doc/2016-11-15/.
        availability_zone (Optional[str]): AWS region area where the volume is stored. Example: eu-west-3c.
        create_time (Optional[datetime.datetime]): The timestamp when the volume was created. Example:
                2024-08-22T11:12:14.000Z.
        encrypted (Optional[bool]): Indicates whether the volume is encrypted.
        iops (Optional[int]): Input/output operations per second for the volume. Example: 7500.0.
        multi_attach_enabled (Optional[bool]): Indicates if the volume can be attached to multiple instances.
        request_id (Optional[str]): The unique identifier for the API request. Example:
                49386bc2-45ad-45d3-a3e4-219f0cae8878.
        size (Optional[int]): The size of the volume in gibibytes (GiB). Example: 150.0.
        status (Optional[str]): Current state of the EBS volume, such as 'creating', 'available', etc. Example:
                creating.
        volume_id (Optional[str]): Unique identifier for the Elastic Block Store volume. Example: vol-08bb0ebf6da7590c3.
        volume_type (Optional[str]): The type of EBS volume, such as gp2 for General Purpose SSD. Example: io1.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    xmlns: Optional[str] = Field(alias="@xmlns", default=None)
    availability_zone: Optional[str] = Field(alias="availabilityZone", default=None)
    create_time: Optional[datetime.datetime] = Field(alias="createTime", default=None)
    encrypted: Optional[bool] = Field(alias="encrypted", default=None)
    iops: Optional[int] = Field(alias="iops", default=None)
    multi_attach_enabled: Optional[bool] = Field(
        alias="multiAttachEnabled", default=None
    )
    request_id: Optional[str] = Field(alias="requestId", default=None)
    size: Optional[int] = Field(alias="size", default=None)
    status: Optional[str] = Field(alias="status", default=None)
    volume_id: Optional[str] = Field(alias="volumeId", default=None)
    volume_type: Optional[str] = Field(alias="volumeType", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["CreateVolume"], src_dict: Dict[str, Any]):
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
