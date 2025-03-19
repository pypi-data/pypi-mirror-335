from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type


class UploadFilesResponseCapabilities(BaseModel):
    """
    Attributes:
        can_accept_ownership (Optional[bool]):
        can_add_children (Optional[bool]):
        can_add_folder_from_another_drive (Optional[bool]):
        can_add_my_drive_parent (Optional[bool]):
        can_change_copy_requires_writer_permission (Optional[bool]):
        can_change_security_update_enabled (Optional[bool]):
        can_change_viewers_can_copy_content (Optional[bool]):
        can_comment (Optional[bool]):
        can_copy (Optional[bool]):
        can_delete (Optional[bool]):
        can_delete_children (Optional[bool]):
        can_download (Optional[bool]):
        can_edit (Optional[bool]):
        can_list_children (Optional[bool]):
        can_modify_content (Optional[bool]):
        can_modify_content_restriction (Optional[bool]):
        can_move_children_out_of_drive (Optional[bool]):
        can_move_children_out_of_team_drive (Optional[bool]):
        can_move_children_within_drive (Optional[bool]):
        can_move_children_within_team_drive (Optional[bool]):
        can_move_item_into_team_drive (Optional[bool]):
        can_move_item_out_of_drive (Optional[bool]):
        can_move_item_out_of_team_drive (Optional[bool]):
        can_move_item_within_drive (Optional[bool]):
        can_move_item_within_team_drive (Optional[bool]):
        can_move_team_drive_item (Optional[bool]):
        can_read_drive (Optional[bool]):
        can_read_revisions (Optional[bool]):
        can_read_team_drive (Optional[bool]):
        can_remove_children (Optional[bool]):
        can_remove_my_drive_parent (Optional[bool]):
        can_rename (Optional[bool]):
        can_share (Optional[bool]):
        can_trash (Optional[bool]):
        can_trash_children (Optional[bool]):
        can_untrash (Optional[bool]):
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    can_accept_ownership: Optional[bool] = Field(
        alias="canAcceptOwnership", default=None
    )
    can_add_children: Optional[bool] = Field(alias="canAddChildren", default=None)
    can_add_folder_from_another_drive: Optional[bool] = Field(
        alias="canAddFolderFromAnotherDrive", default=None
    )
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
    can_delete_children: Optional[bool] = Field(alias="canDeleteChildren", default=None)
    can_download: Optional[bool] = Field(alias="canDownload", default=None)
    can_edit: Optional[bool] = Field(alias="canEdit", default=None)
    can_list_children: Optional[bool] = Field(alias="canListChildren", default=None)
    can_modify_content: Optional[bool] = Field(alias="canModifyContent", default=None)
    can_modify_content_restriction: Optional[bool] = Field(
        alias="canModifyContentRestriction", default=None
    )
    can_move_children_out_of_drive: Optional[bool] = Field(
        alias="canMoveChildrenOutOfDrive", default=None
    )
    can_move_children_out_of_team_drive: Optional[bool] = Field(
        alias="canMoveChildrenOutOfTeamDrive", default=None
    )
    can_move_children_within_drive: Optional[bool] = Field(
        alias="canMoveChildrenWithinDrive", default=None
    )
    can_move_children_within_team_drive: Optional[bool] = Field(
        alias="canMoveChildrenWithinTeamDrive", default=None
    )
    can_move_item_into_team_drive: Optional[bool] = Field(
        alias="canMoveItemIntoTeamDrive", default=None
    )
    can_move_item_out_of_drive: Optional[bool] = Field(
        alias="canMoveItemOutOfDrive", default=None
    )
    can_move_item_out_of_team_drive: Optional[bool] = Field(
        alias="canMoveItemOutOfTeamDrive", default=None
    )
    can_move_item_within_drive: Optional[bool] = Field(
        alias="canMoveItemWithinDrive", default=None
    )
    can_move_item_within_team_drive: Optional[bool] = Field(
        alias="canMoveItemWithinTeamDrive", default=None
    )
    can_move_team_drive_item: Optional[bool] = Field(
        alias="canMoveTeamDriveItem", default=None
    )
    can_read_drive: Optional[bool] = Field(alias="canReadDrive", default=None)
    can_read_revisions: Optional[bool] = Field(alias="canReadRevisions", default=None)
    can_read_team_drive: Optional[bool] = Field(alias="canReadTeamDrive", default=None)
    can_remove_children: Optional[bool] = Field(alias="canRemoveChildren", default=None)
    can_remove_my_drive_parent: Optional[bool] = Field(
        alias="canRemoveMyDriveParent", default=None
    )
    can_rename: Optional[bool] = Field(alias="canRename", default=None)
    can_share: Optional[bool] = Field(alias="canShare", default=None)
    can_trash: Optional[bool] = Field(alias="canTrash", default=None)
    can_trash_children: Optional[bool] = Field(alias="canTrashChildren", default=None)
    can_untrash: Optional[bool] = Field(alias="canUntrash", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(
        cls: Type["UploadFilesResponseCapabilities"], src_dict: Dict[str, Any]
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
