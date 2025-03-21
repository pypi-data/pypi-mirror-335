from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.curated_file_and_folder_owner import CuratedFileAndFolderOwner
from ..models.curated_file_and_folder_type import CuratedFileAndFolderType


class CuratedFileAndFolder(BaseModel):
    """
    Attributes:
        extension (Optional[str]):  Example: docx.
        full_name (Optional[str]):  Example: Document.docx.
        id (Optional[str]):  Example: 01EPMICMOI6MDHDWBT4ZHJYPXPKRC7WQB7.
        mime_type (Optional[str]):  Example: application/vnd.openxmlformats-officedocument.wordprocessingml.document.
        owner (Optional[CuratedFileAndFolderOwner]):
        parent_drive_id (Optional[str]):  Example: b!_YnPyCC75kOq5OtXNRC1rpGAGXeO4CVNqawKnDOE1YXYbbrpZxdyRZtp0X--PJd5.
        parent_id (Optional[str]):  Example: 01EPMICMN6Y2GOVW7725BZO354PWSELRRZ.
        reference_id (Optional[str]):  Example: True.
        type_ (Optional[CuratedFileAndFolderType]):  Example: folder.
        url (Optional[str]):  Example: https://uipath-
                my.sharepoint.com/personal/mohit_achary_uipath_com/Documents/Desktop.
        is_folder (Optional[bool]):  Example: True.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    extension: Optional[str] = Field(alias="Extension", default=None)
    full_name: Optional[str] = Field(alias="FullName", default=None)
    id: Optional[str] = Field(alias="ID", default=None)
    mime_type: Optional[str] = Field(alias="MIMEType", default=None)
    owner: Optional["CuratedFileAndFolderOwner"] = Field(alias="Owner", default=None)
    parent_drive_id: Optional[str] = Field(alias="ParentDriveID", default=None)
    parent_id: Optional[str] = Field(alias="ParentID", default=None)
    reference_id: Optional[str] = Field(alias="ReferenceID", default=None)
    type_: Optional["CuratedFileAndFolderType"] = Field(alias="Type", default=None)
    url: Optional[str] = Field(alias="URL", default=None)
    is_folder: Optional[bool] = Field(alias="isFolder", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["CuratedFileAndFolder"], src_dict: Dict[str, Any]):
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
