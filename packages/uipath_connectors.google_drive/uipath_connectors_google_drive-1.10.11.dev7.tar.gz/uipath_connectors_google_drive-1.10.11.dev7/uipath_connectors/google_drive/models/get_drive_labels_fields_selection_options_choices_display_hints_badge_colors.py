from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.get_drive_labels_fields_selection_options_choices_display_hints_badge_colors_background_color import (
    GetDriveLabelsFieldsSelectionOptionsChoicesDisplayHintsBadgeColorsBackgroundColor,
)
from ..models.get_drive_labels_fields_selection_options_choices_display_hints_badge_colors_solo_color import (
    GetDriveLabelsFieldsSelectionOptionsChoicesDisplayHintsBadgeColorsSoloColor,
)
from ..models.get_drive_labels_fields_selection_options_choices_display_hints_badge_colors_foreground_color import (
    GetDriveLabelsFieldsSelectionOptionsChoicesDisplayHintsBadgeColorsForegroundColor,
)


class GetDriveLabelsFieldsSelectionOptionsChoicesDisplayHintsBadgeColors(BaseModel):
    """
    Attributes:
        background_color (Optional[GetDriveLabelsFieldsSelectionOptionsChoicesDisplayHintsBadgeColorsBackgroundColor]):
        foreground_color (Optional[GetDriveLabelsFieldsSelectionOptionsChoicesDisplayHintsBadgeColorsForegroundColor]):
        solo_color (Optional[GetDriveLabelsFieldsSelectionOptionsChoicesDisplayHintsBadgeColorsSoloColor]):
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    background_color: Optional[
        "GetDriveLabelsFieldsSelectionOptionsChoicesDisplayHintsBadgeColorsBackgroundColor"
    ] = Field(alias="backgroundColor", default=None)
    foreground_color: Optional[
        "GetDriveLabelsFieldsSelectionOptionsChoicesDisplayHintsBadgeColorsForegroundColor"
    ] = Field(alias="foregroundColor", default=None)
    solo_color: Optional[
        "GetDriveLabelsFieldsSelectionOptionsChoicesDisplayHintsBadgeColorsSoloColor"
    ] = Field(alias="soloColor", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(
        cls: Type["GetDriveLabelsFieldsSelectionOptionsChoicesDisplayHintsBadgeColors"],
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
