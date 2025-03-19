from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type


class CreateSpreadsheetResponsePropertiesDefaultFormatBackgroundColorStyleRgbColor(
    BaseModel
):
    """
    Attributes:
        blue (Optional[int]): Specifies the blue component of the default background style color. Example: 1.0.
        green (Optional[int]): Specifies the green component of the default background style color. Example: 1.0.
        red (Optional[int]): The red component of the default background color. Example: 1.0.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    blue: Optional[int] = Field(alias="blue", default=None)
    green: Optional[int] = Field(alias="green", default=None)
    red: Optional[int] = Field(alias="red", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(
        cls: Type[
            "CreateSpreadsheetResponsePropertiesDefaultFormatBackgroundColorStyleRgbColor"
        ],
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
