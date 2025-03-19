from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.get_drive_labels_fields_selection_options_choices_properties import (
    GetDriveLabelsFieldsSelectionOptionsChoicesProperties,
)
from ..models.get_drive_labels_fields_selection_options_choices_applied_capabilities import (
    GetDriveLabelsFieldsSelectionOptionsChoicesAppliedCapabilities,
)
from ..models.get_drive_labels_fields_selection_options_choices_display_hints import (
    GetDriveLabelsFieldsSelectionOptionsChoicesDisplayHints,
)
from ..models.get_drive_labels_fields_selection_options_choices_lifecycle import (
    GetDriveLabelsFieldsSelectionOptionsChoicesLifecycle,
)


class GetDriveLabelsFieldsSelectionOptionsChoicesArrayItemRef(BaseModel):
    """
    Attributes:
        applied_capabilities (Optional[GetDriveLabelsFieldsSelectionOptionsChoicesAppliedCapabilities]):
        display_hints (Optional[GetDriveLabelsFieldsSelectionOptionsChoicesDisplayHints]):
        id (Optional[str]): The Fields selection options choices ID Example: E381451061.
        lifecycle (Optional[GetDriveLabelsFieldsSelectionOptionsChoicesLifecycle]):
        properties (Optional[GetDriveLabelsFieldsSelectionOptionsChoicesProperties]):
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    applied_capabilities: Optional[
        "GetDriveLabelsFieldsSelectionOptionsChoicesAppliedCapabilities"
    ] = Field(alias="appliedCapabilities", default=None)
    display_hints: Optional[
        "GetDriveLabelsFieldsSelectionOptionsChoicesDisplayHints"
    ] = Field(alias="displayHints", default=None)
    id: Optional[str] = Field(alias="id", default=None)
    lifecycle: Optional["GetDriveLabelsFieldsSelectionOptionsChoicesLifecycle"] = Field(
        alias="lifecycle", default=None
    )
    properties: Optional["GetDriveLabelsFieldsSelectionOptionsChoicesProperties"] = (
        Field(alias="properties", default=None)
    )

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(
        cls: Type["GetDriveLabelsFieldsSelectionOptionsChoicesArrayItemRef"],
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
