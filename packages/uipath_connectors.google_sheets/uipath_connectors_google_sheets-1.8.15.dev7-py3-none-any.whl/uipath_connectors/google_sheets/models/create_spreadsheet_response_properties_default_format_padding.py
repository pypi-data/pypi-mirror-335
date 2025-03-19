from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type


class CreateSpreadsheetResponsePropertiesDefaultFormatPadding(BaseModel):
    """
    Attributes:
        bottom (Optional[int]): The default bottom padding for cells in the spreadsheet. Example: 2.0.
        left (Optional[int]): The default left padding for cell content. Example: 3.0.
        right (Optional[int]): The default right padding for cells in the sheet. Example: 3.0.
        top (Optional[int]): The default top padding for cells in the spreadsheet. Example: 2.0.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    bottom: Optional[int] = Field(alias="bottom", default=None)
    left: Optional[int] = Field(alias="left", default=None)
    right: Optional[int] = Field(alias="right", default=None)
    top: Optional[int] = Field(alias="top", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(
        cls: Type["CreateSpreadsheetResponsePropertiesDefaultFormatPadding"],
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
