"""Contains all the data models used in inputs/outputs"""

from .apply_labels_request import ApplyLabelsRequest
from .apply_labels_response import ApplyLabelsResponse
from .copy_file_request import CopyFileRequest
from .copy_file_response import CopyFileResponse
from .create_folder_request import CreateFolderRequest
from .create_folder_response import CreateFolderResponse
from .default_error import DefaultError
from .get_drive_labels import GetDriveLabels
from .get_drive_labels_applied_capabilities import GetDriveLabelsAppliedCapabilities
from .get_drive_labels_applied_label_policy import GetDriveLabelsAppliedLabelPolicy
from .get_drive_labels_creator import GetDriveLabelsCreator
from .get_drive_labels_display_hints import GetDriveLabelsDisplayHints
from .get_drive_labels_fields_applied_capabilities import (
    GetDriveLabelsFieldsAppliedCapabilities,
)
from .get_drive_labels_fields_array_item_ref import GetDriveLabelsFieldsArrayItemRef
from .get_drive_labels_fields_creator import GetDriveLabelsFieldsCreator
from .get_drive_labels_fields_display_hints import GetDriveLabelsFieldsDisplayHints
from .get_drive_labels_fields_lifecycle import GetDriveLabelsFieldsLifecycle
from .get_drive_labels_fields_properties import GetDriveLabelsFieldsProperties
from .get_drive_labels_fields_publisher import GetDriveLabelsFieldsPublisher
from .get_drive_labels_fields_selection_options import (
    GetDriveLabelsFieldsSelectionOptions,
)
from .get_drive_labels_fields_selection_options_choices_applied_capabilities import (
    GetDriveLabelsFieldsSelectionOptionsChoicesAppliedCapabilities,
)
from .get_drive_labels_fields_selection_options_choices_array_item_ref import (
    GetDriveLabelsFieldsSelectionOptionsChoicesArrayItemRef,
)
from .get_drive_labels_fields_selection_options_choices_display_hints import (
    GetDriveLabelsFieldsSelectionOptionsChoicesDisplayHints,
)
from .get_drive_labels_fields_selection_options_choices_display_hints_badge_colors import (
    GetDriveLabelsFieldsSelectionOptionsChoicesDisplayHintsBadgeColors,
)
from .get_drive_labels_fields_selection_options_choices_display_hints_badge_colors_background_color import (
    GetDriveLabelsFieldsSelectionOptionsChoicesDisplayHintsBadgeColorsBackgroundColor,
)
from .get_drive_labels_fields_selection_options_choices_display_hints_badge_colors_foreground_color import (
    GetDriveLabelsFieldsSelectionOptionsChoicesDisplayHintsBadgeColorsForegroundColor,
)
from .get_drive_labels_fields_selection_options_choices_display_hints_badge_colors_solo_color import (
    GetDriveLabelsFieldsSelectionOptionsChoicesDisplayHintsBadgeColorsSoloColor,
)
from .get_drive_labels_fields_selection_options_choices_display_hints_dark_badge_colors import (
    GetDriveLabelsFieldsSelectionOptionsChoicesDisplayHintsDarkBadgeColors,
)
from .get_drive_labels_fields_selection_options_choices_display_hints_dark_badge_colors_background_color import (
    GetDriveLabelsFieldsSelectionOptionsChoicesDisplayHintsDarkBadgeColorsBackgroundColor,
)
from .get_drive_labels_fields_selection_options_choices_display_hints_dark_badge_colors_foreground_color import (
    GetDriveLabelsFieldsSelectionOptionsChoicesDisplayHintsDarkBadgeColorsForegroundColor,
)
from .get_drive_labels_fields_selection_options_choices_display_hints_dark_badge_colors_solo_color import (
    GetDriveLabelsFieldsSelectionOptionsChoicesDisplayHintsDarkBadgeColorsSoloColor,
)
from .get_drive_labels_fields_selection_options_choices_lifecycle import (
    GetDriveLabelsFieldsSelectionOptionsChoicesLifecycle,
)
from .get_drive_labels_fields_selection_options_choices_properties import (
    GetDriveLabelsFieldsSelectionOptionsChoicesProperties,
)
from .get_drive_labels_fields_selection_options_choices_properties_badge_config import (
    GetDriveLabelsFieldsSelectionOptionsChoicesPropertiesBadgeConfig,
)
from .get_drive_labels_fields_selection_options_choices_properties_badge_config_color import (
    GetDriveLabelsFieldsSelectionOptionsChoicesPropertiesBadgeConfigColor,
)
from .get_drive_labels_fields_updater import GetDriveLabelsFieldsUpdater
from .get_drive_labels_lifecycle import GetDriveLabelsLifecycle
from .get_drive_labels_properties import GetDriveLabelsProperties
from .get_drive_labels_publisher import GetDriveLabelsPublisher
from .get_drive_labels_revision_creator import GetDriveLabelsRevisionCreator
from .get_file_labels import GetFileLabels
from .get_file_or_folder_response import GetFileOrFolderResponse
from .get_file_or_folder_response_capabilities import (
    GetFileOrFolderResponseCapabilities,
)
from .get_file_or_folder_response_image_media_metadata import (
    GetFileOrFolderResponseImageMediaMetadata,
)
from .get_file_or_folder_response_last_modifying_user import (
    GetFileOrFolderResponseLastModifyingUser,
)
from .get_file_or_folder_response_link_share_metadata import (
    GetFileOrFolderResponseLinkShareMetadata,
)
from .get_file_or_folder_response_owners_array_item_ref import (
    GetFileOrFolderResponseOwnersArrayItemRef,
)
from .get_file_or_folder_response_permissions_array_item_ref import (
    GetFileOrFolderResponsePermissionsArrayItemRef,
)
from .get_fileor_folder_list import GetFileorFolderList
from .move_fileor_folder_request import MoveFileorFolderRequest
from .move_fileor_folder_response import MoveFileorFolderResponse
from .remove_labels_request import RemoveLabelsRequest
from .remove_labels_response import RemoveLabelsResponse
from .share_file_or_folder_request import ShareFileOrFolderRequest
from .share_file_or_folder_request_permission import ShareFileOrFolderRequestPermission
from .share_file_or_folder_request_share_with import ShareFileOrFolderRequestShareWith
from .share_file_or_folder_response import ShareFileOrFolderResponse
from .share_file_or_folder_response_permission import (
    ShareFileOrFolderResponsePermission,
)
from .share_file_or_folder_response_share_with import ShareFileOrFolderResponseShareWith
from .upload_files_request import UploadFilesRequest
from .upload_files_response import UploadFilesResponse
from .upload_files_response_app_properties import UploadFilesResponseAppProperties
from .upload_files_response_capabilities import UploadFilesResponseCapabilities
from .upload_files_response_content_hints import UploadFilesResponseContentHints
from .upload_files_response_content_hints_thumbnail import (
    UploadFilesResponseContentHintsThumbnail,
)
from .upload_files_response_content_restrictions_array_item_ref import (
    UploadFilesResponseContentRestrictionsArrayItemRef,
)
from .upload_files_response_content_restrictions_restricting_user import (
    UploadFilesResponseContentRestrictionsRestrictingUser,
)
from .upload_files_response_export_links import UploadFilesResponseExportLinks
from .upload_files_response_image_media_metadata import (
    UploadFilesResponseImageMediaMetadata,
)
from .upload_files_response_image_media_metadata_location import (
    UploadFilesResponseImageMediaMetadataLocation,
)
from .upload_files_response_last_modifying_user import (
    UploadFilesResponseLastModifyingUser,
)
from .upload_files_response_link_share_metadata import (
    UploadFilesResponseLinkShareMetadata,
)
from .upload_files_response_owners_array_item_ref import (
    UploadFilesResponseOwnersArrayItemRef,
)
from .upload_files_response_permissions_array_item_ref import (
    UploadFilesResponsePermissionsArrayItemRef,
)
from .upload_files_response_permissions_permission_details_array_item_ref import (
    UploadFilesResponsePermissionsPermissionDetailsArrayItemRef,
)
from .upload_files_response_permissions_team_drive_permission_details_array_item_ref import (
    UploadFilesResponsePermissionsTeamDrivePermissionDetailsArrayItemRef,
)
from .upload_files_response_properties import UploadFilesResponseProperties
from .upload_files_response_sharing_user import UploadFilesResponseSharingUser
from .upload_files_response_shortcut_details import UploadFilesResponseShortcutDetails
from .upload_files_response_trashing_user import UploadFilesResponseTrashingUser
from .upload_files_response_video_media_metadata import (
    UploadFilesResponseVideoMediaMetadata,
)

