from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type



class DeleteVolumeDeleteVolumeResponse(BaseModel):
    """
    Attributes:
        xmlns (Optional[str]): Defines the XML namespace for the response Example:
                http://ec2.amazonaws.com/doc/2016-11-15/.
        request_id (Optional[str]): A unique ID to reference the delete volume request Example:
                1b4b5e4e-7da7-471f-8834-b197d75c7404.
        return_ (Optional[bool]): Indicates if the volume deletion was successful Example: True.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    xmlns: Optional[str] = Field(alias="@xmlns", default=None)
    request_id: Optional[str] = Field(alias="requestId", default=None)
    return_: Optional[bool] = Field(alias="return", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(
        cls: Type["DeleteVolumeDeleteVolumeResponse"], src_dict: Dict[str, Any]
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
