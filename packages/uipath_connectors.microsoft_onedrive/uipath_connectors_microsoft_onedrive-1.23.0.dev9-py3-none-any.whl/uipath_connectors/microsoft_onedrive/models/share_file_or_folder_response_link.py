from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type



class ShareFileOrFolderResponseLink(BaseModel):
    """
    Attributes:
        prevents_download (Optional[bool]): Indicates if downloading the shared file or folder is restricted.
        scope (Optional[str]): Defines the access level of the shared link. Example: organization.
        type_ (Optional[str]): Indicates whether the link is view-only or allows editing. Example: view.
        web_url (Optional[str]): The web address that provides access to the shared file or folder. Example:
                https://uipathstaging-my.sharepoint.com/:i:/g/personal/devuser3_uipathstaging_onmicrosoft_com/EdX9ga2hRIVFq0cX4S
                3GZMIB5s1WyNc9tyvsMy8fxQ7cTQ.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    prevents_download: Optional[bool] = Field(alias="preventsDownload", default=None)
    scope: Optional[str] = Field(alias="scope", default=None)
    type_: Optional[str] = Field(alias="type", default=None)
    web_url: Optional[str] = Field(alias="webUrl", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["ShareFileOrFolderResponseLink"], src_dict: Dict[str, Any]):
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
