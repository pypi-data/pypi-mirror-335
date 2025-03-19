from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

import datetime
from ..models.upload_files_response_app_properties import (
    UploadFilesResponseAppProperties,
)
from ..models.upload_files_response_sharing_user import UploadFilesResponseSharingUser
from ..models.upload_files_response_image_media_metadata import (
    UploadFilesResponseImageMediaMetadata,
)
from ..models.upload_files_response_trashing_user import UploadFilesResponseTrashingUser
from ..models.upload_files_response_owners_array_item_ref import (
    UploadFilesResponseOwnersArrayItemRef,
)
from ..models.upload_files_response_link_share_metadata import (
    UploadFilesResponseLinkShareMetadata,
)
from ..models.upload_files_response_capabilities import UploadFilesResponseCapabilities
from ..models.upload_files_response_content_hints import UploadFilesResponseContentHints
from ..models.upload_files_response_last_modifying_user import (
    UploadFilesResponseLastModifyingUser,
)
from ..models.upload_files_response_properties import UploadFilesResponseProperties
from ..models.upload_files_response_permissions_array_item_ref import (
    UploadFilesResponsePermissionsArrayItemRef,
)
from ..models.upload_files_response_video_media_metadata import (
    UploadFilesResponseVideoMediaMetadata,
)
from ..models.upload_files_response_shortcut_details import (
    UploadFilesResponseShortcutDetails,
)
from ..models.upload_files_response_content_restrictions_array_item_ref import (
    UploadFilesResponseContentRestrictionsArrayItemRef,
)
from ..models.upload_files_response_export_links import UploadFilesResponseExportLinks


