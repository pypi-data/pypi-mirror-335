from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type


class GetDriveLabelsFieldsSelectionOptionsChoicesDisplayHintsBadgeColorsForegroundColor(
    BaseModel
):
    """
    Attributes:
        blue (Optional[float]): The Fields selection options choices display hints badge colors foreground color blue
                Example: 0.14117648.
        green (Optional[float]): The Fields selection options choices display hints badge colors foreground color green
                Example: 0.12941177.
        red (Optional[float]): The Fields selection options choices display hints badge colors foreground color red
                Example: 0.1254902.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    blue: Optional[float] = Field(alias="blue", default=None)
    green: Optional[float] = Field(alias="green", default=None)
    red: Optional[float] = Field(alias="red", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(
        cls: Type[
            "GetDriveLabelsFieldsSelectionOptionsChoicesDisplayHintsBadgeColorsForegroundColor"
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