__all__ = (
    "ApplyLabelsRequest",
    "ApplyLabelsResponse",
    "CopyFileRequest",
    "CopyFileResponse",
    "CreateFolderRequest",
    "CreateFolderResponse",
    "DefaultError",
    "GetDriveLabels",
    "GetDriveLabelsAppliedCapabilities",
    "GetDriveLabelsAppliedLabelPolicy",
    "GetDriveLabelsCreator",
    "GetDriveLabelsDisplayHints",
    "GetDriveLabelsFieldsAppliedCapabilities",
    "GetDriveLabelsFieldsArrayItemRef",
    "GetDriveLabelsFieldsCreator",
    "GetDriveLabelsFieldsDisplayHints",
    "GetDriveLabelsFieldsLifecycle",
    "GetDriveLabelsFieldsProperties",
    "GetDriveLabelsFieldsPublisher",
    "GetDriveLabelsFieldsSelectionOptions",
    "GetDriveLabelsFieldsSelectionOptionsChoicesAppliedCapabilities",
    "GetDriveLabelsFieldsSelectionOptionsChoicesArrayItemRef",
    "GetDriveLabelsFieldsSelectionOptionsChoicesDisplayHints",
    "GetDriveLabelsFieldsSelectionOptionsChoicesDisplayHintsBadgeColors",
    "GetDriveLabelsFieldsSelectionOptionsChoicesDisplayHintsBadgeColorsBackgroundColor",
    "GetDriveLabelsFieldsSelectionOptionsChoicesDisplayHintsBadgeColorsForegroundColor",
    "GetDriveLabelsFieldsSelectionOptionsChoicesDisplayHintsBadgeColorsSoloColor",
    "GetDriveLabelsFieldsSelectionOptionsChoicesDisplayHintsDarkBadgeColors",
    "GetDriveLabelsFieldsSelectionOptionsChoicesDisplayHintsDarkBadgeColorsBackgroundColor",
    "GetDriveLabelsFieldsSelectionOptionsChoicesDisplayHintsDarkBadgeColorsForegroundColor",
    "GetDriveLabelsFieldsSelectionOptionsChoicesDisplayHintsDarkBadgeColorsSoloColor",
    "GetDriveLabelsFieldsSelectionOptionsChoicesLifecycle",
    "GetDriveLabelsFieldsSelectionOptionsChoicesProperties",
    "GetDriveLabelsFieldsSelectionOptionsChoicesPropertiesBadgeConfig",
    "GetDriveLabelsFieldsSelectionOptionsChoicesPropertiesBadgeConfigColor",
    "GetDriveLabelsFieldsUpdater",
    "GetDriveLabelsLifecycle",
    "GetDriveLabelsProperties",
    "GetDriveLabelsPublisher",
    "GetDriveLabelsRevisionCreator",
    "GetFileLabels",
    "GetFileorFolderList",
    "GetFileOrFolderResponse",
    "GetFileOrFolderResponseCapabilities",
    "GetFileOrFolderResponseImageMediaMetadata",
    "GetFileOrFolderResponseLastModifyingUser",
    "GetFileOrFolderResponseLinkShareMetadata",
    "GetFileOrFolderResponseOwnersArrayItemRef",
    "GetFileOrFolderResponsePermissionsArrayItemRef",
    "MoveFileorFolderRequest",
    "MoveFileorFolderResponse",
    "RemoveLabelsRequest",
    "RemoveLabelsResponse",
    "ShareFileOrFolderRequest",
    "ShareFileOrFolderRequestPermission",
    "ShareFileOrFolderRequestShareWith",
    "ShareFileOrFolderResponse",
    "ShareFileOrFolderResponsePermission",
    "ShareFileOrFolderResponseShareWith",
    "UploadFilesRequest",
    "UploadFilesResponse",
    "UploadFilesResponseAppProperties",
    "UploadFilesResponseCapabilities",
    "UploadFilesResponseContentHints",
    "UploadFilesResponseContentHintsThumbnail",
    "UploadFilesResponseContentRestrictionsArrayItemRef",
    "UploadFilesResponseContentRestrictionsRestrictingUser",
    "UploadFilesResponseExportLinks",
    "UploadFilesResponseImageMediaMetadata",
    "UploadFilesResponseImageMediaMetadataLocation",
    "UploadFilesResponseLastModifyingUser",
    "UploadFilesResponseLinkShareMetadata",
    "UploadFilesResponseOwnersArrayItemRef",
    "UploadFilesResponsePermissionsArrayItemRef",
    "UploadFilesResponsePermissionsPermissionDetailsArrayItemRef",
    "UploadFilesResponsePermissionsTeamDrivePermissionDetailsArrayItemRef",
    "UploadFilesResponseProperties",
    "UploadFilesResponseSharingUser",
    "UploadFilesResponseShortcutDetails",
    "UploadFilesResponseTrashingUser",
    "UploadFilesResponseVideoMediaMetadata",
)
