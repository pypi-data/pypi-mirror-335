from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.share_file_or_folder_response_link import ShareFileOrFolderResponseLink
from ..models.share_file_or_folder_response_scope import ShareFileOrFolderResponseScope
from ..models.share_file_or_folder_response_type import ShareFileOrFolderResponseType
import datetime


class ShareFileOrFolderResponse(BaseModel):
    """
    Attributes:
        scope (ShareFileOrFolderResponseScope): Defines the access level or audience for the shared link. Example:
                anonymous.
        type_ (ShareFileOrFolderResponseType): Specifies the type of sharing action performed. Example: view.
        expiration_date_time (Optional[datetime.datetime]): The date and time when the shared link will expire. Example:
                2025-02-11T11:11:11Z.
        has_password (Optional[bool]): Indicates if the file or folder is password protected.
        id (Optional[str]): Unique identifier for the item being shared. Example: c86378b2-98df-4198-8093-6fadda09ea27.
        link (Optional[ShareFileOrFolderResponseLink]):
        password (Optional[str]): The password required to access the shared file or folder. Example:
                ThisIsMyPrivatePassword.
        roles (Optional[list[str]]):
        share_id (Optional[str]): Unique identifier for the shared file or folder. Example: u!aHR0cHM6Ly91aXBhdGhzdGFnaW
                5nLW15LnNoYXJlcG9pbnQuY29tLzppOi9nL3BlcnNvbmFsL2RldnVzZXIzX3VpcGF0aHN0YWdpbmdfb25taWNyb3NvZnRfY29tL0VkWDlnYTJoUk
                lWRnEwY1g0UzNHWk1JQjVzMVd5TmM5dHl2c015OGZ4UTdjVFE.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    scope: "ShareFileOrFolderResponseScope" = Field(alias="scope")
    type_: "ShareFileOrFolderResponseType" = Field(alias="type")
    expiration_date_time: Optional[datetime.datetime] = Field(
        alias="expirationDateTime", default=None
    )
    has_password: Optional[bool] = Field(alias="hasPassword", default=None)
    id: Optional[str] = Field(alias="id", default=None)
    link: Optional["ShareFileOrFolderResponseLink"] = Field(alias="link", default=None)
    password: Optional[str] = Field(alias="password", default=None)
    roles: Optional[list[str]] = Field(alias="roles", default=None)
    share_id: Optional[str] = Field(alias="shareId", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["ShareFileOrFolderResponse"], src_dict: Dict[str, Any]):
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
