from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.create_share_link_response_link_application import (
    CreateShareLinkResponseLinkApplication,
)


class CreateShareLinkResponseLink(BaseModel):
    """
    Attributes:
        application (Optional[CreateShareLinkResponseLinkApplication]):
        scope (Optional[str]):  Example: anonymous.
        type_ (Optional[str]):  Example: view.
        web_url (Optional[str]):  Example: https://1drv.ms/A6913278E564460AA616C71B28AD6EB6.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    application: Optional["CreateShareLinkResponseLinkApplication"] = Field(
        alias="application", default=None
    )
    scope: Optional[str] = Field(alias="scope", default=None)
    type_: Optional[str] = Field(alias="type", default=None)
    web_url: Optional[str] = Field(alias="webUrl", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["CreateShareLinkResponseLink"], src_dict: Dict[str, Any]):
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
