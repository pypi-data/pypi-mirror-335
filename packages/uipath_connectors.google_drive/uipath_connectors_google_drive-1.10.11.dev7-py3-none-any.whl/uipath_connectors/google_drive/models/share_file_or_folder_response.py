from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.share_file_or_folder_response_permission import (
    ShareFileOrFolderResponsePermission,
)
from ..models.share_file_or_folder_response_share_with import (
    ShareFileOrFolderResponseShareWith,
)


class ShareFileOrFolderResponse(BaseModel):
    """
    Attributes:
        id (Optional[str]): The unique identifier for the file or folder being shared. Example: 08297724243212991059.
        kind (Optional[str]): The type of resource, typically a fixed string indicating the API. Example:
                drive#permission.
        role (Optional[ShareFileOrFolderResponsePermission]): The type of entity receiving the permission, such as user
                or group. Example: reader.
        type_ (Optional[ShareFileOrFolderResponseShareWith]): The level of access granted to the user or group. Example:
                user.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    id: Optional[str] = Field(alias="id", default=None)
    kind: Optional[str] = Field(alias="kind", default=None)
    role: Optional[ShareFileOrFolderResponsePermission] = Field(
        alias="role", default=None
    )
    type_: Optional[ShareFileOrFolderResponseShareWith] = Field(
        alias="type", default=None
    )

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["ShareFileOrFolderResponse"], src_dict: Dict[str, Any]):
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
