from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.create_spreadsheet_response_properties_spreadsheet_theme import (
    CreateSpreadsheetResponsePropertiesSpreadsheetTheme,
)
from ..models.create_spreadsheet_response_properties_default_format import (
    CreateSpreadsheetResponsePropertiesDefaultFormat,
)


class CreateSpreadsheetResponseProperties(BaseModel):
    """
    Attributes:
        auto_recalc (Optional[str]): Determines how often the spreadsheet recalculates formulas. Example: ON_CHANGE.
        default_format (Optional[CreateSpreadsheetResponsePropertiesDefaultFormat]):
        locale (Optional[str]): The regional settings for the spreadsheet, affecting formats. Example: en_US.
        spreadsheet_theme (Optional[CreateSpreadsheetResponsePropertiesSpreadsheetTheme]):
        time_zone (Optional[str]): Sets the time zone for the spreadsheet's date and time functions. Example: Etc/GMT.
        title (Optional[str]): The title of the spreadsheet. Example: New spread sheet at 5pm.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    auto_recalc: Optional[str] = Field(alias="autoRecalc", default=None)
    default_format: Optional["CreateSpreadsheetResponsePropertiesDefaultFormat"] = (
        Field(alias="defaultFormat", default=None)
    )
    locale: Optional[str] = Field(alias="locale", default=None)
    spreadsheet_theme: Optional[
        "CreateSpreadsheetResponsePropertiesSpreadsheetTheme"
    ] = Field(alias="spreadsheetTheme", default=None)
    time_zone: Optional[str] = Field(alias="timeZone", default=None)
    title: Optional[str] = Field(alias="title", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(
        cls: Type["CreateSpreadsheetResponseProperties"], src_dict: Dict[str, Any]
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
