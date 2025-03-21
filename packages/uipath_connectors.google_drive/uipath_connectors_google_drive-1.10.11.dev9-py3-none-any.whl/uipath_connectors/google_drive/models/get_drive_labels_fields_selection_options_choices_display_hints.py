from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.get_drive_labels_fields_selection_options_choices_display_hints_badge_colors import (
    GetDriveLabelsFieldsSelectionOptionsChoicesDisplayHintsBadgeColors,
)
from ..models.get_drive_labels_fields_selection_options_choices_display_hints_dark_badge_colors import (
    GetDriveLabelsFieldsSelectionOptionsChoicesDisplayHintsDarkBadgeColors,
)


class GetDriveLabelsFieldsSelectionOptionsChoicesDisplayHints(BaseModel):
    """
    Attributes:
        badge_colors (Optional[GetDriveLabelsFieldsSelectionOptionsChoicesDisplayHintsBadgeColors]):
        badge_priority (Optional[str]): The Fields selection options choices display hints badge priority Example:
                16867352630000.
        dark_badge_colors (Optional[GetDriveLabelsFieldsSelectionOptionsChoicesDisplayHintsDarkBadgeColors]):
        shown_in_apply (Optional[bool]): The Fields selection options choices display hints shown in apply Example:
                True.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    badge_colors: Optional[
        "GetDriveLabelsFieldsSelectionOptionsChoicesDisplayHintsBadgeColors"
    ] = Field(alias="badgeColors", default=None)
    badge_priority: Optional[str] = Field(alias="badgePriority", default=None)
    dark_badge_colors: Optional[
        "GetDriveLabelsFieldsSelectionOptionsChoicesDisplayHintsDarkBadgeColors"
    ] = Field(alias="darkBadgeColors", default=None)
    shown_in_apply: Optional[bool] = Field(alias="shownInApply", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(
        cls: Type["GetDriveLabelsFieldsSelectionOptionsChoicesDisplayHints"],
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