class UploadFilesResponse(BaseModel):
    """
    Attributes:
        app_properties (Optional[UploadFilesResponseAppProperties]):
        capabilities (Optional[UploadFilesResponseCapabilities]):
        content_hints (Optional[UploadFilesResponseContentHints]):
        content_restrictions (Optional[list['UploadFilesResponseContentRestrictionsArrayItemRef']]):
        copy_requires_writer_permission (Optional[bool]):
        created_time (Optional[datetime.datetime]):
        description (Optional[str]):
        drive_id (Optional[str]):
        explicitly_trashed (Optional[bool]):
        export_links (Optional[UploadFilesResponseExportLinks]):
        file_extension (Optional[str]):
        folder_color_rgb (Optional[str]):
        full_file_extension (Optional[str]):
        has_augmented_permissions (Optional[bool]):
        has_thumbnail (Optional[bool]):
        head_revision_id (Optional[str]):
        icon_link (Optional[str]):
        id (Optional[str]):
        image_media_metadata (Optional[UploadFilesResponseImageMediaMetadata]):
        is_app_authorized (Optional[bool]):
        kind (Optional[str]):
        last_modifying_user (Optional[UploadFilesResponseLastModifyingUser]):
        link_share_metadata (Optional[UploadFilesResponseLinkShareMetadata]):
        md_5_checksum (Optional[str]):
        mime_type (Optional[str]):
        modified_by_me (Optional[bool]):
        modified_by_me_time (Optional[datetime.datetime]):
        modified_time (Optional[datetime.datetime]):
        name (Optional[str]):
        original_filename (Optional[str]):
        owned_by_me (Optional[bool]):
        owners (Optional[list['UploadFilesResponseOwnersArrayItemRef']]):
        parents (Optional[list[str]]):
        permission_ids (Optional[list[str]]):
        permissions (Optional[list['UploadFilesResponsePermissionsArrayItemRef']]):
        properties (Optional[UploadFilesResponseProperties]):
        quota_bytes_used (Optional[str]):
        resource_key (Optional[str]):
        shared (Optional[bool]):
        shared_with_me_time (Optional[datetime.datetime]):
        sharing_user (Optional[UploadFilesResponseSharingUser]):
        shortcut_details (Optional[UploadFilesResponseShortcutDetails]):
        size (Optional[str]):
        spaces (Optional[list[str]]):
        starred (Optional[bool]):
        team_drive_id (Optional[str]):
        thumbnail_link (Optional[str]):
        thumbnail_version (Optional[str]):
        trashed (Optional[bool]):
        trashed_time (Optional[datetime.datetime]):
        trashing_user (Optional[UploadFilesResponseTrashingUser]):
        version (Optional[str]):
        video_media_metadata (Optional[UploadFilesResponseVideoMediaMetadata]):
        viewed_by_me (Optional[bool]):
        viewed_by_me_time (Optional[datetime.datetime]):
        viewers_can_copy_content (Optional[bool]):
        web_content_link (Optional[str]):
        web_view_link (Optional[str]):
        writers_can_share (Optional[bool]):
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    app_properties: Optional["UploadFilesResponseAppProperties"] = Field(
        alias="appProperties", default=None
    )
    capabilities: Optional["UploadFilesResponseCapabilities"] = Field(
        alias="capabilities", default=None
    )
    content_hints: Optional["UploadFilesResponseContentHints"] = Field(
        alias="contentHints", default=None
    )
    content_restrictions: Optional[
        list["UploadFilesResponseContentRestrictionsArrayItemRef"]
    ] = Field(alias="contentRestrictions", default=None)
    copy_requires_writer_permission: Optional[bool] = Field(
        alias="copyRequiresWriterPermission", default=None
    )
    created_time: Optional[datetime.datetime] = Field(alias="createdTime", default=None)
    description: Optional[str] = Field(alias="description", default=None)
    drive_id: Optional[str] = Field(alias="driveId", default=None)
    explicitly_trashed: Optional[bool] = Field(alias="explicitlyTrashed", default=None)
    export_links: Optional["UploadFilesResponseExportLinks"] = Field(
        alias="exportLinks", default=None
    )
    file_extension: Optional[str] = Field(alias="fileExtension", default=None)
    folder_color_rgb: Optional[str] = Field(alias="folderColorRgb", default=None)
    full_file_extension: Optional[str] = Field(alias="fullFileExtension", default=None)
    has_augmented_permissions: Optional[bool] = Field(
        alias="hasAugmentedPermissions", default=None
    )
    has_thumbnail: Optional[bool] = Field(alias="hasThumbnail", default=None)
    head_revision_id: Optional[str] = Field(alias="headRevisionId", default=None)
    icon_link: Optional[str] = Field(alias="iconLink", default=None)
    id: Optional[str] = Field(alias="id", default=None)
    image_media_metadata: Optional["UploadFilesResponseImageMediaMetadata"] = Field(
        alias="imageMediaMetadata", default=None
    )
    is_app_authorized: Optional[bool] = Field(alias="isAppAuthorized", default=None)
    kind: Optional[str] = Field(alias="kind", default=None)
    last_modifying_user: Optional["UploadFilesResponseLastModifyingUser"] = Field(
        alias="lastModifyingUser", default=None
    )
    link_share_metadata: Optional["UploadFilesResponseLinkShareMetadata"] = Field(
        alias="linkShareMetadata", default=None
    )
    md_5_checksum: Optional[str] = Field(alias="md5Checksum", default=None)
    mime_type: Optional[str] = Field(alias="mimeType", default=None)
    modified_by_me: Optional[bool] = Field(alias="modifiedByMe", default=None)
    modified_by_me_time: Optional[datetime.datetime] = Field(
        alias="modifiedByMeTime", default=None
    )
    modified_time: Optional[datetime.datetime] = Field(
        alias="modifiedTime", default=None
    )
    name: Optional[str] = Field(alias="name", default=None)
    original_filename: Optional[str] = Field(alias="originalFilename", default=None)
    owned_by_me: Optional[bool] = Field(alias="ownedByMe", default=None)
    owners: Optional[list["UploadFilesResponseOwnersArrayItemRef"]] = Field(
        alias="owners", default=None
    )
    parents: Optional[list[str]] = Field(alias="parents", default=None)
    permission_ids: Optional[list[str]] = Field(alias="permissionIds", default=None)
    permissions: Optional[list["UploadFilesResponsePermissionsArrayItemRef"]] = Field(
        alias="permissions", default=None
    )
    properties: Optional["UploadFilesResponseProperties"] = Field(
        alias="properties", default=None
    )
    quota_bytes_used: Optional[str] = Field(alias="quotaBytesUsed", default=None)
    resource_key: Optional[str] = Field(alias="resourceKey", default=None)
    shared: Optional[bool] = Field(alias="shared", default=None)
    shared_with_me_time: Optional[datetime.datetime] = Field(
        alias="sharedWithMeTime", default=None
    )
    sharing_user: Optional["UploadFilesResponseSharingUser"] = Field(
        alias="sharingUser", default=None
    )
    shortcut_details: Optional["UploadFilesResponseShortcutDetails"] = Field(
        alias="shortcutDetails", default=None
    )
    size: Optional[str] = Field(alias="size", default=None)
    spaces: Optional[list[str]] = Field(alias="spaces", default=None)
    starred: Optional[bool] = Field(alias="starred", default=None)
    team_drive_id: Optional[str] = Field(alias="teamDriveId", default=None)
    thumbnail_link: Optional[str] = Field(alias="thumbnailLink", default=None)
    thumbnail_version: Optional[str] = Field(alias="thumbnailVersion", default=None)
    trashed: Optional[bool] = Field(alias="trashed", default=None)
    trashed_time: Optional[datetime.datetime] = Field(alias="trashedTime", default=None)
    trashing_user: Optional["UploadFilesResponseTrashingUser"] = Field(
        alias="trashingUser", default=None
    )
    version: Optional[str] = Field(alias="version", default=None)
    video_media_metadata: Optional["UploadFilesResponseVideoMediaMetadata"] = Field(
        alias="videoMediaMetadata", default=None
    )
    viewed_by_me: Optional[bool] = Field(alias="viewedByMe", default=None)
    viewed_by_me_time: Optional[datetime.datetime] = Field(
        alias="viewedByMeTime", default=None
    )
    viewers_can_copy_content: Optional[bool] = Field(
        alias="viewersCanCopyContent", default=None
    )
    web_content_link: Optional[str] = Field(alias="webContentLink", default=None)
    web_view_link: Optional[str] = Field(alias="webViewLink", default=None)
    writers_can_share: Optional[bool] = Field(alias="writersCanShare", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["UploadFilesResponse"], src_dict: Dict[str, Any]):
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
