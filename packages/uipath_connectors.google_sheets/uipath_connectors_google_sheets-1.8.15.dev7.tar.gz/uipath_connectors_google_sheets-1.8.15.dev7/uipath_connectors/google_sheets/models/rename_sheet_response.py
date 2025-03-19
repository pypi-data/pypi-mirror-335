from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type


class RenameSheetResponse(BaseModel):
    """
    Attributes:
        spreadsheet_id (Optional[str]): Unique identifier for the spreadsheet. Example:
                1OCj9pL5oLAVoBBO45q-GQlZW_NN9xXRCKraKM9F1J2U.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    spreadsheet_id: Optional[str] = Field(alias="spreadsheetId", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["RenameSheetResponse"], src_dict: Dict[str, Any]):
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
