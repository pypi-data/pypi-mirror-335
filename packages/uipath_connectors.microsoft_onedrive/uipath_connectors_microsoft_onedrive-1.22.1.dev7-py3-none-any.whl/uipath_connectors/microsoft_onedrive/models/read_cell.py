from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.read_cell_values_item import ReadCellValuesItem
from ..models.read_cell_text_item import ReadCellTextItem
from ..models.read_cell_formulas_item import ReadCellFormulasItem


class ReadCell(BaseModel):
    """
    Attributes:
        cell_value (Optional[str]): Value in cell
        formulas (Optional[list['ReadCellFormulasItem']]):
        text (Optional[list['ReadCellTextItem']]):
        values (Optional[list['ReadCellValuesItem']]):
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    cell_value: Optional[str] = Field(alias="CellValue", default=None)
    formulas: Optional[list["ReadCellFormulasItem"]] = Field(
        alias="formulas", default=None
    )
    text: Optional[list["ReadCellTextItem"]] = Field(alias="text", default=None)
    values: Optional[list["ReadCellValuesItem"]] = Field(alias="values", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["ReadCell"], src_dict: Dict[str, Any]):
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
