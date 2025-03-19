from .get_file_labels import (
    get_file_labels as _get_file_labels,
    get_file_labels_async as _get_file_labels_async,
)
from ..models.default_error import DefaultError
from ..models.get_file_labels import GetFileLabels
from typing import cast
from .share_file_or_folder import (
    share_file_or_folder as _share_file_or_folder,
    share_file_or_folder_async as _share_file_or_folder_async,
)
from ..models.share_file_or_folder_request import ShareFileOrFolderRequest
from ..models.share_file_or_folder_response import ShareFileOrFolderResponse
from .download_file import (
    download_file as _download_file,
    download_file_async as _download_file_async,
)
from .get_fileor_folder import (
    get_file_or_folder as _get_file_or_folder,
    get_file_or_folder_async as _get_file_or_folder_async,
)
from ..models.get_file_or_folder_response import GetFileOrFolderResponse
from .remove_labels import (
    remove_labels as _remove_labels,
    remove_labels_async as _remove_labels_async,
)
from ..models.remove_labels_request import RemoveLabelsRequest
from ..models.remove_labels_response import RemoveLabelsResponse
from .labels import (
    get_drive_labels as _get_drive_labels,
    get_drive_labels_async as _get_drive_labels_async,
)
from ..models.get_drive_labels import GetDriveLabels
from .move_fileor_folder import (
    move_fileor_folder as _move_fileor_folder,
    move_fileor_folder_async as _move_fileor_folder_async,
)
from ..models.move_fileor_folder_request import MoveFileorFolderRequest
from ..models.move_fileor_folder_response import MoveFileorFolderResponse
from .create_folder import (
    create_folder as _create_folder,
    create_folder_async as _create_folder_async,
)
from ..models.create_folder_request import CreateFolderRequest
from ..models.create_folder_response import CreateFolderResponse
from .copy_file import (
    copy_file as _copy_file,
    copy_file_async as _copy_file_async,
)
from ..models.copy_file_request import CopyFileRequest
from ..models.copy_file_response import CopyFileResponse
from .delete_fileor_folder import (
    delete_fileor_folder as _delete_fileor_folder,
    delete_fileor_folder_async as _delete_fileor_folder_async,
)
from .upload_file import (
    upload_files as _upload_files,
    upload_files_async as _upload_files_async,
)
from ..models.upload_files_request import UploadFilesRequest
from ..models.upload_files_response import UploadFilesResponse
from .get_fileor_folder_list import (
    get_fileor_folder_list as _get_fileor_folder_list,
    get_fileor_folder_list_async as _get_fileor_folder_list_async,
)
from ..models.get_fileor_folder_list import GetFileorFolderList
from .modify_label import (
    apply_labels as _apply_labels,
    apply_labels_async as _apply_labels_async,
)
from ..models.apply_labels_request import ApplyLabelsRequest
from ..models.apply_labels_response import ApplyLabelsResponse

from pydantic import Field
from typing import Any, Optional, Union

from ..client import Client
import httpx


