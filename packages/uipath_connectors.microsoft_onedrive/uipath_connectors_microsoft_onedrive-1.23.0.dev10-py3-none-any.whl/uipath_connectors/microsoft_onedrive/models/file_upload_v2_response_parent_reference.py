from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type



class FileUploadV2ResponseParentReference(BaseModel):
    """
    Attributes:
        drive_id (Optional[str]): The Parent reference drive ID Example:
                b!wjQhbOjjl0OF8lEnwz6vV0FqJbJQb_ZNrUVz5cKrQofzYipZHU0dTJLZYhwDixYd.
        drive_type (Optional[str]): The Parent reference drive type Example: documentLibrary.
        id (Optional[str]): The Parent reference ID Example: 012GK26CJAYYNL5LWLOFALO6TQ4VNZLFGY.
        name (Optional[str]): The Parent reference name Example: Folder10.
        path (Optional[str]): The Parent reference path Example:
                /drives/b!wjQhbOjjl0OF8lEnwz6vV0FqJbJQb_ZNrUVz5cKrQofzYipZHU0dTJLZYhwDixYd/root:/Folder10.
        site_id (Optional[str]): The Parent reference site ID Example: 6c2134c2-e3e8-4397-85f2-5127c33eaf57.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    drive_id: Optional[str] = Field(alias="driveId", default=None)
    drive_type: Optional[str] = Field(alias="driveType", default=None)
    id: Optional[str] = Field(alias="id", default=None)
    name: Optional[str] = Field(alias="name", default=None)
    path: Optional[str] = Field(alias="path", default=None)
    site_id: Optional[str] = Field(alias="siteId", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(
        cls: Type["FileUploadV2ResponseParentReference"], src_dict: Dict[str, Any]
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
