from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.get_drive_labels_fields_selection_options_choices_properties_badge_config import (
    GetDriveLabelsFieldsSelectionOptionsChoicesPropertiesBadgeConfig,
)


class GetDriveLabelsFieldsSelectionOptionsChoicesProperties(BaseModel):
    """
    Attributes:
        badge_config (Optional[GetDriveLabelsFieldsSelectionOptionsChoicesPropertiesBadgeConfig]):
        description (Optional[str]): The Fields selection options choices properties description Example: Option 1
                Description.
        display_name (Optional[str]): The Fields selection options choices properties display name Example: Option 1.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    badge_config: Optional[
        "GetDriveLabelsFieldsSelectionOptionsChoicesPropertiesBadgeConfig"
    ] = Field(alias="badgeConfig", default=None)
    description: Optional[str] = Field(alias="description", default=None)
    display_name: Optional[str] = Field(alias="displayName", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(
        cls: Type["GetDriveLabelsFieldsSelectionOptionsChoicesProperties"],
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
