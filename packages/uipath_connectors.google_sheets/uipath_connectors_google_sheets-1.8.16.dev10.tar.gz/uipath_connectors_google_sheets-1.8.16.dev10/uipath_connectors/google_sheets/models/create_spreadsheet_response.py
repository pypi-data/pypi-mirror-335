from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.create_spreadsheet_response_properties import (
    CreateSpreadsheetResponseProperties,
)
from ..models.create_spreadsheet_response_sheets_array_item_ref import (
    CreateSpreadsheetResponseSheetsArrayItemRef,
)


class CreateSpreadsheetResponse(BaseModel):
    """
    Attributes:
        properties (Optional[CreateSpreadsheetResponseProperties]):
        sheets (Optional[list['CreateSpreadsheetResponseSheetsArrayItemRef']]):
        spreadsheet_id (Optional[str]): Unique identifier for the entire spreadsheet document. Example:
                1BbSFfnoCdocT51sjz49Bdy9l8pzLdpU-UcCHZ1VPSQ0.
        spreadsheet_url (Optional[str]): The web address to access the spreadsheet. Example:
                https://docs.google.com/spreadsheets/d/1BbSFfnoCdocT51sjz49Bdy9l8pzLdpU-UcCHZ1VPSQ0/edit.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    properties: Optional["CreateSpreadsheetResponseProperties"] = Field(
        alias="properties", default=None
    )
    sheets: Optional[list["CreateSpreadsheetResponseSheetsArrayItemRef"]] = Field(
        alias="sheets", default=None
    )
    spreadsheet_id: Optional[str] = Field(alias="spreadsheetId", default=None)
    spreadsheet_url: Optional[str] = Field(alias="spreadsheetUrl", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["CreateSpreadsheetResponse"], src_dict: Dict[str, Any]):
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
