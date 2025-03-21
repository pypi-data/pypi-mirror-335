from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type



class GetFileFolderMetadataResponseParentReference(BaseModel):
    """
    Attributes:
        drive_id (Optional[str]): The unique identifier of the drive containing the parent folder. Example:
                b!DVFqQPEoG0yShqSXvePVy2f9AJ5eEYFJrMwJAEdWoj912uw8AfAWTonhZgO36N2G.
        drive_type (Optional[str]): The type of drive where the parent folder is located. Example: business.
        id (Optional[str]): A unique identifier for the parent folder. Example: 01BX6K4RWWE6YSKAUJKRFYBT3SKHFJ65TT.
        name (Optional[str]): The name of the folder containing the file or folder. Example: 207.
        path (Optional[str]): The full path to the parent folder in the drive. Example:
                /drives/b!DVFqQPEoG0yShqSXvePVy2f9AJ5eEYFJrMwJAEdWoj912uw8AfAWTonhZgO36N2G/root:/207.
        site_id (Optional[str]): The unique identifier of the parent site. Example:
                406a510d-28f1-4c1b-9286-a497bde3d5cb.
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
        cls: Type["GetFileFolderMetadataResponseParentReference"],
        src_dict: Dict[str, Any],
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
