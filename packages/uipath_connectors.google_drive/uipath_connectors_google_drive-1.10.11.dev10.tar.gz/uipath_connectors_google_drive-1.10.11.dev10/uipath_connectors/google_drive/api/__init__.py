from .modify_label import (
    apply_labels as _apply_labels,
    apply_labels_async as _apply_labels_async,
)
from ..models.apply_labels_request import ApplyLabelsRequest
from ..models.apply_labels_response import ApplyLabelsResponse
from ..models.default_error import DefaultError
from typing import cast
from .copy_file import (
    copy_file as _copy_file,
    copy_file_async as _copy_file_async,
)
from ..models.copy_file_request import CopyFileRequest
from ..models.copy_file_response import CopyFileResponse
from .create_folder import (
    create_folder as _create_folder,
    create_folder_async as _create_folder_async,
)
from ..models.create_folder_request import CreateFolderRequest
from ..models.create_folder_response import CreateFolderResponse
from .delete_fileor_folder import (
    delete_fileor_folder as _delete_fileor_folder,
    delete_fileor_folder_async as _delete_fileor_folder_async,
)
from .download_file import (
    download_file as _download_file,
    download_file_async as _download_file_async,
)
from ..models.download_file_response import DownloadFileResponse
from ..types import File
from io import BytesIO
from .labels import (
    get_drive_labels as _get_drive_labels,
    get_drive_labels_async as _get_drive_labels_async,
)
from ..models.get_drive_labels import GetDriveLabels
from .get_file_labels import (
    get_file_labels as _get_file_labels,
    get_file_labels_async as _get_file_labels_async,
)
from ..models.get_file_labels import GetFileLabels
from .get_fileor_folder import (
    get_file_or_folder as _get_file_or_folder,
    get_file_or_folder_async as _get_file_or_folder_async,
)
from ..models.get_file_or_folder_response import GetFileOrFolderResponse
from .get_fileor_folder_list import (
    get_fileor_folder_list as _get_fileor_folder_list,
    get_fileor_folder_list_async as _get_fileor_folder_list_async,
)
from ..models.get_fileor_folder_list import GetFileorFolderList
from .move_fileor_folder import (
    move_fileor_folder as _move_fileor_folder,
    move_fileor_folder_async as _move_fileor_folder_async,
)
from ..models.move_fileor_folder_request import MoveFileorFolderRequest
from ..models.move_fileor_folder_response import MoveFileorFolderResponse
from .remove_labels import (
    remove_labels as _remove_labels,
    remove_labels_async as _remove_labels_async,
)
from ..models.remove_labels_request import RemoveLabelsRequest
from ..models.remove_labels_response import RemoveLabelsResponse
from .share_file_or_folder import (
    share_file_or_folder as _share_file_or_folder,
    share_file_or_folder_async as _share_file_or_folder_async,
)
from ..models.share_file_or_folder_request import ShareFileOrFolderRequest
from ..models.share_file_or_folder_response import ShareFileOrFolderResponse
from .upload_file import (
    upload_files as _upload_files,
    upload_files_async as _upload_files_async,
)
from ..models.upload_files_body import UploadFilesBody
from ..models.upload_files_request import UploadFilesRequest
from ..models.upload_files_response import UploadFilesResponse

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

    def download_file(
        self,
        *,
        mime_type: Optional[str] = None,
        file_id: str,
        file_id_lookup: Any,
        file_name: Optional[str] = None,
    ) -> Optional[Union[DefaultError, File]]:
        return _download_file(
            client=self.client,
            mime_type=mime_type,
            file_id=file_id,
            file_id_lookup=file_id_lookup,
            file_name=file_name,
        )

    async def download_file_async(
        self,
        *,
        mime_type: Optional[str] = None,
        file_id: str,
        file_id_lookup: Any,
        file_name: Optional[str] = None,
    ) -> Optional[Union[DefaultError, File]]:
        return await _download_file_async(
            client=self.client,
            mime_type=mime_type,
            file_id=file_id,
            file_id_lookup=file_id_lookup,
            file_name=file_name,
        )

    def get_drive_labels(
        self,
        *,
        page_size: Optional[int] = None,
        next_page: Optional[str] = None,
    ) -> Optional[Union[DefaultError, list["GetDriveLabels"]]]:
        return _get_drive_labels(
            client=self.client,
            page_size=page_size,
            next_page=next_page,
        )

    async def get_drive_labels_async(
        self,
        *,
        page_size: Optional[int] = None,
        next_page: Optional[str] = None,
    ) -> Optional[Union[DefaultError, list["GetDriveLabels"]]]:
        return await _get_drive_labels_async(
            client=self.client,
            page_size=page_size,
            next_page=next_page,
        )

    def get_file_labels(
        self,
        *,
        file_id: str,
        file_id_lookup: Any,
    ) -> Optional[Union[DefaultError, list["GetFileLabels"]]]:
        return _get_file_labels(
            client=self.client,
            file_id=file_id,
            file_id_lookup=file_id_lookup,
        )

    async def get_file_labels_async(
        self,
        *,
        file_id: str,
        file_id_lookup: Any,
    ) -> Optional[Union[DefaultError, list["GetFileLabels"]]]:
        return await _get_file_labels_async(
            client=self.client,
            file_id=file_id,
            file_id_lookup=file_id_lookup,
        )

    def get_file_or_folder(
        self,
        id: str,
        id_lookup: Any,
        *,
        supports_all_drives: Optional[bool] = None,
    ) -> Optional[Union[DefaultError, GetFileOrFolderResponse]]:
        return _get_file_or_folder(
            client=self.client,
            id=id,
            id_lookup=id_lookup,
            supports_all_drives=supports_all_drives,
        )

    async def get_file_or_folder_async(
        self,
        id: str,
        id_lookup: Any,
        *,
        supports_all_drives: Optional[bool] = None,
    ) -> Optional[Union[DefaultError, GetFileOrFolderResponse]]:
        return await _get_file_or_folder_async(
            client=self.client,
            id=id,
            id_lookup=id_lookup,
            supports_all_drives=supports_all_drives,
        )

    def get_fileor_folder_list(
        self,
        *,
        page_size: Optional[int] = None,
        next_page: Optional[str] = None,
        starred_only: Optional[bool] = False,
        what_to_return: Optional[str] = "files",
        parent_id: str,
        parent_id_lookup: Any,
    ) -> Optional[Union[DefaultError, list["GetFileorFolderList"]]]:
        return _get_fileor_folder_list(
            client=self.client,
            page_size=page_size,
            next_page=next_page,
            starred_only=starred_only,
            what_to_return=what_to_return,
            parent_id=parent_id,
            parent_id_lookup=parent_id_lookup,
        )

    async def get_fileor_folder_list_async(
        self,
        *,
        page_size: Optional[int] = None,
        next_page: Optional[str] = None,
        starred_only: Optional[bool] = False,
        what_to_return: Optional[str] = "files",
        parent_id: str,
        parent_id_lookup: Any,
    ) -> Optional[Union[DefaultError, list["GetFileorFolderList"]]]:
        return await _get_fileor_folder_list_async(
            client=self.client,
            page_size=page_size,
            next_page=next_page,
            starred_only=starred_only,
            what_to_return=what_to_return,
            parent_id=parent_id,
            parent_id_lookup=parent_id_lookup,
        )

    def move_fileor_folder(
        self,
        *,
        body: MoveFileorFolderRequest,
        remove_parents: Optional[str] = None,
        add_parents: str,
        add_parents_lookup: Any,
        file_id: str,
        file_id_lookup: Any,
    ) -> Optional[Union[DefaultError, MoveFileorFolderResponse]]:
        return _move_fileor_folder(
            client=self.client,
            body=body,
            remove_parents=remove_parents,
            add_parents=add_parents,
            add_parents_lookup=add_parents_lookup,
            file_id=file_id,
            file_id_lookup=file_id_lookup,
        )

    async def move_fileor_folder_async(
        self,
        *,
        body: MoveFileorFolderRequest,
        remove_parents: Optional[str] = None,
        add_parents: str,
        add_parents_lookup: Any,
        file_id: str,
        file_id_lookup: Any,
    ) -> Optional[Union[DefaultError, MoveFileorFolderResponse]]:
        return await _move_fileor_folder_async(
            client=self.client,
            body=body,
            remove_parents=remove_parents,
            add_parents=add_parents,
            add_parents_lookup=add_parents_lookup,
            file_id=file_id,
            file_id_lookup=file_id_lookup,
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

    def share_file_or_folder(
        self,
        *,
        body: ShareFileOrFolderRequest,
        send_notification_email: bool = True,
        file_id: str,
        file_id_lookup: Any,
    ) -> Optional[Union[DefaultError, ShareFileOrFolderResponse]]:
        return _share_file_or_folder(
            client=self.client,
            body=body,
            send_notification_email=send_notification_email,
            file_id=file_id,
            file_id_lookup=file_id_lookup,
        )

    async def share_file_or_folder_async(
        self,
        *,
        body: ShareFileOrFolderRequest,
        send_notification_email: bool = True,
        file_id: str,
        file_id_lookup: Any,
    ) -> Optional[Union[DefaultError, ShareFileOrFolderResponse]]:
        return await _share_file_or_folder_async(
            client=self.client,
            body=body,
            send_notification_email=send_notification_email,
            file_id=file_id,
            file_id_lookup=file_id_lookup,
        )

    def upload_files(
        self,
        *,
        body: UploadFilesBody,
        convert: Optional[bool] = None,
    ) -> Optional[Union[DefaultError, UploadFilesResponse]]:
        return _upload_files(
            client=self.client,
            body=body,
            convert=convert,
        )

    async def upload_files_async(
        self,
        *,
        body: UploadFilesBody,
        convert: Optional[bool] = None,
    ) -> Optional[Union[DefaultError, UploadFilesResponse]]:
        return await _upload_files_async(
            client=self.client,
            body=body,
            convert=convert,
        )
