from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.move_file_folder_response_created_by import (
    MoveFileFolderResponseCreatedBy,
)
from ..models.move_file_folder_response_file_system_info import (
    MoveFileFolderResponseFileSystemInfo,
)
from ..models.move_file_folder_response_folder import MoveFileFolderResponseFolder
from ..models.move_file_folder_response_last_modified_by import (
    MoveFileFolderResponseLastModifiedBy,
)
from ..models.move_file_folder_response_parent_reference import (
    MoveFileFolderResponseParentReference,
)
import datetime


class MoveFileFolderResponse(BaseModel):
    """
    Attributes:
        c_tag (Optional[str]):  Example: "c:{975DB3DC-1E0E-4163-9AA9-2D597A708A8A},0".
        created_by (Optional[MoveFileFolderResponseCreatedBy]):
        created_date_time (Optional[datetime.datetime]):  Example: 2022-08-03T11:55:31Z.
        e_tag (Optional[str]):  Example: "{975DB3DC-1E0E-4163-9AA9-2D597A708A8A},3".
        file_system_info (Optional[MoveFileFolderResponseFileSystemInfo]):
        folder (Optional[MoveFileFolderResponseFolder]):
        id (Optional[str]):  Example: 01EPMICMO4WNOZODQ6MNAZVKJNLF5HBCUK.
        last_modified_by (Optional[MoveFileFolderResponseLastModifiedBy]):
        last_modified_date_time (Optional[datetime.datetime]):  Example: 2023-01-05T08:12:00Z.
        name (Optional[str]): An optional new name given to the file or folder after it is moved. If left blank, it
                retains the original name. Example: Fiddler2.
        odata_context (Optional[str]):  Example:
                https://graph.microsoft.com/v1.0/$metadata#users('c9e8974b-1f21-4038-b923-eeb790a41116')/drive/items/$entity.
        parent_reference (Optional[MoveFileFolderResponseParentReference]):
        size (Optional[int]):  Example: 140146.0.
        web_url (Optional[str]):  Example: https://uipath-
                my.sharepoint.com/personal/mohit_achary_uipath_com/Documents/Desktop/Fiddler2.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    c_tag: Optional[str] = Field(alias="cTag", default=None)
    created_by: Optional["MoveFileFolderResponseCreatedBy"] = Field(
        alias="createdBy", default=None
    )
    created_date_time: Optional[datetime.datetime] = Field(
        alias="createdDateTime", default=None
    )
    e_tag: Optional[str] = Field(alias="eTag", default=None)
    file_system_info: Optional["MoveFileFolderResponseFileSystemInfo"] = Field(
        alias="fileSystemInfo", default=None
    )
    folder: Optional["MoveFileFolderResponseFolder"] = Field(
        alias="folder", default=None
    )
    id: Optional[str] = Field(alias="id", default=None)
    last_modified_by: Optional["MoveFileFolderResponseLastModifiedBy"] = Field(
        alias="lastModifiedBy", default=None
    )
    last_modified_date_time: Optional[datetime.datetime] = Field(
        alias="lastModifiedDateTime", default=None
    )
    name: Optional[str] = Field(alias="name", default=None)
    odata_context: Optional[str] = Field(alias="odataContext", default=None)
    parent_reference: Optional["MoveFileFolderResponseParentReference"] = Field(
        alias="parentReference", default=None
    )
    size: Optional[int] = Field(alias="size", default=None)
    web_url: Optional[str] = Field(alias="webUrl", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["MoveFileFolderResponse"], src_dict: Dict[str, Any]):
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
