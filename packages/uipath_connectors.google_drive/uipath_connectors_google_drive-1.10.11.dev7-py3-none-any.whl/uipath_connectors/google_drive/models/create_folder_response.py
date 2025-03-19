from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type



class CreateFolderResponse(BaseModel):
    """
    Attributes:
        id (Optional[str]): A unique identifier assigned to the folder. Example: 1cTBAcWEXq-BvuoqWoIVC4rsNXwRxZ636.
        kind (Optional[str]): Indicates the type of resource being dealt with. Example: drive#file.
        mime_type (Optional[str]): Defines the MIME type of the folder, typically a fixed value. Example:
                application/vnd.google-apps.folder.
        name (Optional[str]): Specifies the name of the folder being created. Example: New Folder.
        parents (Optional[list[str]]):  Example: 1U-shNvcKVrJY3uHdw5rb1_5Nmar43qWM.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    id: Optional[str] = Field(alias="id", default=None)
    kind: Optional[str] = Field(alias="kind", default=None)
    mime_type: Optional[str] = Field(alias="mimeType", default=None)
    name: Optional[str] = Field(alias="name", default=None)
    parents: Optional[list[str]] = Field(alias="parents", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["CreateFolderResponse"], src_dict: Dict[str, Any]):
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
