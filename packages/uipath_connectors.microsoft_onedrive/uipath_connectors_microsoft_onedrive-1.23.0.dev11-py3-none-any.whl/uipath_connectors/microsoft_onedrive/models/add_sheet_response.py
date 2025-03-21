from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type



class AddSheetResponse(BaseModel):
    """
    Attributes:
        id (Optional[str]): Unique identifier for the sheet. Example: {EC461D76-E8D0-4A39-BE55-646762AA5F0B}.
        position (Optional[int]): Indicates the index where the new sheet is added. Example: 10.0.
        visibility (Optional[str]): Indicates whether the sheet is visible or hidden. Example: Visible.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    id: Optional[str] = Field(alias="id", default=None)
    position: Optional[int] = Field(alias="position", default=None)
    visibility: Optional[str] = Field(alias="visibility", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["AddSheetResponse"], src_dict: Dict[str, Any]):
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
