from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.share_file_or_folder_request_permission import (
    ShareFileOrFolderRequestPermission,
)
from ..models.share_file_or_folder_request_share_with import (
    ShareFileOrFolderRequestShareWith,
)


class ShareFileOrFolderRequest(BaseModel):
    """
    Attributes:
        email_address (Optional[str]): The email address of the user or group being shared with. Example:
                harishlpu123@gmail.com.
        role (Optional[ShareFileOrFolderRequestPermission]): The type of entity receiving the permission, such as user
                or group. Example: reader.
        type_ (Optional[ShareFileOrFolderRequestShareWith]): The level of access granted to the user or group. Example:
                user.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    email_address: Optional[str] = Field(alias="emailAddress", default=None)
    role: Optional[ShareFileOrFolderRequestPermission] = Field(
        alias="role", default=None
    )
    type_: Optional[ShareFileOrFolderRequestShareWith] = Field(
        alias="type", default=None
    )

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["ShareFileOrFolderRequest"], src_dict: Dict[str, Any]):
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
