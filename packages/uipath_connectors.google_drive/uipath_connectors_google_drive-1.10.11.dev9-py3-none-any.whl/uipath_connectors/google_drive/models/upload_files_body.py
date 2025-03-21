from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Type

from ..types import File


class UploadFilesBody(BaseModel):
    """
    Attributes:
        media (File): The file's data to the media part.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    media: File = Field(alias="Media")

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["UploadFilesBody"], src_dict: Dict[str, Any]):
        return cls.model_validate(src_dict)

    def to_multipart(self) -> dict[str, Any]:
        media = self.media.to_tuple()

        field_dict: dict[str, Any] = {}
        for prop_name, prop in self.additional_keys:
            field_dict[prop_name] = (
                None,
                str(self.__getitem__(prop)).encode(),
                "text/plain",
            )
        field_dict.update(
            {
                "Media": media,
            }
        )

        return field_dict

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
