from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.create_folder_response_created_by import CreateFolderResponseCreatedBy
from ..models.create_folder_response_file_system_info import (
    CreateFolderResponseFileSystemInfo,
)
from ..models.create_folder_response_folder import CreateFolderResponseFolder
from ..models.create_folder_response_last_modified_by import (
    CreateFolderResponseLastModifiedBy,
)
from ..models.create_folder_response_parent_reference import (
    CreateFolderResponseParentReference,
)
import datetime


class CreateFolderResponse(BaseModel):
    """
    Attributes:
        name (str): Name of new folder Example: NewTest.
        c_tag (Optional[str]):  Example: "c:{3680CB34-D1E3-429D-931A-030562234186},0".
        created_by (Optional[CreateFolderResponseCreatedBy]):
        created_date_time (Optional[datetime.datetime]):  Example: 2023-01-13T11:30:30Z.
        e_tag (Optional[str]):  Example: "{3680CB34-D1E3-429D-931A-030562234186},1".
        file_system_info (Optional[CreateFolderResponseFileSystemInfo]):
        folder (Optional[CreateFolderResponseFolder]):
        id (Optional[str]):  Example: 01EPMICMJUZOADNY6RTVBJGGQDAVRCGQMG.
        last_modified_by (Optional[CreateFolderResponseLastModifiedBy]):
        last_modified_date_time (Optional[datetime.datetime]):  Example: 2023-01-13T11:30:30Z.
        odata_context (Optional[str]):  Example: https://graph.microsoft.com/v1.0/$metadata#users('c9e8974b-1f21-4038-
                b923-eeb790a41116')/drive/items('01EPMICMLYBRERYZ3CJBAI72NBEPG7B6A2')/children/$entity.
        parent_reference (Optional[CreateFolderResponseParentReference]):
        size (Optional[int]):
        web_url (Optional[str]):  Example: https://uipath-
                my.sharepoint.com/personal/mohit_achary_uipath_com/Documents/Documents/Office%20Scripts/NewTest.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    name: str = Field(alias="name")
    c_tag: Optional[str] = Field(alias="cTag", default=None)
    created_by: Optional["CreateFolderResponseCreatedBy"] = Field(
        alias="createdBy", default=None
    )
    created_date_time: Optional[datetime.datetime] = Field(
        alias="createdDateTime", default=None
    )
    e_tag: Optional[str] = Field(alias="eTag", default=None)
    file_system_info: Optional["CreateFolderResponseFileSystemInfo"] = Field(
        alias="fileSystemInfo", default=None
    )
    folder: Optional["CreateFolderResponseFolder"] = Field(alias="folder", default=None)
    id: Optional[str] = Field(alias="id", default=None)
    last_modified_by: Optional["CreateFolderResponseLastModifiedBy"] = Field(
        alias="lastModifiedBy", default=None
    )
    last_modified_date_time: Optional[datetime.datetime] = Field(
        alias="lastModifiedDateTime", default=None
    )
    odata_context: Optional[str] = Field(alias="odataContext", default=None)
    parent_reference: Optional["CreateFolderResponseParentReference"] = Field(
        alias="parentReference", default=None
    )
    size: Optional[int] = Field(alias="size", default=None)
    web_url: Optional[str] = Field(alias="webUrl", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["CreateFolderResponse"], src_dict: Dict[str, Any]):
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
