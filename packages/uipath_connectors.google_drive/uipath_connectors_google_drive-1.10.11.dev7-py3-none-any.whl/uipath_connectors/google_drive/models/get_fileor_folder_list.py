from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type


class GetFileorFolderList(BaseModel):
    """
    Attributes:
        id (Optional[str]): A unique identifier for the file or folder. Example: 1TGivbyQI11MniZt2pQG_ufmxCDmzkHY7.
        kind (Optional[str]): The type of resource, such as a file or folder. Example: drive#file.
        mime_type (Optional[str]): The MIME type of the file, indicating its format. Example: application/pdf.
        name (Optional[str]): The name of the file or folder. Example: harish.pdf.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    id: Optional[str] = Field(alias="id", default=None)
    kind: Optional[str] = Field(alias="kind", default=None)
    mime_type: Optional[str] = Field(alias="mimeType", default=None)
    name: Optional[str] = Field(alias="name", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["GetFileorFolderList"], src_dict: Dict[str, Any]):
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
