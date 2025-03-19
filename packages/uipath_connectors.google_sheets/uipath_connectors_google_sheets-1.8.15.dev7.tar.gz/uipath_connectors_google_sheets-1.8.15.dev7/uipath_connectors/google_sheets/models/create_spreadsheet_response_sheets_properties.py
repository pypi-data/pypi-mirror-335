from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.create_spreadsheet_response_sheets_properties_grid_properties import (
    CreateSpreadsheetResponseSheetsPropertiesGridProperties,
)


class CreateSpreadsheetResponseSheetsProperties(BaseModel):
    """
    Attributes:
        grid_properties (Optional[CreateSpreadsheetResponseSheetsPropertiesGridProperties]):
        index (Optional[int]): The position of the sheet within the spreadsheet. Example: 0.0.
        sheet_id (Optional[int]): Unique identifier for each sheet in the spreadsheet. Example: 9.53933607E8.
        sheet_type (Optional[str]): Identifies the type of sheet, such as grid or chart. Example: GRID.
        title (Optional[str]): The name of the sheet as displayed in the spreadsheet. Example: Sheet name 1.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    grid_properties: Optional[
        "CreateSpreadsheetResponseSheetsPropertiesGridProperties"
    ] = Field(alias="gridProperties", default=None)
    index: Optional[int] = Field(alias="index", default=None)
    sheet_id: Optional[int] = Field(alias="sheetId", default=None)
    sheet_type: Optional[str] = Field(alias="sheetType", default=None)
    title: Optional[str] = Field(alias="title", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(
        cls: Type["CreateSpreadsheetResponseSheetsProperties"], src_dict: Dict[str, Any]
    ):
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
