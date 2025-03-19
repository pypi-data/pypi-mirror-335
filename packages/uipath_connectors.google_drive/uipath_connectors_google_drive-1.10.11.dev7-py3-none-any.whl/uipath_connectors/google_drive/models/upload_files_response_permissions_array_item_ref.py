from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

import datetime
from ..models.upload_files_response_permissions_permission_details_array_item_ref import (
    UploadFilesResponsePermissionsPermissionDetailsArrayItemRef,
)
from ..models.upload_files_response_permissions_team_drive_permission_details_array_item_ref import (
    UploadFilesResponsePermissionsTeamDrivePermissionDetailsArrayItemRef,
)


class UploadFilesResponsePermissionsArrayItemRef(BaseModel):
    """
    Attributes:
        allow_file_discovery (Optional[bool]):
        deleted (Optional[bool]):
        display_name (Optional[str]):
        domain (Optional[str]):
        email_address (Optional[str]):
        expiration_time (Optional[datetime.datetime]):
        id (Optional[str]):
        kind (Optional[str]):
        pending_owner (Optional[bool]):
        permission_details (Optional[list['UploadFilesResponsePermissionsPermissionDetailsArrayItemRef']]):
        photo_link (Optional[str]):
        role (Optional[str]):
        team_drive_permission_details
                (Optional[list['UploadFilesResponsePermissionsTeamDrivePermissionDetailsArrayItemRef']]):
        type_ (Optional[str]):
        view (Optional[str]):
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    allow_file_discovery: Optional[bool] = Field(
        alias="allowFileDiscovery", default=None
    )
    deleted: Optional[bool] = Field(alias="deleted", default=None)
    display_name: Optional[str] = Field(alias="displayName", default=None)
    domain: Optional[str] = Field(alias="domain", default=None)
    email_address: Optional[str] = Field(alias="emailAddress", default=None)
    expiration_time: Optional[datetime.datetime] = Field(
        alias="expirationTime", default=None
    )
    id: Optional[str] = Field(alias="id", default=None)
    kind: Optional[str] = Field(alias="kind", default=None)
    pending_owner: Optional[bool] = Field(alias="pendingOwner", default=None)
    permission_details: Optional[
        list["UploadFilesResponsePermissionsPermissionDetailsArrayItemRef"]
    ] = Field(alias="permissionDetails", default=None)
    photo_link: Optional[str] = Field(alias="photoLink", default=None)
    role: Optional[str] = Field(alias="role", default=None)
    team_drive_permission_details: Optional[
        list["UploadFilesResponsePermissionsTeamDrivePermissionDetailsArrayItemRef"]
    ] = Field(alias="teamDrivePermissionDetails", default=None)
    type_: Optional[str] = Field(alias="type", default=None)
    view: Optional[str] = Field(alias="view", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(
        cls: Type["UploadFilesResponsePermissionsArrayItemRef"],
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
