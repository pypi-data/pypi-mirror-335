from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.copy_file_folder_request_parent_reference import (
    CopyFileFolderRequestParentReference,
)


class CopyFileFolderRequest(BaseModel):
    """
    Attributes:
        file_folder_id (str): File or folder to copy Example: string.
        parent_reference (Optional[CopyFileFolderRequestParentReference]):
        name (Optional[str]): New name for the file or folder Example: string.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    file_folder_id: str = Field(alias="fileFolderId")
    parent_reference: Optional["CopyFileFolderRequestParentReference"] = Field(
        alias="parentReference", default=None
    )
    name: Optional[str] = Field(alias="name", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["CopyFileFolderRequest"], src_dict: Dict[str, Any]):
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
