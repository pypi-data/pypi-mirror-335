from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type



class GetInstanceList(BaseModel):
    """
    Attributes:
        image_id (Optional[str]): The ID of the AMI used to launch the EC2 instance. Example: ami-06ce55df7975baa3b.
        instance_id (Optional[str]): A unique identifier for the specific Amazon EC2 instance. Example:
                i-0a97b6b85b5319c2c.
        instance_state (Optional[str]): The running status of the instance, such as 'running' or 'stopped'. Example:
                stopped.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    image_id: Optional[str] = Field(alias="imageId", default=None)
    instance_id: Optional[str] = Field(alias="instanceId", default=None)
    instance_state: Optional[str] = Field(alias="instanceState", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["GetInstanceList"], src_dict: Dict[str, Any]):
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
