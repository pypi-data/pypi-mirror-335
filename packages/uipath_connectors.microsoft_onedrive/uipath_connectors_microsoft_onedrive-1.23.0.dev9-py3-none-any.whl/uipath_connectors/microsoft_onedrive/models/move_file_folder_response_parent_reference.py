from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type



class MoveFileFolderResponseParentReference(BaseModel):
    """
    Attributes:
        drive_id (Optional[str]):  Example: b!_YnPyCC75kOq5OtXNRC1rpGAGXeO4CVNqawKnDOE1YXYbbrpZxdyRZtp0X--PJd5.
        drive_type (Optional[str]):  Example: business.
        id (Optional[str]):  Example: 01EPMICMOI6MDHDWBT4ZHJYPXPKRC7WQB7.
        path (Optional[str]):  Example: /drive/root:/Desktop.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    drive_id: Optional[str] = Field(alias="driveId", default=None)
    drive_type: Optional[str] = Field(alias="driveType", default=None)
    id: Optional[str] = Field(alias="id", default=None)
    path: Optional[str] = Field(alias="path", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(
        cls: Type["MoveFileFolderResponseParentReference"], src_dict: Dict[str, Any]
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
