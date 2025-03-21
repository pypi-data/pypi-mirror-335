from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.file_upload_v2_response_created_by import FileUploadV2ResponseCreatedBy
from ..models.file_upload_v2_response_file import FileUploadV2ResponseFile
from ..models.file_upload_v2_response_file_system_info import (
    FileUploadV2ResponseFileSystemInfo,
)
from ..models.file_upload_v2_response_last_modified_by import (
    FileUploadV2ResponseLastModifiedBy,
)
from ..models.file_upload_v2_response_parent_reference import (
    FileUploadV2ResponseParentReference,
)
from ..models.file_upload_v2_response_shared import FileUploadV2ResponseShared
import datetime


class FileUploadV2Response(BaseModel):
    """
    Attributes:
        c_tag (Optional[str]): The C tag Example: "c:{39551359-58F7-4B49-A1A6-EEC21254EABA},4".
        content_download_url (Optional[str]): File download url Example: https://uipathstaging.sharepoint.com/sites/MyTe
                st/_layouts/15/download.aspx?UniqueId=39551359-58f7-4b49-a1a6-
                eec21254eaba&Translate=false&tempauth=v1.eyJzaXRlaWQiOiI2YzIxMzRjMi1lM2U4LTQzOTctODVmMi01MTI3YzMzZWFmNTciLCJhcHB
                fZGlzcGxheW5hbWUiOiJVaVBhdGggZm9yIE9uZURyaXZlIGFuZCBTaGFyZVBvaW50IiwiYXBwaWQiOiIxZjVhZjMwNi1mNTUwLTQ0NWYtYTFmYS0
                5NDI3ZmY4OGIwNmUiLCJhdWQiOiIwMDAwMDAwMy0wMDAwLTBmZjEtY2UwMC0wMDAwMDAwMDAwMDAvdWlwYXRoc3RhZ2luZy5zaGFyZXBvaW50LmN
                vbUAzY2U0ZGQwMy1jNWIxLTQ3MWYtOTRiMC0yMTUxMjY5NTVmMTAiLCJleHAiOiIxNzQxMDAwNTU0In0.CgoKBHNuaWQSAjY0EgsIpr-VqM2R7T0
                QBRoNNjEuOTUuMTU4LjExNiosczZnckVlY1Q5aFc3Z1BzcVVVZHByQlkvMGo4K3JicHZkU1RSRXFIZE1YST0wiQE4AUIQoYba4gRwALDV8F8lZpT
                fakoQaGFzaGVkcHJvb2Z0b2tlbnIpMGguZnxtZW1iZXJzaGlwfDEwMDMyMDAzMjQyODBiMmVAbGl2ZS5jb216ATKCARIJA93kPLHFH0cRlLAhUSa
                VXxCiASZkZXZ1c2VyM0B1aXBhdGhzdGFnaW5nLm9ubWljcm9zb2Z0LmNvbaoBEDEwMDMyMDAzMjQyODBCMkWyAXxteWZpbGVzLnJlYWQgYWxsZml
                sZXMucmVhZCBteWZpbGVzLndyaXRlIGFsbGZpbGVzLndyaXRlIGdyb3VwLnJlYWQgZ3JvdXAud3JpdGUgYWxsc2l0ZXMucmVhZCBhbGxzaXRlcy5
                3cml0ZSBhbGxwcm9maWxlcy5yZWFkyAEB.VygVvWMtUZoHooCTiojCQD5i7joN0jVZ4yJTM2diB-0&ApiVersion=2.0.
        created_by (Optional[FileUploadV2ResponseCreatedBy]):
        created_date_time (Optional[datetime.datetime]): The Created date time Example: 2025-03-03T10:15:53Z.
        e_tag (Optional[str]): The E tag Example: "{39551359-58F7-4B49-A1A6-EEC21254EABA},4".
        file (Optional[FileUploadV2ResponseFile]):
        file_system_info (Optional[FileUploadV2ResponseFileSystemInfo]):
        id (Optional[str]): File ID Example: 012GK26CKZCNKTT52YJFF2DJXOYIJFJ2V2.
        last_modified_by (Optional[FileUploadV2ResponseLastModifiedBy]):
        last_modified_date_time (Optional[datetime.datetime]): The Last modified date time Example:
                2025-03-03T10:15:55Z.
        name (Optional[str]): The Name Example: Screenshot 2025-02-28 at 7.46.28 AM.png.
        odata_context (Optional[str]): The Odata context Example:
                https://uipathstaging.sharepoint.com/sites/MyTest/_api/v2.0/$metadata#items/$entity.
        parent_reference (Optional[FileUploadV2ResponseParentReference]):
        shared (Optional[FileUploadV2ResponseShared]):
        size (Optional[int]): The Size Example: 71163.0.
        web_url (Optional[str]): The Web url Example: https://uipathstaging.sharepoint.com/sites/MyTest/Shared%20Documen
                ts/Folder10/Screenshot%202025-02-28%20at%207.46.28%E2%80%AFAM.png.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    c_tag: Optional[str] = Field(alias="cTag", default=None)
    content_download_url: Optional[str] = Field(
        alias="contentDownloadUrl", default=None
    )
    created_by: Optional["FileUploadV2ResponseCreatedBy"] = Field(
        alias="createdBy", default=None
    )
    created_date_time: Optional[datetime.datetime] = Field(
        alias="createdDateTime", default=None
    )
    e_tag: Optional[str] = Field(alias="eTag", default=None)
    file: Optional["FileUploadV2ResponseFile"] = Field(alias="file", default=None)
    file_system_info: Optional["FileUploadV2ResponseFileSystemInfo"] = Field(
        alias="fileSystemInfo", default=None
    )
    id: Optional[str] = Field(alias="id", default=None)
    last_modified_by: Optional["FileUploadV2ResponseLastModifiedBy"] = Field(
        alias="lastModifiedBy", default=None
    )
    last_modified_date_time: Optional[datetime.datetime] = Field(
        alias="lastModifiedDateTime", default=None
    )
    name: Optional[str] = Field(alias="name", default=None)
    odata_context: Optional[str] = Field(alias="odataContext", default=None)
    parent_reference: Optional["FileUploadV2ResponseParentReference"] = Field(
        alias="parentReference", default=None
    )
    shared: Optional["FileUploadV2ResponseShared"] = Field(alias="shared", default=None)
    size: Optional[int] = Field(alias="size", default=None)
    web_url: Optional[str] = Field(alias="webUrl", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["FileUploadV2Response"], src_dict: Dict[str, Any]):
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
