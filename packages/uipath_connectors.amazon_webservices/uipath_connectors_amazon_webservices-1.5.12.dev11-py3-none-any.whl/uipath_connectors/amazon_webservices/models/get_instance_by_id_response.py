from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.get_instance_by_id_response_tags_array_item_ref import (
    GetInstanceByIdResponseTagsArrayItemRef,
)
import datetime


class GetInstanceByIdResponse(BaseModel):
    """
    Attributes:
        availability_zone (Optional[str]): The Availability zone Example: eu-west-3c.
        creation_date (Optional[datetime.datetime]): The Creation date Example: 2024-08-13T10:08:51.000Z.
        hibernation_enabled (Optional[bool]): The Hibernation enabled
        image_id (Optional[str]): The Image ID Example: ami-06ce55df7975baa3b.
        instance_id (Optional[str]): The Instance ID Example: i-0a97b6b85b5319c2c.
        instance_state (Optional[str]): The Instance state Example: running.
        instance_type (Optional[str]): The Instance type Example: t2.micro.
        key_pair_name (Optional[str]): The Key pair name Example: MyWindowsMachineKeys.
        private_dns_name (Optional[str]): The Private dns name Example: ip-172-31-40-115.eu-west-3.compute.internal.
        private_i_pv_4_address (Optional[str]): The Private i pv 4 address Example: 172.31.40.115.
        public_dns (Optional[str]): The Public dns Example: ec2-51-44-19-8.eu-west-3.compute.amazonaws.com.
        public_i_pv_4_address (Optional[str]): The Public i pv 4 address Example: 51.44.19.8.
        subnet_id (Optional[str]): The Subnet ID Example: subnet-bd6ef4f0.
        tags (Optional[list['GetInstanceByIdResponseTagsArrayItemRef']]):
        virtual_private_cloud_id (Optional[str]): The Virtual private cloud ID Example: vpc-f9283b90.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    availability_zone: Optional[str] = Field(alias="AvailabilityZone", default=None)
    creation_date: Optional[datetime.datetime] = Field(
        alias="CreationDate", default=None
    )
    hibernation_enabled: Optional[bool] = Field(
        alias="HibernationEnabled", default=None
    )
    image_id: Optional[str] = Field(alias="ImageId", default=None)
    instance_id: Optional[str] = Field(alias="InstanceId", default=None)
    instance_state: Optional[str] = Field(alias="InstanceState", default=None)
    instance_type: Optional[str] = Field(alias="InstanceType", default=None)
    key_pair_name: Optional[str] = Field(alias="KeyPairName", default=None)
    private_dns_name: Optional[str] = Field(alias="PrivateDnsName", default=None)
    private_i_pv_4_address: Optional[str] = Field(
        alias="PrivateIPv4Address", default=None
    )
    public_dns: Optional[str] = Field(alias="PublicDns", default=None)
    public_i_pv_4_address: Optional[str] = Field(
        alias="PublicIPv4Address", default=None
    )
    subnet_id: Optional[str] = Field(alias="SubnetId", default=None)
    tags: Optional[list["GetInstanceByIdResponseTagsArrayItemRef"]] = Field(
        alias="Tags", default=None
    )
    virtual_private_cloud_id: Optional[str] = Field(
        alias="VirtualPrivateCloudId", default=None
    )

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["GetInstanceByIdResponse"], src_dict: Dict[str, Any]):
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
