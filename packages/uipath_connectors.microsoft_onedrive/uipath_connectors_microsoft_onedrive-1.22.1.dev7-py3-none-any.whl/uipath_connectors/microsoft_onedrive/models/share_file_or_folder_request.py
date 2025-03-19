from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.share_file_or_folder_request_permission import (
    ShareFileOrFolderRequestPermission,
)
from ..models.share_file_or_folder_request_share_with import (
    ShareFileOrFolderRequestShareWith,
)
import datetime


class ShareFileOrFolderRequest(BaseModel):
    """
    Attributes:
        scope (ShareFileOrFolderRequestShareWith): Defines the access level or audience for the shared link. Example:
                anonymous.
        type_ (ShareFileOrFolderRequestPermission): Specifies the type of sharing action performed. Example: view.
        expiration_date_time (Optional[datetime.datetime]): The date and time when the shared link will expire. Example:
                2025-02-11T11:11:11.0000000+00:00.
        password (Optional[str]): The password required to access the shared file or folder. Example:
                ThisIsMyPrivatePassword.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    scope: ShareFileOrFolderRequestShareWith = Field(alias="scope")
    type_: ShareFileOrFolderRequestPermission = Field(alias="type")
    expiration_date_time: Optional[datetime.datetime] = Field(
        alias="expirationDateTime", default=None
    )
    password: Optional[str] = Field(alias="password", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["ShareFileOrFolderRequest"], src_dict: Dict[str, Any]):
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
