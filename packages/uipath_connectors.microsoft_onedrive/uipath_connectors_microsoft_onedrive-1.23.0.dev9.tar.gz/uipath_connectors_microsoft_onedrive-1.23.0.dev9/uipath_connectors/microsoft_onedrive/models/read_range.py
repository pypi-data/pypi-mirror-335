from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.read_range_formulas_array_item_ref import ReadRangeFormulasArrayItemRef
from ..models.read_range_texts_array_item_ref import ReadRangeTextsArrayItemRef
from ..models.read_range_values_array_item_ref import ReadRangeValuesArrayItemRef


class ReadRange(BaseModel):
    """
    Attributes:
        formulas (Optional[list['ReadRangeFormulasArrayItemRef']]):
        texts (Optional[list['ReadRangeTextsArrayItemRef']]):
        values (Optional[list['ReadRangeValuesArrayItemRef']]):
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    formulas: Optional[list["ReadRangeFormulasArrayItemRef"]] = Field(
        alias="formulas", default=None
    )
    texts: Optional[list["ReadRangeTextsArrayItemRef"]] = Field(
        alias="texts", default=None
    )
    values: Optional[list["ReadRangeValuesArrayItemRef"]] = Field(
        alias="values", default=None
    )

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
