from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.get_files_folders_list_owner import GetFilesFoldersListOwner


class GetFilesFoldersList(BaseModel):
    """
    Attributes:
        extension (Optional[str]): The file extension indicates the file type. Example: png.
        full_name (Optional[str]): The complete name of the file or folder including its path. Example: Fiddler2.
        id (Optional[str]): A unique identifier assigned to the file or folder. Example:
                01BX6K4RQOZ3FW3GQ3JZGZ4PKFQRFUG2ID.
        mime_type (Optional[str]): The MIME type describes the file's format. Example: image/png.
        owner (Optional[GetFilesFoldersListOwner]):
        parent_drive_id (Optional[str]): Unique identifier for the parent drive. Example:
                b!DVFqQPEoG0yShqSXvePVy2f9AJ5eEYFJrMwJAEdWoj912uw8AfAWTonhZgO36N2G.
        parent_id (Optional[str]): Unique identifier for the parent folder. Example: 01BX6K4RWWE6YSKAUJKRFYBT3SKHFJ65TT.
        reference_id (Optional[str]): A unique identifier for the file or folder. Example:
                b!DVFqQPEoG0yShqSXvePVy2f9AJ5eEYFJrMwJAEdWoj912uw8AfAWTonhZgO36N2G - 01BX6K4RQOZ3FW3GQ3JZGZ4PKFQRFUG2ID.
        type_ (Optional[str]): Specifies whether the item is a file or folder. Example: folder.
        url (Optional[str]): Web address to access the file or folder. Example: https://uipathstaging-
                my.sharepoint.com/personal/devuser3_uipathstaging_onmicrosoft_com/Documents/207/Fiddler2.
        is_folder (Optional[bool]): Indicates if the item is a folder. Example: True.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    extension: Optional[str] = Field(alias="Extension", default=None)
    full_name: Optional[str] = Field(alias="FullName", default=None)
    id: Optional[str] = Field(alias="ID", default=None)
    mime_type: Optional[str] = Field(alias="MIMEType", default=None)
    owner: Optional["GetFilesFoldersListOwner"] = Field(alias="Owner", default=None)
    parent_drive_id: Optional[str] = Field(alias="ParentDriveID", default=None)
    parent_id: Optional[str] = Field(alias="ParentID", default=None)
    reference_id: Optional[str] = Field(alias="ReferenceID", default=None)
    type_: Optional[str] = Field(alias="Type", default=None)
    url: Optional[str] = Field(alias="URL", default=None)
    is_folder: Optional[bool] = Field(alias="isFolder", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["GetFilesFoldersList"], src_dict: Dict[str, Any]):
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
