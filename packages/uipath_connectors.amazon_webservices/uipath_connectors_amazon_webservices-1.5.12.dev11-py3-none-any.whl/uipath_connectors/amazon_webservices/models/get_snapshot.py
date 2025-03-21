from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type



class GetSnapshot(BaseModel):
    """
    Attributes:
        encrypted (Optional[bool]): Indicates whether the snapshot is encrypted.
        size_in_gi_bs (Optional[int]): The size of the snapshot in Gibibytes (GiB). Example: 30.0.
        snapshot_id (Optional[str]): A unique identifier for the EBS snapshot. Example: snap-0e6acdeca18ec7d08.
        snapshot_state (Optional[str]): The current state of the EBS snapshot. Example: completed.
        volume_id (Optional[str]): The ID of the EBS volume from which the snapshot was created. Example:
                vol-0838f7769d5c269a3.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    encrypted: Optional[bool] = Field(alias="Encrypted", default=None)
    size_in_gi_bs: Optional[int] = Field(alias="SizeInGiBs", default=None)
    snapshot_id: Optional[str] = Field(alias="SnapshotId", default=None)
    snapshot_state: Optional[str] = Field(alias="SnapshotState", default=None)
    volume_id: Optional[str] = Field(alias="VolumeId", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["GetSnapshot"], src_dict: Dict[str, Any]):
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