class GoogleDrive:
    def __init__(self, *, instance_id: str, client: httpx.Client):
        base_url = str(client.base_url).rstrip("/")
        new_headers = {
            k: v for k, v in client.headers.items() if k not in ["content-type"]
        }
        new_client = httpx.Client(
            base_url=base_url + f"/elements_/v3/element/instances/{instance_id}",
            headers=new_headers,
            timeout=100,
        )
        new_client_async = httpx.AsyncClient(
            base_url=base_url + f"/elements_/v3/element/instances/{instance_id}",
            headers=new_headers,
            timeout=100,
        )
        self.client = (
            Client(
                base_url="",  # this will be overridden by the base_url in the Client constructor
            )
            .set_httpx_client(new_client)
            .set_async_httpx_client(new_client_async)
        )

    def get_file_labels(
        self,
        *,
        file_id: str,
        file_id_lookup: Any,
        fields: Optional[str] = None,
        fields_lookup: Any,
        next_page: Optional[str] = None,
        next_page_lookup: Any,
        page_size: Optional[int] = None,
        page_size_lookup: Any,
    ) -> Optional[Union[DefaultError, list["GetFileLabels"]]]:
        return _get_file_labels(
            client=self.client,
            file_id=file_id,
            file_id_lookup=file_id_lookup,
            fields=fields,
            fields_lookup=fields_lookup,
            next_page=next_page,
            next_page_lookup=next_page_lookup,
            page_size=page_size,
            page_size_lookup=page_size_lookup,
        )

    async def get_file_labels_async(
        self,
        *,
        file_id: str,
        file_id_lookup: Any,
        fields: Optional[str] = None,
        fields_lookup: Any,
        next_page: Optional[str] = None,
        next_page_lookup: Any,
        page_size: Optional[int] = None,
        page_size_lookup: Any,
    ) -> Optional[Union[DefaultError, list["GetFileLabels"]]]:
        return await _get_file_labels_async(
            client=self.client,
            file_id=file_id,
            file_id_lookup=file_id_lookup,
            fields=fields,
            fields_lookup=fields_lookup,
            next_page=next_page,
            next_page_lookup=next_page_lookup,
            page_size=page_size,
            page_size_lookup=page_size_lookup,
        )

    def share_file_or_folder(
        self,
        *,
        body: ShareFileOrFolderRequest,
        send_notification_email: bool = True,
        send_notification_email_lookup: Any,
        file_id: str,
        file_id_lookup: Any,
    ) -> Optional[Union[DefaultError, ShareFileOrFolderResponse]]:
        return _share_file_or_folder(
            client=self.client,
            body=body,
            send_notification_email=send_notification_email,
            send_notification_email_lookup=send_notification_email_lookup,
            file_id=file_id,
            file_id_lookup=file_id_lookup,
        )

    async def share_file_or_folder_async(
        self,
        *,
        body: ShareFileOrFolderRequest,
        send_notification_email: bool = True,
        send_notification_email_lookup: Any,
        file_id: str,
        file_id_lookup: Any,
    ) -> Optional[Union[DefaultError, ShareFileOrFolderResponse]]:
        return await _share_file_or_folder_async(
            client=self.client,
            body=body,
            send_notification_email=send_notification_email,
            send_notification_email_lookup=send_notification_email_lookup,
            file_id=file_id,
            file_id_lookup=file_id_lookup,
        )

    def download_file(
        self,
        *,
        file_id: str,
        file_id_lookup: Any,
        file_name: Optional[str] = None,
        file_name_lookup: Any,
        mime_type: Optional[str] = None,
        mime_type_lookup: Any,
    ) -> Optional[Union[Any, DefaultError]]:
        return _download_file(
            client=self.client,
            file_id=file_id,
            file_id_lookup=file_id_lookup,
            file_name=file_name,
            file_name_lookup=file_name_lookup,
            mime_type=mime_type,
            mime_type_lookup=mime_type_lookup,
        )

    async def download_file_async(
        self,
        *,
        file_id: str,
        file_id_lookup: Any,
        file_name: Optional[str] = None,
        file_name_lookup: Any,
        mime_type: Optional[str] = None,
        mime_type_lookup: Any,
    ) -> Optional[Union[Any, DefaultError]]:
        return await _download_file_async(
            client=self.client,
            file_id=file_id,
            file_id_lookup=file_id_lookup,
            file_name=file_name,
            file_name_lookup=file_name_lookup,
            mime_type=mime_type,
            mime_type_lookup=mime_type_lookup,
        )

    def get_file_or_folder(
        self,
        id: str,
        id_lookup: Any,
        *,
        supports_all_drives: Optional[bool] = None,
        supports_all_drives_lookup: Any,
    ) -> Optional[Union[DefaultError, GetFileOrFolderResponse]]:
        return _get_file_or_folder(
            client=self.client,
            id=id,
            id_lookup=id_lookup,
            supports_all_drives=supports_all_drives,
            supports_all_drives_lookup=supports_all_drives_lookup,
        )

    async def get_file_or_folder_async(
        self,
        id: str,
        id_lookup: Any,
        *,
        supports_all_drives: Optional[bool] = None,
        supports_all_drives_lookup: Any,
    ) -> Optional[Union[DefaultError, GetFileOrFolderResponse]]:
        return await _get_file_or_folder_async(
            client=self.client,
            id=id,
            id_lookup=id_lookup,
            supports_all_drives=supports_all_drives,
            supports_all_drives_lookup=supports_all_drives_lookup,
        )

    def remove_labels(
        self,
        file_id: str,
        file_id_lookup: Any,
        *,
        body: RemoveLabelsRequest,
    ) -> Optional[Union[DefaultError, RemoveLabelsResponse]]:
        return _remove_labels(
            client=self.client,
            file_id=file_id,
            file_id_lookup=file_id_lookup,
            body=body,
        )

    async def remove_labels_async(
        self,
        file_id: str,
        file_id_lookup: Any,
        *,
        body: RemoveLabelsRequest,
    ) -> Optional[Union[DefaultError, RemoveLabelsResponse]]:
        return await _remove_labels_async(
            client=self.client,
            file_id=file_id,
            file_id_lookup=file_id_lookup,
            body=body,
        )

    def get_drive_labels(
        self,
        *,
        fields: Optional[str] = None,
        fields_lookup: Any,
        next_page: Optional[str] = None,
        next_page_lookup: Any,
        page_size: Optional[int] = None,
        page_size_lookup: Any,
    ) -> Optional[Union[DefaultError, list["GetDriveLabels"]]]:
        return _get_drive_labels(
            client=self.client,
            fields=fields,
            fields_lookup=fields_lookup,
            next_page=next_page,
            next_page_lookup=next_page_lookup,
            page_size=page_size,
            page_size_lookup=page_size_lookup,
        )

    async def get_drive_labels_async(
        self,
        *,
        fields: Optional[str] = None,
        fields_lookup: Any,
        next_page: Optional[str] = None,
        next_page_lookup: Any,
        page_size: Optional[int] = None,
        page_size_lookup: Any,
    ) -> Optional[Union[DefaultError, list["GetDriveLabels"]]]:
        return await _get_drive_labels_async(
            client=self.client,
            fields=fields,
            fields_lookup=fields_lookup,
            next_page=next_page,
            next_page_lookup=next_page_lookup,
            page_size=page_size,
            page_size_lookup=page_size_lookup,
        )

    def move_fileor_folder(
        self,
        *,
        body: MoveFileorFolderRequest,
        add_parents: str,
        add_parents_lookup: Any,
        file_id: str,
        file_id_lookup: Any,
        remove_parents: Optional[str] = None,
        remove_parents_lookup: Any,
    ) -> Optional[Union[DefaultError, MoveFileorFolderResponse]]:
        return _move_fileor_folder(
            client=self.client,
            body=body,
            add_parents=add_parents,
            add_parents_lookup=add_parents_lookup,
            file_id=file_id,
            file_id_lookup=file_id_lookup,
            remove_parents=remove_parents,
            remove_parents_lookup=remove_parents_lookup,
        )

    async def move_fileor_folder_async(
        self,
        *,
        body: MoveFileorFolderRequest,
        add_parents: str,
        add_parents_lookup: Any,
        file_id: str,
        file_id_lookup: Any,
        remove_parents: Optional[str] = None,
        remove_parents_lookup: Any,
    ) -> Optional[Union[DefaultError, MoveFileorFolderResponse]]:
        return await _move_fileor_folder_async(
            client=self.client,
            body=body,
            add_parents=add_parents,
            add_parents_lookup=add_parents_lookup,
            file_id=file_id,
            file_id_lookup=file_id_lookup,
            remove_parents=remove_parents,
            remove_parents_lookup=remove_parents_lookup,
        )

    def create_folder(
        self,
        *,
        body: CreateFolderRequest,
    ) -> Optional[Union[CreateFolderResponse, DefaultError]]:
        return _create_folder(
            client=self.client,
            body=body,
        )

    async def create_folder_async(
        self,
        *,
        body: CreateFolderRequest,
    ) -> Optional[Union[CreateFolderResponse, DefaultError]]:
        return await _create_folder_async(
            client=self.client,
            body=body,
        )

    def copy_file(
        self,
        *,
        body: CopyFileRequest,
        file_id: str,
        file_id_lookup: Any,
    ) -> Optional[Union[CopyFileResponse, DefaultError]]:
        return _copy_file(
            client=self.client,
            body=body,
            file_id=file_id,
            file_id_lookup=file_id_lookup,
        )

    async def copy_file_async(
        self,
        *,
        body: CopyFileRequest,
        file_id: str,
        file_id_lookup: Any,
    ) -> Optional[Union[CopyFileResponse, DefaultError]]:
        return await _copy_file_async(
            client=self.client,
            body=body,
            file_id=file_id,
            file_id_lookup=file_id_lookup,
        )

    def delete_fileor_folder(
        self,
        *,
        file_id: str,
        file_id_lookup: Any,
    ) -> Optional[Union[Any, DefaultError]]:
        return _delete_fileor_folder(
            client=self.client,
            file_id=file_id,
            file_id_lookup=file_id_lookup,
        )

    async def delete_fileor_folder_async(
        self,
        *,
        file_id: str,
        file_id_lookup: Any,
    ) -> Optional[Union[Any, DefaultError]]:
        return await _delete_fileor_folder_async(
            client=self.client,
            file_id=file_id,
            file_id_lookup=file_id_lookup,
        )

    def upload_files(
        self,
        *,
        body: UploadFilesRequest,
        convert: Optional[bool] = None,
        convert_lookup: Any,
    ) -> Optional[Union[DefaultError, UploadFilesResponse]]:
        return _upload_files(
            client=self.client,
            body=body,
            convert=convert,
            convert_lookup=convert_lookup,
        )

    async def upload_files_async(
        self,
        *,
        body: UploadFilesRequest,
        convert: Optional[bool] = None,
        convert_lookup: Any,
    ) -> Optional[Union[DefaultError, UploadFilesResponse]]:
        return await _upload_files_async(
            client=self.client,
            body=body,
            convert=convert,
            convert_lookup=convert_lookup,
        )

    def get_fileor_folder_list(
        self,
        *,
        parent_id: str,
        parent_id_lookup: Any,
        fields: Optional[str] = None,
        fields_lookup: Any,
        next_page: Optional[str] = None,
        next_page_lookup: Any,
        page_size: Optional[int] = None,
        page_size_lookup: Any,
        starred_only: Optional[bool] = False,
        starred_only_lookup: Any,
        what_to_return: Optional[str] = "files",
        what_to_return_lookup: Any,
    ) -> Optional[Union[DefaultError, list["GetFileorFolderList"]]]:
        return _get_fileor_folder_list(
            client=self.client,
            parent_id=parent_id,
            parent_id_lookup=parent_id_lookup,
            fields=fields,
            fields_lookup=fields_lookup,
            next_page=next_page,
            next_page_lookup=next_page_lookup,
            page_size=page_size,
            page_size_lookup=page_size_lookup,
            starred_only=starred_only,
            starred_only_lookup=starred_only_lookup,
            what_to_return=what_to_return,
            what_to_return_lookup=what_to_return_lookup,
        )

    async def get_fileor_folder_list_async(
        self,
        *,
        parent_id: str,
        parent_id_lookup: Any,
        fields: Optional[str] = None,
        fields_lookup: Any,
        next_page: Optional[str] = None,
        next_page_lookup: Any,
        page_size: Optional[int] = None,
        page_size_lookup: Any,
        starred_only: Optional[bool] = False,
        starred_only_lookup: Any,
        what_to_return: Optional[str] = "files",
        what_to_return_lookup: Any,
    ) -> Optional[Union[DefaultError, list["GetFileorFolderList"]]]:
        return await _get_fileor_folder_list_async(
            client=self.client,
            parent_id=parent_id,
            parent_id_lookup=parent_id_lookup,
            fields=fields,
            fields_lookup=fields_lookup,
            next_page=next_page,
            next_page_lookup=next_page_lookup,
            page_size=page_size,
            page_size_lookup=page_size_lookup,
            starred_only=starred_only,
            starred_only_lookup=starred_only_lookup,
            what_to_return=what_to_return,
            what_to_return_lookup=what_to_return_lookup,
        )

    def apply_labels(
        self,
        file_id: str,
        file_id_lookup: Any,
        *,
        body: ApplyLabelsRequest,
    ) -> Optional[Union[ApplyLabelsResponse, DefaultError]]:
        return _apply_labels(
            client=self.client,
            file_id=file_id,
            file_id_lookup=file_id_lookup,
            body=body,
        )

    async def apply_labels_async(
        self,
        file_id: str,
        file_id_lookup: Any,
        *,
        body: ApplyLabelsRequest,
    ) -> Optional[Union[ApplyLabelsResponse, DefaultError]]:
        return await _apply_labels_async(
            client=self.client,
            file_id=file_id,
            file_id_lookup=file_id_lookup,
            body=body,
        )
