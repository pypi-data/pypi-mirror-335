from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type


class CreateSpreadsheetResponsePropertiesDefaultFormatTextFormat(BaseModel):
    """
    Attributes:
        bold (Optional[bool]): Indicates if the default text format is bold in the spreadsheet.
        font_family (Optional[str]): Specifies the default font family for text in the sheet. Example: arial,sans,sans-
                serif.
        font_size (Optional[int]): Specifies the default font size for text in the spreadsheet. Example: 10.0.
        italic (Optional[bool]): Indicates if the default text format is italicized.
        strikethrough (Optional[bool]): Indicates if text is strikethrough by default in the spreadsheet.
        underline (Optional[bool]): Indicates if text is underlined by default in the sheet.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    bold: Optional[bool] = Field(alias="bold", default=None)
    font_family: Optional[str] = Field(alias="fontFamily", default=None)
    font_size: Optional[int] = Field(alias="fontSize", default=None)
    italic: Optional[bool] = Field(alias="italic", default=None)
    strikethrough: Optional[bool] = Field(alias="strikethrough", default=None)
    underline: Optional[bool] = Field(alias="underline", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(
        cls: Type["CreateSpreadsheetResponsePropertiesDefaultFormatTextFormat"],
        src_dict: Dict[str, Any],
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
