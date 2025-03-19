from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

import datetime
from ..models.get_file_or_folder_response_image_media_metadata import (
    GetFileOrFolderResponseImageMediaMetadata,
)
from ..models.get_file_or_folder_response_last_modifying_user import (
    GetFileOrFolderResponseLastModifyingUser,
)
from ..models.get_file_or_folder_response_capabilities import (
    GetFileOrFolderResponseCapabilities,
)
from ..models.get_file_or_folder_response_permissions_array_item_ref import (
    GetFileOrFolderResponsePermissionsArrayItemRef,
)
from ..models.get_file_or_folder_response_link_share_metadata import (
    GetFileOrFolderResponseLinkShareMetadata,
)
from ..models.get_file_or_folder_response_owners_array_item_ref import (
    GetFileOrFolderResponseOwnersArrayItemRef,
)


class GetFileOrFolderResponse(BaseModel):
    """
    Attributes:
        capabilities (Optional[GetFileOrFolderResponseCapabilities]):
        copy_requires_writer_permission (Optional[bool]): Specifies if copying the file requires writer permission.
        created_time (Optional[datetime.datetime]): The date and time when the file was created. Example:
                2025-02-13T07:29:23.1040000+00:00.
        explicitly_trashed (Optional[bool]): Indicates if the file was explicitly moved to trash.
        file_extension (Optional[str]): Specifies the file extension, indicating the file type. Example: png.
        full_file_extension (Optional[str]): Provides the complete file extension, including multiple parts. Example:
                png.
        has_thumbnail (Optional[bool]): Indicates if a thumbnail image is available. Example: True.
        head_revision_id (Optional[str]): The unique identifier for the latest file revision. Example:
                0B7hwk0b56Qg4dlpsKy96bXVnQWl2L1BNMEhuTkVlRmxZTzBZPQ.
        icon_link (Optional[str]): URL to the icon representing the file type. Example: https://drive-
                thirdparty.googleusercontent.com/16/type/image/png.
        id (Optional[str]): A unique identifier assigned to the file. Example: 1EKt00NeawSSjX024pWmzgLpbXIYHuy0V.
        image_media_metadata (Optional[GetFileOrFolderResponseImageMediaMetadata]):
        inherited_permissions_disabled (Optional[bool]): Shows if inherited permissions are disabled for the file.
        is_app_authorized (Optional[bool]): Indicates whether the app is authorized to access the file. Example: True.
        kind (Optional[str]): Specifies the type of resource in the response. Example: drive#file.
        last_modifying_user (Optional[GetFileOrFolderResponseLastModifyingUser]):
        link_share_metadata (Optional[GetFileOrFolderResponseLinkShareMetadata]):
        md_5_checksum (Optional[str]): A hash value used to verify file integrity. Example:
                c32525664af1946676057f036d0ce236.
        mime_type (Optional[str]): The MIME type of the file, indicating its format. Example: image/png.
        modified_by_me (Optional[bool]): Indicates if the file was last modified by the user. Example: True.
        modified_by_me_time (Optional[datetime.datetime]): The timestamp of when the file was last modified by the user.
                Example: 2025-02-13T07:29:23.1040000+00:00.
        modified_time (Optional[datetime.datetime]): Shows the last time the file was modified. Example:
                2025-02-13T07:29:23.1040000+00:00.
        name (Optional[str]): The name of the file. Example: Screenshot 2025-02-13 at 11.39.35???AM.png.
        original_filename (Optional[str]): The name of the file as it was originally uploaded. Example: Screenshot
                2025-02-13 at 11.39.35???AM.png.
        owned_by_me (Optional[bool]): Shows whether the file is owned by the current user. Example: True.
        owners (Optional[list['GetFileOrFolderResponseOwnersArrayItemRef']]):
        parents (Optional[list[str]]):  Example: 0ALhwk0b56Qg4Uk9PVA.
        permission_ids (Optional[list[str]]):  Example: 03464898141015738316.
        permissions (Optional[list['GetFileOrFolderResponsePermissionsArrayItemRef']]):
        quota_bytes_used (Optional[str]): Amount of storage space used by the file in bytes. Example: 154898.
        sha_1_checksum (Optional[str]): A SHA-1 hash of the file content for verification. Example:
                cd4313d327c73f0e01ab0f2777b037af2e6b5744.
        sha_256_checksum (Optional[str]): A checksum to verify the file's integrity using SHA-256. Example:
                c1372dc7db507eb7983ebd5978952e0a30c358b4175ace9afa03e13aa5e0acd6.
        shared (Optional[bool]): Indicates whether the file is shared with other users.
        size (Optional[str]): The size of the file in bytes. Example: 154898.
        spaces (Optional[list[str]]):  Example: drive.
        starred (Optional[bool]): Indicates if the file is marked as important by the user.
        thumbnail_link (Optional[str]): A URL link to a small preview image of the file. Example:
                https://lh3.googleusercontent.com/drive-storage/AJQWtBPs05-
                TD6jly7Jkj5I7j5RSRtFUn8b5MRHjOVK1unNk7vbMiLpvbwGXostogBKd0i9cKIRGNUINvJNfab4dZ54eUP55lLcQVje-n6SgSUM1kyA=s220.
        thumbnail_version (Optional[str]): Represents the version number of the file's thumbnail. Example: 1.
        trashed (Optional[bool]): Indicates if the file is in the trash.
        version (Optional[str]): The current version number of the file. Example: 95.
        viewed_by_me (Optional[bool]): Shows if the file has been viewed by the current user. Example: True.
        viewed_by_me_time (Optional[datetime.datetime]): The last time the file was viewed by the user. Example:
                2025-02-21T16:37:28.8870000+00:00.
        viewers_can_copy_content (Optional[bool]): Indicates if viewers are allowed to copy the file content. Example:
                True.
        web_content_link (Optional[str]): Provides a URL to access the file's content on the web. Example:
                https://drive.google.com/uc?id=1EKt00NeawSSjX024pWmzgLpbXIYHuy0V&export=download.
        web_view_link (Optional[str]): Provides a URL to view the file in a web browser. Example:
                https://drive.google.com/file/d/1EKt00NeawSSjX024pWmzgLpbXIYHuy0V/view?usp=drivesdk.
        writers_can_share (Optional[bool]): Indicates if users with write access can share the file. Example: True.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    capabilities: Optional["GetFileOrFolderResponseCapabilities"] = Field(
        alias="capabilities", default=None
    )
    copy_requires_writer_permission: Optional[bool] = Field(
        alias="copyRequiresWriterPermission", default=None
    )
    created_time: Optional[datetime.datetime] = Field(alias="createdTime", default=None)
    explicitly_trashed: Optional[bool] = Field(alias="explicitlyTrashed", default=None)
    file_extension: Optional[str] = Field(alias="fileExtension", default=None)
    full_file_extension: Optional[str] = Field(alias="fullFileExtension", default=None)
    has_thumbnail: Optional[bool] = Field(alias="hasThumbnail", default=None)
    head_revision_id: Optional[str] = Field(alias="headRevisionId", default=None)
    icon_link: Optional[str] = Field(alias="iconLink", default=None)
    id: Optional[str] = Field(alias="id", default=None)
    image_media_metadata: Optional["GetFileOrFolderResponseImageMediaMetadata"] = Field(
        alias="imageMediaMetadata", default=None
    )
    inherited_permissions_disabled: Optional[bool] = Field(
        alias="inheritedPermissionsDisabled", default=None
    )
    is_app_authorized: Optional[bool] = Field(alias="isAppAuthorized", default=None)
    kind: Optional[str] = Field(alias="kind", default=None)
    last_modifying_user: Optional["GetFileOrFolderResponseLastModifyingUser"] = Field(
        alias="lastModifyingUser", default=None
    )
    link_share_metadata: Optional["GetFileOrFolderResponseLinkShareMetadata"] = Field(
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
    owners: Optional[list["GetFileOrFolderResponseOwnersArrayItemRef"]] = Field(
        alias="owners", default=None
    )
    parents: Optional[list[str]] = Field(alias="parents", default=None)
    permission_ids: Optional[list[str]] = Field(alias="permissionIds", default=None)
    permissions: Optional[list["GetFileOrFolderResponsePermissionsArrayItemRef"]] = (
        Field(alias="permissions", default=None)
    )
    quota_bytes_used: Optional[str] = Field(alias="quotaBytesUsed", default=None)
    sha_1_checksum: Optional[str] = Field(alias="sha1Checksum", default=None)
    sha_256_checksum: Optional[str] = Field(alias="sha256Checksum", default=None)
    shared: Optional[bool] = Field(alias="shared", default=None)
    size: Optional[str] = Field(alias="size", default=None)
    spaces: Optional[list[str]] = Field(alias="spaces", default=None)
    starred: Optional[bool] = Field(alias="starred", default=None)
    thumbnail_link: Optional[str] = Field(alias="thumbnailLink", default=None)
    thumbnail_version: Optional[str] = Field(alias="thumbnailVersion", default=None)
    trashed: Optional[bool] = Field(alias="trashed", default=None)
    version: Optional[str] = Field(alias="version", default=None)
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
    def from_dict(cls: Type["GetFileOrFolderResponse"], src_dict: Dict[str, Any]):
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
