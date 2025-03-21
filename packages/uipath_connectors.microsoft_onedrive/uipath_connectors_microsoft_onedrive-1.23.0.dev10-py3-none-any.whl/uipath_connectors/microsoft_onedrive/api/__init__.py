from .add_sheet import (
    add_sheet as _add_sheet,
    add_sheet_async as _add_sheet_async,
)
from ..models.add_sheet_request import AddSheetRequest
from ..models.add_sheet_response import AddSheetResponse
from ..models.default_error import DefaultError
from typing import cast
from .copy_file_folder import (
    copy_file_folder as _copy_file_folder,
    copy_file_folder_async as _copy_file_folder_async,
)
from ..models.copy_file_folder_request import CopyFileFolderRequest
from ..models.copy_file_folder_response import CopyFileFolderResponse
from .create_folder import (
    create_folder as _create_folder,
    create_folder_async as _create_folder_async,
)
from ..models.create_folder_request import CreateFolderRequest
from ..models.create_folder_response import CreateFolderResponse
from .create_share_link import (
    create_share_link as _create_share_link,
    create_share_link_async as _create_share_link_async,
)
from ..models.create_share_link_request import CreateShareLinkRequest
from ..models.create_share_link_response import CreateShareLinkResponse
from .create_workbook import (
    create_workbook as _create_workbook,
    create_workbook_async as _create_workbook_async,
)
from ..models.create_workbook_request import CreateWorkbookRequest
from ..models.create_workbook_response import CreateWorkbookResponse
from .curated_file import (
    curated_file as _curated_file,
    curated_file_async as _curated_file_async,
    get_file_list as _get_file_list,
    get_file_list_async as _get_file_list_async,
)
from ..models.curated_file import CuratedFile
from ..models.get_file_list_response import GetFileListResponse
from .curated_file_and_folder import (
    curated_file_and_folder as _curated_file_and_folder,
    curated_file_and_folder_async as _curated_file_and_folder_async,
    get_file_folder as _get_file_folder,
    get_file_folder_async as _get_file_folder_async,
)
from ..models.curated_file_and_folder import CuratedFileAndFolder
from ..models.get_file_folder_response import GetFileFolderResponse
from .delete_column import (
    delete_column as _delete_column,
    delete_column_async as _delete_column_async,
)
from ..models.delete_column_request import DeleteColumnRequest
from .delete_file_folder import (
    delete_file_folder as _delete_file_folder,
    delete_file_folder_async as _delete_file_folder_async,
)
from .delete_range import (
    delete_range as _delete_range,
    delete_range_async as _delete_range_async,
)
from ..models.delete_range_request import DeleteRangeRequest
from .delete_row import (
    delete_row as _delete_row,
    delete_row_async as _delete_row_async,
)
from ..models.delete_row_request import DeleteRowRequest
from .delete_sheet import (
    delete_sheet as _delete_sheet,
    delete_sheet_async as _delete_sheet_async,
)
from .download_file import (
    download_file as _download_file,
    download_file_async as _download_file_async,
)
from ..models.download_file_response import DownloadFileResponse
from ..types import File
from io import BytesIO
from .file_checkin_check_out import (
    file_checkin_check_out as _file_checkin_check_out,
    file_checkin_check_out_async as _file_checkin_check_out_async,
)
from ..models.file_checkin_check_out_request import FileCheckinCheckOutRequest
from .file_upload_v2 import (
    file_upload_v2 as _file_upload_v2,
    file_upload_v2_async as _file_upload_v2_async,
)
from ..models.file_upload_v2_body import FileUploadV2Body
from ..models.file_upload_v2_response import FileUploadV2Response
from .get_file_folder_metadata import (
    get_file_folder_metadata as _get_file_folder_metadata,
    get_file_folder_metadata_async as _get_file_folder_metadata_async,
)
from ..models.get_file_folder_metadata_response import GetFileFolderMetadataResponse
from .get_files_folders import (
    get_files_folders as _get_files_folders,
    get_files_folders_async as _get_files_folders_async,
    get_files_folders_list as _get_files_folders_list,
    get_files_folders_list_async as _get_files_folders_list_async,
)
from ..models.get_files_folders_response import GetFilesFoldersResponse
from ..models.get_files_folders_list import GetFilesFoldersList
from .move_file_folder import (
    move_file_folder as _move_file_folder,
    move_file_folder_async as _move_file_folder_async,
)
from ..models.move_file_folder_request import MoveFileFolderRequest
from ..models.move_file_folder_response import MoveFileFolderResponse
from .read_cell import (
    read_cell as _read_cell,
    read_cell_async as _read_cell_async,
)
from ..models.read_cell import ReadCell
from .read_range import (
    read_range as _read_range,
    read_range_async as _read_range_async,
)
from ..models.read_range import ReadRange
from .rename_sheet import (
    rename_sheet as _rename_sheet,
    rename_sheet_async as _rename_sheet_async,
)
from ..models.rename_sheet_request import RenameSheetRequest
from ..models.rename_sheet_response import RenameSheetResponse
from .share_file_or_folder import (
    share_file_or_folder as _share_file_or_folder,
    share_file_or_folder_async as _share_file_or_folder_async,
)
from ..models.share_file_or_folder_request import ShareFileOrFolderRequest
from ..models.share_file_or_folder_response import ShareFileOrFolderResponse
from .write_cell import (
    write_cell as _write_cell,
    write_cell_async as _write_cell_async,
)
from ..models.write_cell_request import WriteCellRequest
from .write_column import (
    write_column as _write_column,
    write_column_async as _write_column_async,
)
from ..models.write_column_request import WriteColumnRequest
from .write_range import (
    write_range as _write_range,
    write_range_async as _write_range_async,
)
from ..models.write_range_request import WriteRangeRequest
from .write_row import (
    write_row as _write_row,
    write_row_async as _write_row_async,
)
from ..models.write_row_request import WriteRowRequest

