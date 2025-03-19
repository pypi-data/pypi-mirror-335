from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type


class GetFileOrFolderResponseImageMediaMetadata(BaseModel):
    """
    Attributes:
        height (Optional[int]): The height of the image in pixels. Example: 1374.0.
        rotation (Optional[int]): Specifies the rotation angle of the image in its metadata. Example: 0.0.
        width (Optional[int]): The width of the image in pixels. Example: 1204.0.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    height: Optional[int] = Field(alias="height", default=None)
    rotation: Optional[int] = Field(alias="rotation", default=None)
    width: Optional[int] = Field(alias="width", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(
        cls: Type["GetFileOrFolderResponseImageMediaMetadata"], src_dict: Dict[str, Any]
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
