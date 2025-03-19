from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.read_range_texts_item import ReadRangeTextsItem
from ..models.read_range_values_item import ReadRangeValuesItem
from ..models.read_range_formulas_item import ReadRangeFormulasItem


class ReadRange(BaseModel):
    """
    Attributes:
        formulas (Optional[list['ReadRangeFormulasItem']]):
        texts (Optional[list['ReadRangeTextsItem']]):
        values (Optional[list['ReadRangeValuesItem']]):
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    formulas: Optional[list["ReadRangeFormulasItem"]] = Field(
        alias="formulas", default=None
    )
    texts: Optional[list["ReadRangeTextsItem"]] = Field(alias="texts", default=None)
    values: Optional[list["ReadRangeValuesItem"]] = Field(alias="values", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["ReadRange"], src_dict: Dict[str, Any]):
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
