from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type


class GetFileOrFolderResponseCapabilities(BaseModel):
    """
    Attributes:
        can_accept_ownership (Optional[bool]): Indicates if the user can accept ownership of the file.
        can_add_children (Optional[bool]): Specifies if the user can add child files or folders.
        can_add_my_drive_parent (Optional[bool]): Indicates if the file can be added to My Drive.
        can_change_copy_requires_writer_permission (Optional[bool]): Indicates if the copy requires writer permission
                can be changed. Example: True.
        can_change_security_update_enabled (Optional[bool]): Indicates if you can change the security update settings.
        can_change_viewers_can_copy_content (Optional[bool]): Indicates if the user can change the permission for
                viewers to copy content. Example: True.
        can_comment (Optional[bool]): Indicates if comments can be added to the file. Example: True.
        can_copy (Optional[bool]): Indicates if the file can be copied by the user. Example: True.
        can_delete (Optional[bool]): Indicates if the file can be deleted. Example: True.
        can_disable_inherited_permissions (Optional[bool]): Indicates if inherited permissions can be disabled for the
                file.
        can_download (Optional[bool]): Indicates if the file can be downloaded by the user. Example: True.
        can_edit (Optional[bool]): Indicates if the file can be edited by the user. Example: True.
        can_enable_inherited_permissions (Optional[bool]): Indicates if inherited permissions can be enabled. Example:
                True.
        can_list_children (Optional[bool]): Indicates if the user can list child files or folders.
        can_modify_content (Optional[bool]): Indicates if the user can modify the file's content. Example: True.
        can_modify_content_restriction (Optional[bool]): Indicates if content restrictions can be modified. Example:
                True.
        can_modify_editor_content_restriction (Optional[bool]): Indicates if editor content restrictions can be
                modified. Example: True.
        can_modify_labels (Optional[bool]): Indicates if the user can modify labels on the file. Example: True.
        can_modify_owner_content_restriction (Optional[bool]): Shows if the user can change content restrictions set by
                the owner. Example: True.
        can_move_children_within_drive (Optional[bool]): Indicates if child items can be moved within the drive.
        can_move_item_into_team_drive (Optional[bool]): Indicates if the item can be moved into a shared drive. Example:
                True.
        can_move_item_out_of_drive (Optional[bool]): Indicates if the user can move the item out of Google Drive.
                Example: True.
        can_move_item_within_drive (Optional[bool]): Indicates if the user can move the file within Google Drive.
                Example: True.
        can_read_labels (Optional[bool]): Indicates if the user can read labels on the file. Example: True.
        can_read_revisions (Optional[bool]): Indicates if the user can read the file's revision history. Example: True.
        can_remove_children (Optional[bool]): Indicates if the user can remove child files or folders.
        can_remove_content_restriction (Optional[bool]): Indicates if content restrictions can be removed from the file.
        can_remove_my_drive_parent (Optional[bool]): Indicates if the file can be removed from the My Drive folder.
                Example: True.
        can_rename (Optional[bool]): Indicates if the file can be renamed by the user. Example: True.
        can_share (Optional[bool]): Indicates if the user can share the file with others. Example: True.
        can_trash (Optional[bool]): Indicates if the file can be moved to the trash by the user. Example: True.
        can_untrash (Optional[bool]): Indicates if the user can restore the file from the trash. Example: True.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    can_accept_ownership: Optional[bool] = Field(
        alias="canAcceptOwnership", default=None
    )
    can_add_children: Optional[bool] = Field(alias="canAddChildren", default=None)
    can_add_my_drive_parent: Optional[bool] = Field(
        alias="canAddMyDriveParent", default=None
    )
    can_change_copy_requires_writer_permission: Optional[bool] = Field(
        alias="canChangeCopyRequiresWriterPermission", default=None
    )
    can_change_security_update_enabled: Optional[bool] = Field(
        alias="canChangeSecurityUpdateEnabled", default=None
    )
    can_change_viewers_can_copy_content: Optional[bool] = Field(
        alias="canChangeViewersCanCopyContent", default=None
    )
    can_comment: Optional[bool] = Field(alias="canComment", default=None)
    can_copy: Optional[bool] = Field(alias="canCopy", default=None)
    can_delete: Optional[bool] = Field(alias="canDelete", default=None)
    can_disable_inherited_permissions: Optional[bool] = Field(
        alias="canDisableInheritedPermissions", default=None
    )
    can_download: Optional[bool] = Field(alias="canDownload", default=None)
    can_edit: Optional[bool] = Field(alias="canEdit", default=None)
    can_enable_inherited_permissions: Optional[bool] = Field(
        alias="canEnableInheritedPermissions", default=None
    )
    can_list_children: Optional[bool] = Field(alias="canListChildren", default=None)
    can_modify_content: Optional[bool] = Field(alias="canModifyContent", default=None)
    can_modify_content_restriction: Optional[bool] = Field(
        alias="canModifyContentRestriction", default=None
    )
    can_modify_editor_content_restriction: Optional[bool] = Field(
        alias="canModifyEditorContentRestriction", default=None
    )
    can_modify_labels: Optional[bool] = Field(alias="canModifyLabels", default=None)
    can_modify_owner_content_restriction: Optional[bool] = Field(
        alias="canModifyOwnerContentRestriction", default=None
    )
    can_move_children_within_drive: Optional[bool] = Field(
        alias="canMoveChildrenWithinDrive", default=None
    )
    can_move_item_into_team_drive: Optional[bool] = Field(
        alias="canMoveItemIntoTeamDrive", default=None
    )
    can_move_item_out_of_drive: Optional[bool] = Field(
        alias="canMoveItemOutOfDrive", default=None
    )
    can_move_item_within_drive: Optional[bool] = Field(
        alias="canMoveItemWithinDrive", default=None
    )
    can_read_labels: Optional[bool] = Field(alias="canReadLabels", default=None)
    can_read_revisions: Optional[bool] = Field(alias="canReadRevisions", default=None)
    can_remove_children: Optional[bool] = Field(alias="canRemoveChildren", default=None)
    can_remove_content_restriction: Optional[bool] = Field(
        alias="canRemoveContentRestriction", default=None
    )
    can_remove_my_drive_parent: Optional[bool] = Field(
        alias="canRemoveMyDriveParent", default=None
    )
    can_rename: Optional[bool] = Field(alias="canRename", default=None)
    can_share: Optional[bool] = Field(alias="canShare", default=None)
    can_trash: Optional[bool] = Field(alias="canTrash", default=None)
    can_untrash: Optional[bool] = Field(alias="canUntrash", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(
        cls: Type["GetFileOrFolderResponseCapabilities"], src_dict: Dict[str, Any]
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
