from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.create_share_link_request_scope import CreateShareLinkRequestScope
from ..models.create_share_link_request_type import CreateShareLinkRequestType


class CreateShareLinkRequest(BaseModel):
    """
    Attributes:
        expiration_date_time (Optional[str]):  Example: string.
        file_folder_id (Optional[str]):  Example: string.
        password (Optional[str]):  Example: string.
        scope (Optional[CreateShareLinkRequestScope]):  Example: string.
        type_ (Optional[CreateShareLinkRequestType]):  Example: string.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    expiration_date_time: Optional[str] = Field(
        alias="expirationDateTime", default=None
    )
    file_folder_id: Optional[str] = Field(alias="fileFolderId", default=None)
    password: Optional[str] = Field(alias="password", default=None)
    scope: Optional["CreateShareLinkRequestScope"] = Field(alias="scope", default=None)
    type_: Optional["CreateShareLinkRequestType"] = Field(alias="type", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["CreateShareLinkRequest"], src_dict: Dict[str, Any]):
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
