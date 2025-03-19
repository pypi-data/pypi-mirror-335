from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.add_sheet_response_replies_add_sheet_properties_grid_properties import (
    AddSheetResponseRepliesAddSheetPropertiesGridProperties,
)


class AddSheetResponseRepliesAddSheetProperties(BaseModel):
    """
    Attributes:
        grid_properties (Optional[AddSheetResponseRepliesAddSheetPropertiesGridProperties]):
        index (Optional[int]): The position of the sheet in the spreadsheet. Example: 1.0.
        sheet_id (Optional[int]): The unique identifier for the new sheet. Example: 1.496273301E9.
        sheet_type (Optional[str]): Specifies the type of sheet being added. Example: GRID.
        title (Optional[str]): The name given to the new sheet. Example: NewSheet.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    grid_properties: Optional[
        "AddSheetResponseRepliesAddSheetPropertiesGridProperties"
    ] = Field(alias="gridProperties", default=None)
    index: Optional[int] = Field(alias="index", default=None)
    sheet_id: Optional[int] = Field(alias="sheetId", default=None)
    sheet_type: Optional[str] = Field(alias="sheetType", default=None)
    title: Optional[str] = Field(alias="title", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(
        cls: Type["AddSheetResponseRepliesAddSheetProperties"], src_dict: Dict[str, Any]
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
