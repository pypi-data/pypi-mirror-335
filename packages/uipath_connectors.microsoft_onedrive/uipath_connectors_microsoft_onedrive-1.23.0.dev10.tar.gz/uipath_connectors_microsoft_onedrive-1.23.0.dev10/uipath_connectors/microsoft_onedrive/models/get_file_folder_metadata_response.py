from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.get_file_folder_metadata_response_created_by import (
    GetFileFolderMetadataResponseCreatedBy,
)
from ..models.get_file_folder_metadata_response_file_system_info import (
    GetFileFolderMetadataResponseFileSystemInfo,
)
from ..models.get_file_folder_metadata_response_folder import (
    GetFileFolderMetadataResponseFolder,
)
from ..models.get_file_folder_metadata_response_last_modified_by import (
    GetFileFolderMetadataResponseLastModifiedBy,
)
from ..models.get_file_folder_metadata_response_parent_reference import (
    GetFileFolderMetadataResponseParentReference,
)
import datetime


class GetFileFolderMetadataResponse(BaseModel):
    """
    Attributes:
        c_tag (Optional[str]): A tag that indicates the version of the file or folder. Example:
                "c:{40751C10-227C-4700-822A-B587B993B0A6},0".
        created_by (Optional[GetFileFolderMetadataResponseCreatedBy]):
        created_date_time (Optional[datetime.datetime]): The date and time when the item was created. Example:
                2024-06-25T06:36:10Z.
        e_tag (Optional[str]): A unique identifier for the file or folder version. Example:
                "{40751C10-227C-4700-822A-B587B993B0A6},1".
        file_system_info (Optional[GetFileFolderMetadataResponseFileSystemInfo]):
        folder (Optional[GetFileFolderMetadataResponseFolder]):
        id (Optional[str]): A unique identifier for the file or folder. Example: 01BX6K4RQQDR2UA7BCABDYEKVVQ64ZHMFG.
        last_modified_by (Optional[GetFileFolderMetadataResponseLastModifiedBy]):
        last_modified_date_time (Optional[datetime.datetime]): The date and time when the item was last modified.
                Example: 2025-01-25T04:41:46Z.
        name (Optional[str]): The name of the file or folder. Example: NewCopy.
        parent_reference (Optional[GetFileFolderMetadataResponseParentReference]):
        size (Optional[int]): The size of the file or folder in bytes. Example: 676563.0.
        web_url (Optional[str]): The web URL to access the file or folder online. Example: https://uipathstaging-
                my.sharepoint.com/personal/devuser3_uipathstaging_onmicrosoft_com/Documents/207/NewCopy.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    c_tag: Optional[str] = Field(alias="cTag", default=None)
    created_by: Optional["GetFileFolderMetadataResponseCreatedBy"] = Field(
        alias="createdBy", default=None
    )
    created_date_time: Optional[datetime.datetime] = Field(
        alias="createdDateTime", default=None
    )
    e_tag: Optional[str] = Field(alias="eTag", default=None)
    file_system_info: Optional["GetFileFolderMetadataResponseFileSystemInfo"] = Field(
        alias="fileSystemInfo", default=None
    )
    folder: Optional["GetFileFolderMetadataResponseFolder"] = Field(
        alias="folder", default=None
    )
    id: Optional[str] = Field(alias="id", default=None)
    last_modified_by: Optional["GetFileFolderMetadataResponseLastModifiedBy"] = Field(
        alias="lastModifiedBy", default=None
    )
    last_modified_date_time: Optional[datetime.datetime] = Field(
        alias="lastModifiedDateTime", default=None
    )
    name: Optional[str] = Field(alias="name", default=None)
    parent_reference: Optional["GetFileFolderMetadataResponseParentReference"] = Field(
        alias="parentReference", default=None
    )
    size: Optional[int] = Field(alias="size", default=None)
    web_url: Optional[str] = Field(alias="webUrl", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["GetFileFolderMetadataResponse"], src_dict: Dict[str, Any]):
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
