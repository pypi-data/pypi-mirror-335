from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type


class GetFileOrFolderResponsePermissionsArrayItemRef(BaseModel):
    """
    Attributes:
        deleted (Optional[bool]): Indicates if a permission has been deleted.
        display_name (Optional[str]): The name displayed for the user or group with permission. Example: Dev User1.
        email_address (Optional[str]): Shows the email address linked to the file permissions. Example: devuser1@uipath-
                dev.com.
        id (Optional[str]): Unique identifier for each permission on the file. Example: 03464898141015738316.
        kind (Optional[str]): Specifies the type of permission for the file. Example: drive#permission.
        pending_owner (Optional[bool]): Indicates if there is a pending owner for the file.
        photo_link (Optional[str]): URL to the user's profile photo associated with permissions. Example:
                https://lh3.googleusercontent.com/a/ACg8ocJA8OAiIs7P5QTkbRh8Kr3IaiAVH4Oc2TmLCaRg8w2gik8cTw=s64.
        role (Optional[str]): The role assigned to a user for the file. Example: owner.
        type_ (Optional[str]): Specifies the type of permission granted to the user. Example: user.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    deleted: Optional[bool] = Field(alias="deleted", default=None)
    display_name: Optional[str] = Field(alias="displayName", default=None)
    email_address: Optional[str] = Field(alias="emailAddress", default=None)
    id: Optional[str] = Field(alias="id", default=None)
    kind: Optional[str] = Field(alias="kind", default=None)
    pending_owner: Optional[bool] = Field(alias="pendingOwner", default=None)
    photo_link: Optional[str] = Field(alias="photoLink", default=None)
    role: Optional[str] = Field(alias="role", default=None)
    type_: Optional[str] = Field(alias="type", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(
        cls: Type["GetFileOrFolderResponsePermissionsArrayItemRef"],
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