from pydantic import Field
from typing import Any, Optional, Union

from ..client import Client
import httpx


class MicrosoftOnedrive:
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

    def add_sheet(
        self,
        *,
        body: AddSheetRequest,
        reference_id: str,
        reference_id_lookup: Any,
    ) -> Optional[Union[AddSheetResponse, DefaultError]]:
        return _add_sheet(
            client=self.client,
            body=body,
            reference_id=reference_id,
            reference_id_lookup=reference_id_lookup,
        )

    async def add_sheet_async(
        self,
        *,
        body: AddSheetRequest,
        reference_id: str,
        reference_id_lookup: Any,
    ) -> Optional[Union[AddSheetResponse, DefaultError]]:
        return await _add_sheet_async(
            client=self.client,
            body=body,
            reference_id=reference_id,
            reference_id_lookup=reference_id_lookup,
        )

    def copy_file_folder(
        self,
        *,
        body: CopyFileFolderRequest,
        conflict_behavior: Optional[str] = None,
    ) -> Optional[Union[CopyFileFolderResponse, DefaultError]]:
        return _copy_file_folder(
            client=self.client,
            body=body,
            conflict_behavior=conflict_behavior,
        )

    async def copy_file_folder_async(
        self,
        *,
        body: CopyFileFolderRequest,
        conflict_behavior: Optional[str] = None,
    ) -> Optional[Union[CopyFileFolderResponse, DefaultError]]:
        return await _copy_file_folder_async(
            client=self.client,
            body=body,
            conflict_behavior=conflict_behavior,
        )

    def create_folder(
        self,
        *,
        body: CreateFolderRequest,
        conflict_behavior: Optional[str] = None,
    ) -> Optional[Union[CreateFolderResponse, DefaultError]]:
        return _create_folder(
            client=self.client,
            body=body,
            conflict_behavior=conflict_behavior,
        )

    async def create_folder_async(
        self,
        *,
        body: CreateFolderRequest,
        conflict_behavior: Optional[str] = None,
    ) -> Optional[Union[CreateFolderResponse, DefaultError]]:
        return await _create_folder_async(
            client=self.client,
            body=body,
            conflict_behavior=conflict_behavior,
        )

    def create_share_link(
        self,
        *,
        body: CreateShareLinkRequest,
    ) -> Optional[Union[CreateShareLinkResponse, DefaultError]]:
        return _create_share_link(
            client=self.client,
            body=body,
        )

    async def create_share_link_async(
        self,
        *,
        body: CreateShareLinkRequest,
    ) -> Optional[Union[CreateShareLinkResponse, DefaultError]]:
        return await _create_share_link_async(
            client=self.client,
            body=body,
        )

    def create_workbook(
        self,
        *,
        body: CreateWorkbookRequest,
        reference_id: str,
        reference_id_lookup: Any,
    ) -> Optional[Union[CreateWorkbookResponse, DefaultError]]:
        return _create_workbook(
            client=self.client,
            body=body,
            reference_id=reference_id,
            reference_id_lookup=reference_id_lookup,
        )

    async def create_workbook_async(
        self,
        *,
        body: CreateWorkbookRequest,
        reference_id: str,
        reference_id_lookup: Any,
    ) -> Optional[Union[CreateWorkbookResponse, DefaultError]]:
        return await _create_workbook_async(
            client=self.client,
            body=body,
            reference_id=reference_id,
            reference_id_lookup=reference_id_lookup,
        )

    def curated_file(
        self,
        *,
        page_size: Optional[int] = None,
        next_page: Optional[str] = None,
        drive_id: Optional[str] = None,
        path: Optional[str] = None,
        id: Optional[str] = None,
    ) -> Optional[Union[DefaultError, list["CuratedFile"]]]:
        return _curated_file(
            client=self.client,
            page_size=page_size,
            next_page=next_page,
            drive_id=drive_id,
            path=path,
            id=id,
        )

    async def curated_file_async(
        self,
        *,
        page_size: Optional[int] = None,
        next_page: Optional[str] = None,
        drive_id: Optional[str] = None,
        path: Optional[str] = None,
        id: Optional[str] = None,
    ) -> Optional[Union[DefaultError, list["CuratedFile"]]]:
        return await _curated_file_async(
            client=self.client,
            page_size=page_size,
            next_page=next_page,
            drive_id=drive_id,
            path=path,
            id=id,
        )

    def get_file_list(
        self,
        id: str,
        *,
        drive_id: Optional[str] = None,
    ) -> Optional[Union[DefaultError, GetFileListResponse]]:
        return _get_file_list(
            client=self.client,
            id=id,
            drive_id=drive_id,
        )

    async def get_file_list_async(
        self,
        id: str,
        *,
        drive_id: Optional[str] = None,
    ) -> Optional[Union[DefaultError, GetFileListResponse]]:
        return await _get_file_list_async(
            client=self.client,
            id=id,
            drive_id=drive_id,
        )

    def curated_file_and_folder(
        self,
        *,
        page_size: Optional[int] = None,
        next_page: Optional[str] = None,
        drive_id: Optional[str] = None,
        path: Optional[str] = None,
        id: Optional[str] = None,
    ) -> Optional[Union[DefaultError, list["CuratedFileAndFolder"]]]:
        return _curated_file_and_folder(
            client=self.client,
            page_size=page_size,
            next_page=next_page,
            drive_id=drive_id,
            path=path,
            id=id,
        )

    async def curated_file_and_folder_async(
        self,
        *,
        page_size: Optional[int] = None,
        next_page: Optional[str] = None,
        drive_id: Optional[str] = None,
        path: Optional[str] = None,
        id: Optional[str] = None,
    ) -> Optional[Union[DefaultError, list["CuratedFileAndFolder"]]]:
        return await _curated_file_and_folder_async(
            client=self.client,
            page_size=page_size,
            next_page=next_page,
            drive_id=drive_id,
            path=path,
            id=id,
        )

    def get_file_folder(
        self,
        id: str,
        *,
        drive_id: Optional[str] = None,
    ) -> Optional[Union[DefaultError, GetFileFolderResponse]]:
        return _get_file_folder(
            client=self.client,
            id=id,
            drive_id=drive_id,
        )

    async def get_file_folder_async(
        self,
        id: str,
        *,
        drive_id: Optional[str] = None,
    ) -> Optional[Union[DefaultError, GetFileFolderResponse]]:
        return await _get_file_folder_async(
            client=self.client,
            id=id,
            drive_id=drive_id,
        )

    def delete_column(
        self,
        *,
        body: DeleteColumnRequest,
        reference_id: str,
        reference_id_lookup: Any,
        has_headers: bool = False,
        range_: str,
        column_position: str,
    ) -> Optional[Union[Any, DefaultError]]:
        return _delete_column(
            client=self.client,
            body=body,
            reference_id=reference_id,
            reference_id_lookup=reference_id_lookup,
            has_headers=has_headers,
            range_=range_,
            column_position=column_position,
        )

    async def delete_column_async(
        self,
        *,
        body: DeleteColumnRequest,
        reference_id: str,
        reference_id_lookup: Any,
        has_headers: bool = False,
        range_: str,
        column_position: str,
    ) -> Optional[Union[Any, DefaultError]]:
        return await _delete_column_async(
            client=self.client,
            body=body,
            reference_id=reference_id,
            reference_id_lookup=reference_id_lookup,
            has_headers=has_headers,
            range_=range_,
            column_position=column_position,
        )

    def delete_file_folder(
        self,
        *,
        reference_id: str,
        reference_id_lookup: Any,
    ) -> Optional[Union[Any, DefaultError]]:
        return _delete_file_folder(
            client=self.client,
            reference_id=reference_id,
            reference_id_lookup=reference_id_lookup,
        )

    async def delete_file_folder_async(
        self,
        *,
        reference_id: str,
        reference_id_lookup: Any,
    ) -> Optional[Union[Any, DefaultError]]:
        return await _delete_file_folder_async(
            client=self.client,
            reference_id=reference_id,
            reference_id_lookup=reference_id_lookup,
        )

    def delete_range(
        self,
        *,
        body: DeleteRangeRequest,
        range_: str,
        reference_id: str,
        reference_id_lookup: Any,
    ) -> Optional[Union[Any, DefaultError]]:
        return _delete_range(
            client=self.client,
            body=body,
            range_=range_,
            reference_id=reference_id,
            reference_id_lookup=reference_id_lookup,
        )

    async def delete_range_async(
        self,
        *,
        body: DeleteRangeRequest,
        range_: str,
        reference_id: str,
        reference_id_lookup: Any,
    ) -> Optional[Union[Any, DefaultError]]:
        return await _delete_range_async(
            client=self.client,
            body=body,
            range_=range_,
            reference_id=reference_id,
            reference_id_lookup=reference_id_lookup,
        )

    def delete_row(
        self,
        *,
        body: DeleteRowRequest,
        range_: str,
        reference_id: str,
        reference_id_lookup: Any,
        row: str,
    ) -> Optional[Union[Any, DefaultError]]:
        return _delete_row(
            client=self.client,
            body=body,
            range_=range_,
            reference_id=reference_id,
            reference_id_lookup=reference_id_lookup,
            row=row,
        )

    async def delete_row_async(
        self,
        *,
        body: DeleteRowRequest,
        range_: str,
        reference_id: str,
        reference_id_lookup: Any,
        row: str,
    ) -> Optional[Union[Any, DefaultError]]:
        return await _delete_row_async(
            client=self.client,
            body=body,
            range_=range_,
            reference_id=reference_id,
            reference_id_lookup=reference_id_lookup,
            row=row,
        )

    def delete_sheet(
        self,
        id: str,
        *,
        reference_id: str,
        reference_id_lookup: Any,
    ) -> Optional[Union[Any, DefaultError]]:
        return _delete_sheet(
            client=self.client,
            id=id,
            reference_id=reference_id,
            reference_id_lookup=reference_id_lookup,
        )

    async def delete_sheet_async(
        self,
        id: str,
        *,
        reference_id: str,
        reference_id_lookup: Any,
    ) -> Optional[Union[Any, DefaultError]]:
        return await _delete_sheet_async(
            client=self.client,
            id=id,
            reference_id=reference_id,
            reference_id_lookup=reference_id_lookup,
        )

    def download_file(
        self,
        *,
        convert_to_pdf: Optional[bool] = False,
        reference_id: str,
        reference_id_lookup: Any,
    ) -> Optional[Union[DefaultError, File]]:
        return _download_file(
            client=self.client,
            convert_to_pdf=convert_to_pdf,
            reference_id=reference_id,
            reference_id_lookup=reference_id_lookup,
        )

    async def download_file_async(
        self,
        *,
        convert_to_pdf: Optional[bool] = False,
        reference_id: str,
        reference_id_lookup: Any,
    ) -> Optional[Union[DefaultError, File]]:
        return await _download_file_async(
            client=self.client,
            convert_to_pdf=convert_to_pdf,
            reference_id=reference_id,
            reference_id_lookup=reference_id_lookup,
        )

    def file_checkin_check_out(
        self,
        *,
        body: FileCheckinCheckOutRequest,
        reference_id: str,
        reference_id_lookup: Any,
        action: str,
    ) -> Optional[Union[Any, DefaultError]]:
        return _file_checkin_check_out(
            client=self.client,
            body=body,
            reference_id=reference_id,
            reference_id_lookup=reference_id_lookup,
            action=action,
        )

    async def file_checkin_check_out_async(
        self,
        *,
        body: FileCheckinCheckOutRequest,
        reference_id: str,
        reference_id_lookup: Any,
        action: str,
    ) -> Optional[Union[Any, DefaultError]]:
        return await _file_checkin_check_out_async(
            client=self.client,
            body=body,
            reference_id=reference_id,
            reference_id_lookup=reference_id_lookup,
            action=action,
        )

    def file_upload_v2(
        self,
        *,
        body: FileUploadV2Body,
        conflict_behavior: Optional[str] = None,
        reference_id: str,
        reference_id_lookup: Any,
    ) -> Optional[Union[DefaultError, FileUploadV2Response]]:
        return _file_upload_v2(
            client=self.client,
            body=body,
            conflict_behavior=conflict_behavior,
            reference_id=reference_id,
            reference_id_lookup=reference_id_lookup,
        )

    async def file_upload_v2_async(
        self,
        *,
        body: FileUploadV2Body,
        conflict_behavior: Optional[str] = None,
        reference_id: str,
        reference_id_lookup: Any,
    ) -> Optional[Union[DefaultError, FileUploadV2Response]]:
        return await _file_upload_v2_async(
            client=self.client,
            body=body,
            conflict_behavior=conflict_behavior,
            reference_id=reference_id,
            reference_id_lookup=reference_id_lookup,
        )

    def get_file_folder_metadata(
        self,
        reference_id: str,
        reference_id_lookup: Any,
    ) -> Optional[Union[DefaultError, GetFileFolderMetadataResponse]]:
        return _get_file_folder_metadata(
            client=self.client,
            reference_id=reference_id,
            reference_id_lookup=reference_id_lookup,
        )

    async def get_file_folder_metadata_async(
        self,
        reference_id: str,
        reference_id_lookup: Any,
    ) -> Optional[Union[DefaultError, GetFileFolderMetadataResponse]]:
        return await _get_file_folder_metadata_async(
            client=self.client,
            reference_id=reference_id,
            reference_id_lookup=reference_id_lookup,
        )

    def get_files_folders(
        self,
        id: str,
        id_lookup: Any,
    ) -> Optional[Union[DefaultError, GetFilesFoldersResponse]]:
        return _get_files_folders(
            client=self.client,
            id=id,
            id_lookup=id_lookup,
        )

    async def get_files_folders_async(
        self,
        id: str,
        id_lookup: Any,
    ) -> Optional[Union[DefaultError, GetFilesFoldersResponse]]:
        return await _get_files_folders_async(
            client=self.client,
            id=id,
            id_lookup=id_lookup,
        )

    def get_files_folders_list(
        self,
        *,
        reference_id: str,
        reference_id_lookup: Any,
        return_: Optional[str] = None,
    ) -> Optional[Union[DefaultError, list["GetFilesFoldersList"]]]:
        return _get_files_folders_list(
            client=self.client,
            reference_id=reference_id,
            reference_id_lookup=reference_id_lookup,
            return_=return_,
        )

    async def get_files_folders_list_async(
        self,
        *,
        reference_id: str,
        reference_id_lookup: Any,
        return_: Optional[str] = None,
    ) -> Optional[Union[DefaultError, list["GetFilesFoldersList"]]]:
        return await _get_files_folders_list_async(
            client=self.client,
            reference_id=reference_id,
            reference_id_lookup=reference_id_lookup,
            return_=return_,
        )

    def move_file_folder(
        self,
        *,
        body: MoveFileFolderRequest,
        conflict_behavior: Optional[str] = None,
        reference_folder_id: str,
        reference_folder_id_lookup: Any,
    ) -> Optional[Union[DefaultError, MoveFileFolderResponse]]:
        return _move_file_folder(
            client=self.client,
            body=body,
            conflict_behavior=conflict_behavior,
            reference_folder_id=reference_folder_id,
            reference_folder_id_lookup=reference_folder_id_lookup,
        )

    async def move_file_folder_async(
        self,
        *,
        body: MoveFileFolderRequest,
        conflict_behavior: Optional[str] = None,
        reference_folder_id: str,
        reference_folder_id_lookup: Any,
    ) -> Optional[Union[DefaultError, MoveFileFolderResponse]]:
        return await _move_file_folder_async(
            client=self.client,
            body=body,
            conflict_behavior=conflict_behavior,
            reference_folder_id=reference_folder_id,
            reference_folder_id_lookup=reference_folder_id_lookup,
        )

    def read_cell(
        self,
        *,
        worksheet_id: str,
        read: Optional[str] = None,
        reference_id: str,
        reference_id_lookup: Any,
        cell_address: str,
    ) -> Optional[Union[DefaultError, list["ReadCell"]]]:
        return _read_cell(
            client=self.client,
            worksheet_id=worksheet_id,
            read=read,
            reference_id=reference_id,
            reference_id_lookup=reference_id_lookup,
            cell_address=cell_address,
        )

    async def read_cell_async(
        self,
        *,
        worksheet_id: str,
        read: Optional[str] = None,
        reference_id: str,
        reference_id_lookup: Any,
        cell_address: str,
    ) -> Optional[Union[DefaultError, list["ReadCell"]]]:
        return await _read_cell_async(
            client=self.client,
            worksheet_id=worksheet_id,
            read=read,
            reference_id=reference_id,
            reference_id_lookup=reference_id_lookup,
            cell_address=cell_address,
        )

    def read_range(
        self,
        *,
        reference_id: str,
        reference_id_lookup: Any,
        range_: str,
        read: Optional[str] = None,
    ) -> Optional[Union[DefaultError, list["ReadRange"]]]:
        return _read_range(
            client=self.client,
            reference_id=reference_id,
            reference_id_lookup=reference_id_lookup,
            range_=range_,
            read=read,
        )

    async def read_range_async(
        self,
        *,
        reference_id: str,
        reference_id_lookup: Any,
        range_: str,
        read: Optional[str] = None,
    ) -> Optional[Union[DefaultError, list["ReadRange"]]]:
        return await _read_range_async(
            client=self.client,
            reference_id=reference_id,
            reference_id_lookup=reference_id_lookup,
            range_=range_,
            read=read,
        )

    def rename_sheet(
        self,
        id: str,
        *,
        body: RenameSheetRequest,
        reference_id: str,
        reference_id_lookup: Any,
    ) -> Optional[Union[DefaultError, RenameSheetResponse]]:
        return _rename_sheet(
            client=self.client,
            id=id,
            body=body,
            reference_id=reference_id,
            reference_id_lookup=reference_id_lookup,
        )

    async def rename_sheet_async(
        self,
        id: str,
        *,
        body: RenameSheetRequest,
        reference_id: str,
        reference_id_lookup: Any,
    ) -> Optional[Union[DefaultError, RenameSheetResponse]]:
        return await _rename_sheet_async(
            client=self.client,
            id=id,
            body=body,
            reference_id=reference_id,
            reference_id_lookup=reference_id_lookup,
        )

    def share_file_or_folder(
        self,
        *,
        body: ShareFileOrFolderRequest,
        reference_id: str,
        reference_id_lookup: Any,
    ) -> Optional[Union[DefaultError, ShareFileOrFolderResponse]]:
        return _share_file_or_folder(
            client=self.client,
            body=body,
            reference_id=reference_id,
            reference_id_lookup=reference_id_lookup,
        )

    async def share_file_or_folder_async(
        self,
        *,
        body: ShareFileOrFolderRequest,
        reference_id: str,
        reference_id_lookup: Any,
    ) -> Optional[Union[DefaultError, ShareFileOrFolderResponse]]:
        return await _share_file_or_folder_async(
            client=self.client,
            body=body,
            reference_id=reference_id,
            reference_id_lookup=reference_id_lookup,
        )

    def write_cell(
        self,
        *,
        body: WriteCellRequest,
        reference_id: str,
        reference_id_lookup: Any,
        cell_address: str,
        worksheet_id: str,
    ) -> Optional[Union[Any, DefaultError]]:
        return _write_cell(
            client=self.client,
            body=body,
            reference_id=reference_id,
            reference_id_lookup=reference_id_lookup,
            cell_address=cell_address,
            worksheet_id=worksheet_id,
        )

    async def write_cell_async(
        self,
        *,
        body: WriteCellRequest,
        reference_id: str,
        reference_id_lookup: Any,
        cell_address: str,
        worksheet_id: str,
    ) -> Optional[Union[Any, DefaultError]]:
        return await _write_cell_async(
            client=self.client,
            body=body,
            reference_id=reference_id,
            reference_id_lookup=reference_id_lookup,
            cell_address=cell_address,
            worksheet_id=worksheet_id,
        )

    def write_column(
        self,
        *,
        body: WriteColumnRequest,
        reference_id: str,
        reference_id_lookup: Any,
        include_headers: Optional[bool] = True,
        range_: str,
    ) -> Optional[Union[Any, DefaultError]]:
        return _write_column(
            client=self.client,
            body=body,
            reference_id=reference_id,
            reference_id_lookup=reference_id_lookup,
            include_headers=include_headers,
            range_=range_,
        )

    async def write_column_async(
        self,
        *,
        body: WriteColumnRequest,
        reference_id: str,
        reference_id_lookup: Any,
        include_headers: Optional[bool] = True,
        range_: str,
    ) -> Optional[Union[Any, DefaultError]]:
        return await _write_column_async(
            client=self.client,
            body=body,
            reference_id=reference_id,
            reference_id_lookup=reference_id_lookup,
            include_headers=include_headers,
            range_=range_,
        )

    def write_range(
        self,
        *,
        body: WriteRangeRequest,
        range_: str,
        reference_id: str,
        reference_id_lookup: Any,
        include_headers: Optional[bool] = True,
    ) -> Optional[Union[Any, DefaultError]]:
        return _write_range(
            client=self.client,
            body=body,
            range_=range_,
            reference_id=reference_id,
            reference_id_lookup=reference_id_lookup,
            include_headers=include_headers,
        )

    async def write_range_async(
        self,
        *,
        body: WriteRangeRequest,
        range_: str,
        reference_id: str,
        reference_id_lookup: Any,
        include_headers: Optional[bool] = True,
    ) -> Optional[Union[Any, DefaultError]]:
        return await _write_range_async(
            client=self.client,
            body=body,
            range_=range_,
            reference_id=reference_id,
            reference_id_lookup=reference_id_lookup,
            include_headers=include_headers,
        )

    def write_row(
        self,
        *,
        body: WriteRowRequest,
        reference_id: str,
        reference_id_lookup: Any,
        range_: str,
        include_headers: Optional[bool] = True,
    ) -> Optional[Union[Any, DefaultError]]:
        return _write_row(
            client=self.client,
            body=body,
            reference_id=reference_id,
            reference_id_lookup=reference_id_lookup,
            range_=range_,
            include_headers=include_headers,
        )

    async def write_row_async(
        self,
        *,
        body: WriteRowRequest,
        reference_id: str,
        reference_id_lookup: Any,
        range_: str,
        include_headers: Optional[bool] = True,
    ) -> Optional[Union[Any, DefaultError]]:
        return await _write_row_async(
            client=self.client,
            body=body,
            reference_id=reference_id,
            reference_id_lookup=reference_id_lookup,
            range_=range_,
            include_headers=include_headers,
        )
