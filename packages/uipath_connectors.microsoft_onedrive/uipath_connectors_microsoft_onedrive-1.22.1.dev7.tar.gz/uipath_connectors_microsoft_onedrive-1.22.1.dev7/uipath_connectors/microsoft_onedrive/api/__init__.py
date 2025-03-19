from .get_files_folders import (
    get_files_folders_list as _get_files_folders_list,
    get_files_folders_list_async as _get_files_folders_list_async,
    get_files_folders as _get_files_folders,
    get_files_folders_async as _get_files_folders_async,
)
from ..models.default_error import DefaultError
from ..models.get_files_folders_list import GetFilesFoldersList
from typing import cast
from ..models.get_files_folders_response import GetFilesFoldersResponse
from .read_range import (
    read_range as _read_range,
    read_range_async as _read_range_async,
)
from ..models.read_range import ReadRange
from .file_upload_v2 import (
    file_upload_v2 as _file_upload_v2,
    file_upload_v2_async as _file_upload_v2_async,
)
from ..models.file_upload_v2_response import FileUploadV2Response
from .move_file_folder import (
    move_file_folder as _move_file_folder,
    move_file_folder_async as _move_file_folder_async,
)
from ..models.move_file_folder_request import MoveFileFolderRequest
from ..models.move_file_folder_response import MoveFileFolderResponse
from .write_range import (
    write_range as _write_range,
    write_range_async as _write_range_async,
)
from ..models.write_range_request import WriteRangeRequest
from .create_folder import (
    create_folder as _create_folder,
    create_folder_async as _create_folder_async,
)
from ..models.create_folder_request import CreateFolderRequest
from ..models.create_folder_response import CreateFolderResponse
from .file_checkin_check_out import (
    file_checkin_check_out as _file_checkin_check_out,
    file_checkin_check_out_async as _file_checkin_check_out_async,
)
from ..models.file_checkin_check_out_request import FileCheckinCheckOutRequest
from .download_file import (
    download_file as _download_file,
    download_file_async as _download_file_async,
)
from .curated_file_and_folder import (
    get_curated_file_and_folders as _get_curated_file_and_folders,
    get_curated_file_and_folders_async as _get_curated_file_and_folders_async,
    get_file_folder as _get_file_folder,
    get_file_folder_async as _get_file_folder_async,
)
from ..models.get_curated_file_and_folders import GetCuratedFileAndFolders
from ..models.get_file_folder_response import GetFileFolderResponse
from .write_cell import (
    write_cell as _write_cell,
    write_cell_async as _write_cell_async,
)
from ..models.write_cell_request import WriteCellRequest
from .create_workbook import (
    create_workbook as _create_workbook,
    create_workbook_async as _create_workbook_async,
)
from ..models.create_workbook_request import CreateWorkbookRequest
from ..models.create_workbook_response import CreateWorkbookResponse
from .write_column import (
    write_column as _write_column,
    write_column_async as _write_column_async,
)
from ..models.write_column_request import WriteColumnRequest
from .delete_range import (
    delete_range as _delete_range,
    delete_range_async as _delete_range_async,
)
from ..models.delete_range_request import DeleteRangeRequest
from .curated_file import (
    get_curated_files as _get_curated_files,
    get_curated_files_async as _get_curated_files_async,
    get_file_list as _get_file_list,
    get_file_list_async as _get_file_list_async,
)
from ..models.get_curated_files import GetCuratedFiles
from ..models.get_file_list_response import GetFileListResponse
from .delete_row import (
    delete_row as _delete_row,
    delete_row_async as _delete_row_async,
)
from ..models.delete_row_request import DeleteRowRequest
from .write_row import (
    write_row as _write_row,
    write_row_async as _write_row_async,
)
from ..models.write_row_request import WriteRowRequest
from .add_sheet import (
    add_sheet as _add_sheet,
    add_sheet_async as _add_sheet_async,
)
from ..models.add_sheet_request import AddSheetRequest
from ..models.add_sheet_response import AddSheetResponse
from .copy_file_folder import (
    copy_file_folder as _copy_file_folder,
    copy_file_folder_async as _copy_file_folder_async,
)
from ..models.copy_file_folder_request import CopyFileFolderRequest
from ..models.copy_file_folder_response import CopyFileFolderResponse
from .share_file_or_folder import (
    share_file_or_folder as _share_file_or_folder,
    share_file_or_folder_async as _share_file_or_folder_async,
)
from ..models.share_file_or_folder_request import ShareFileOrFolderRequest
from ..models.share_file_or_folder_response import ShareFileOrFolderResponse
from .read_cell import (
    read_cell as _read_cell,
    read_cell_async as _read_cell_async,
)
from ..models.read_cell import ReadCell
from .delete_column import (
    delete_column as _delete_column,
    delete_column_async as _delete_column_async,
)
from ..models.delete_column_request import DeleteColumnRequest
from .delete_sheet import (
    delete_sheet as _delete_sheet,
    delete_sheet_async as _delete_sheet_async,
)
from .delete_file_folder import (
    delete_file_folder as _delete_file_folder,
    delete_file_folder_async as _delete_file_folder_async,
)
from .get_file_folder_metadata import (
    get_file_folder_metadata as _get_file_folder_metadata,
    get_file_folder_metadata_async as _get_file_folder_metadata_async,
)
from ..models.get_file_folder_metadata_response import GetFileFolderMetadataResponse
from .rename_sheet import (
    rename_sheet as _rename_sheet,
    rename_sheet_async as _rename_sheet_async,
)
from ..models.rename_sheet_request import RenameSheetRequest
from ..models.rename_sheet_response import RenameSheetResponse
from .create_share_link import (
    create_create_share_link as _create_create_share_link,
    create_create_share_link_async as _create_create_share_link_async,
)
from ..models.create_create_share_link_request import CreateCreateShareLinkRequest
from ..models.create_create_share_link_response import CreateCreateShareLinkResponse

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

    def get_files_folders_list(
        self,
        *,
        reference_id: str,
        reference_id_lookup: Any,
        fields: Optional[str] = None,
        fields_lookup: Any,
        next_page: Optional[str] = None,
        next_page_lookup: Any,
        page_size: Optional[int] = None,
        page_size_lookup: Any,
        return_: Optional[str] = None,
        return__lookup: Any,
    ) -> Optional[Union[DefaultError, list["GetFilesFoldersList"]]]:
        return _get_files_folders_list(
            client=self.client,
            reference_id=reference_id,
            reference_id_lookup=reference_id_lookup,
            fields=fields,
            fields_lookup=fields_lookup,
            next_page=next_page,
            next_page_lookup=next_page_lookup,
            page_size=page_size,
            page_size_lookup=page_size_lookup,
            return_=return_,
            return__lookup=return__lookup,
        )

    async def get_files_folders_list_async(
        self,
        *,
        reference_id: str,
        reference_id_lookup: Any,
        fields: Optional[str] = None,
        fields_lookup: Any,
        next_page: Optional[str] = None,
        next_page_lookup: Any,
        page_size: Optional[int] = None,
        page_size_lookup: Any,
        return_: Optional[str] = None,
        return__lookup: Any,
    ) -> Optional[Union[DefaultError, list["GetFilesFoldersList"]]]:
        return await _get_files_folders_list_async(
            client=self.client,
            reference_id=reference_id,
            reference_id_lookup=reference_id_lookup,
            fields=fields,
            fields_lookup=fields_lookup,
            next_page=next_page,
            next_page_lookup=next_page_lookup,
            page_size=page_size,
            page_size_lookup=page_size_lookup,
            return_=return_,
            return__lookup=return__lookup,
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

    def read_range(
        self,
        *,
        range_: str,
        range__lookup: Any,
        reference_id: str,
        reference_id_lookup: Any,
        fields: Optional[str] = None,
        fields_lookup: Any,
        next_page: Optional[str] = None,
        next_page_lookup: Any,
        page_size: Optional[int] = None,
        page_size_lookup: Any,
        read: Optional[str] = None,
        read_lookup: Any,
    ) -> Optional[Union[DefaultError, list["ReadRange"]]]:
        return _read_range(
            client=self.client,
            range_=range_,
            range__lookup=range__lookup,
            reference_id=reference_id,
            reference_id_lookup=reference_id_lookup,
            fields=fields,
            fields_lookup=fields_lookup,
            next_page=next_page,
            next_page_lookup=next_page_lookup,
            page_size=page_size,
            page_size_lookup=page_size_lookup,
            read=read,
            read_lookup=read_lookup,
        )

    async def read_range_async(
        self,
        *,
        range_: str,
        range__lookup: Any,
        reference_id: str,
        reference_id_lookup: Any,
        fields: Optional[str] = None,
        fields_lookup: Any,
        next_page: Optional[str] = None,
        next_page_lookup: Any,
        page_size: Optional[int] = None,
        page_size_lookup: Any,
        read: Optional[str] = None,
        read_lookup: Any,
    ) -> Optional[Union[DefaultError, list["ReadRange"]]]:
        return await _read_range_async(
            client=self.client,
            range_=range_,
            range__lookup=range__lookup,
            reference_id=reference_id,
            reference_id_lookup=reference_id_lookup,
            fields=fields,
            fields_lookup=fields_lookup,
            next_page=next_page,
            next_page_lookup=next_page_lookup,
            page_size=page_size,
            page_size_lookup=page_size_lookup,
            read=read,
            read_lookup=read_lookup,
        )

    def file_upload_v2(
        self,
        *,
        conflict_behavior: Optional[str] = None,
        conflict_behavior_lookup: Any,
        reference_id: str,
        reference_id_lookup: Any,
    ) -> Optional[Union[DefaultError, FileUploadV2Response]]:
        return _file_upload_v2(
            client=self.client,
            conflict_behavior=conflict_behavior,
            conflict_behavior_lookup=conflict_behavior_lookup,
            reference_id=reference_id,
            reference_id_lookup=reference_id_lookup,
        )

    async def file_upload_v2_async(
        self,
        *,
        conflict_behavior: Optional[str] = None,
        conflict_behavior_lookup: Any,
        reference_id: str,
        reference_id_lookup: Any,
    ) -> Optional[Union[DefaultError, FileUploadV2Response]]:
        return await _file_upload_v2_async(
            client=self.client,
            conflict_behavior=conflict_behavior,
            conflict_behavior_lookup=conflict_behavior_lookup,
            reference_id=reference_id,
            reference_id_lookup=reference_id_lookup,
        )

    def move_file_folder(
        self,
        *,
        body: MoveFileFolderRequest,
        reference_folder_id: str,
        reference_folder_id_lookup: Any,
        conflict_behavior: Optional[str] = None,
        conflict_behavior_lookup: Any,
    ) -> Optional[Union[DefaultError, MoveFileFolderResponse]]:
        return _move_file_folder(
            client=self.client,
            body=body,
            reference_folder_id=reference_folder_id,
            reference_folder_id_lookup=reference_folder_id_lookup,
            conflict_behavior=conflict_behavior,
            conflict_behavior_lookup=conflict_behavior_lookup,
        )

    async def move_file_folder_async(
        self,
        *,
        body: MoveFileFolderRequest,
        reference_folder_id: str,
        reference_folder_id_lookup: Any,
        conflict_behavior: Optional[str] = None,
        conflict_behavior_lookup: Any,
    ) -> Optional[Union[DefaultError, MoveFileFolderResponse]]:
        return await _move_file_folder_async(
            client=self.client,
            body=body,
            reference_folder_id=reference_folder_id,
            reference_folder_id_lookup=reference_folder_id_lookup,
            conflict_behavior=conflict_behavior,
            conflict_behavior_lookup=conflict_behavior_lookup,
        )

    def write_range(
        self,
        *,
        body: WriteRangeRequest,
        range_: str,
        range__lookup: Any,
        reference_id: str,
        reference_id_lookup: Any,
        include_headers: Optional[bool] = True,
        include_headers_lookup: Any,
    ) -> Optional[Union[Any, DefaultError]]:
        return _write_range(
            client=self.client,
            body=body,
            range_=range_,
            range__lookup=range__lookup,
            reference_id=reference_id,
            reference_id_lookup=reference_id_lookup,
            include_headers=include_headers,
            include_headers_lookup=include_headers_lookup,
        )

    async def write_range_async(
        self,
        *,
        body: WriteRangeRequest,
        range_: str,
        range__lookup: Any,
        reference_id: str,
        reference_id_lookup: Any,
        include_headers: Optional[bool] = True,
        include_headers_lookup: Any,
    ) -> Optional[Union[Any, DefaultError]]:
        return await _write_range_async(
            client=self.client,
            body=body,
            range_=range_,
            range__lookup=range__lookup,
            reference_id=reference_id,
            reference_id_lookup=reference_id_lookup,
            include_headers=include_headers,
            include_headers_lookup=include_headers_lookup,
        )

    def create_folder(
        self,
        *,
        body: CreateFolderRequest,
        conflict_behavior: Optional[str] = None,
        conflict_behavior_lookup: Any,
    ) -> Optional[Union[CreateFolderResponse, DefaultError]]:
        return _create_folder(
            client=self.client,
            body=body,
            conflict_behavior=conflict_behavior,
            conflict_behavior_lookup=conflict_behavior_lookup,
        )

    async def create_folder_async(
        self,
        *,
        body: CreateFolderRequest,
        conflict_behavior: Optional[str] = None,
        conflict_behavior_lookup: Any,
    ) -> Optional[Union[CreateFolderResponse, DefaultError]]:
        return await _create_folder_async(
            client=self.client,
            body=body,
            conflict_behavior=conflict_behavior,
            conflict_behavior_lookup=conflict_behavior_lookup,
        )

    def file_checkin_check_out(
        self,
        *,
        body: FileCheckinCheckOutRequest,
        reference_id: str,
        reference_id_lookup: Any,
        action: str,
        action_lookup: Any,
    ) -> Optional[Union[Any, DefaultError]]:
        return _file_checkin_check_out(
            client=self.client,
            body=body,
            reference_id=reference_id,
            reference_id_lookup=reference_id_lookup,
            action=action,
            action_lookup=action_lookup,
        )

    async def file_checkin_check_out_async(
        self,
        *,
        body: FileCheckinCheckOutRequest,
        reference_id: str,
        reference_id_lookup: Any,
        action: str,
        action_lookup: Any,
    ) -> Optional[Union[Any, DefaultError]]:
        return await _file_checkin_check_out_async(
            client=self.client,
            body=body,
            reference_id=reference_id,
            reference_id_lookup=reference_id_lookup,
            action=action,
            action_lookup=action_lookup,
        )

    def download_file(
        self,
        *,
        reference_id: str,
        reference_id_lookup: Any,
        convert_to_pdf: Optional[bool] = False,
        convert_to_pdf_lookup: Any,
    ) -> Optional[Union[Any, DefaultError]]:
        return _download_file(
            client=self.client,
            reference_id=reference_id,
            reference_id_lookup=reference_id_lookup,
            convert_to_pdf=convert_to_pdf,
            convert_to_pdf_lookup=convert_to_pdf_lookup,
        )

    async def download_file_async(
        self,
        *,
        reference_id: str,
        reference_id_lookup: Any,
        convert_to_pdf: Optional[bool] = False,
        convert_to_pdf_lookup: Any,
    ) -> Optional[Union[Any, DefaultError]]:
        return await _download_file_async(
            client=self.client,
            reference_id=reference_id,
            reference_id_lookup=reference_id_lookup,
            convert_to_pdf=convert_to_pdf,
            convert_to_pdf_lookup=convert_to_pdf_lookup,
        )

    def get_curated_file_and_folders(
        self,
        *,
        drive_id: Optional[str] = None,
        drive_id_lookup: Any,
        fields: Optional[str] = None,
        fields_lookup: Any,
        id: Optional[str] = None,
        id_lookup: Any,
        next_page: Optional[str] = None,
        next_page_lookup: Any,
        page_size: Optional[int] = None,
        page_size_lookup: Any,
        path: Optional[str] = None,
        path_lookup: Any,
    ) -> Optional[Union[DefaultError, list["GetCuratedFileAndFolders"]]]:
        return _get_curated_file_and_folders(
            client=self.client,
            drive_id=drive_id,
            drive_id_lookup=drive_id_lookup,
            fields=fields,
            fields_lookup=fields_lookup,
            id=id,
            id_lookup=id_lookup,
            next_page=next_page,
            next_page_lookup=next_page_lookup,
            page_size=page_size,
            page_size_lookup=page_size_lookup,
            path=path,
            path_lookup=path_lookup,
        )

    async def get_curated_file_and_folders_async(
        self,
        *,
        drive_id: Optional[str] = None,
        drive_id_lookup: Any,
        fields: Optional[str] = None,
        fields_lookup: Any,
        id: Optional[str] = None,
        id_lookup: Any,
        next_page: Optional[str] = None,
        next_page_lookup: Any,
        page_size: Optional[int] = None,
        page_size_lookup: Any,
        path: Optional[str] = None,
        path_lookup: Any,
    ) -> Optional[Union[DefaultError, list["GetCuratedFileAndFolders"]]]:
        return await _get_curated_file_and_folders_async(
            client=self.client,
            drive_id=drive_id,
            drive_id_lookup=drive_id_lookup,
            fields=fields,
            fields_lookup=fields_lookup,
            id=id,
            id_lookup=id_lookup,
            next_page=next_page,
            next_page_lookup=next_page_lookup,
            page_size=page_size,
            page_size_lookup=page_size_lookup,
            path=path,
            path_lookup=path_lookup,
        )

    def get_file_folder(
        self,
        id: str,
        id_lookup: Any,
        *,
        drive_id: Optional[str] = None,
        drive_id_lookup: Any,
    ) -> Optional[Union[DefaultError, GetFileFolderResponse]]:
        return _get_file_folder(
            client=self.client,
            id=id,
            id_lookup=id_lookup,
            drive_id=drive_id,
            drive_id_lookup=drive_id_lookup,
        )

    async def get_file_folder_async(
        self,
        id: str,
        id_lookup: Any,
        *,
        drive_id: Optional[str] = None,
        drive_id_lookup: Any,
    ) -> Optional[Union[DefaultError, GetFileFolderResponse]]:
        return await _get_file_folder_async(
            client=self.client,
            id=id,
            id_lookup=id_lookup,
            drive_id=drive_id,
            drive_id_lookup=drive_id_lookup,
        )

    def write_cell(
        self,
        *,
        body: WriteCellRequest,
        cell_address: str,
        cell_address_lookup: Any,
        reference_id: str,
        reference_id_lookup: Any,
        worksheet_id: str,
        worksheet_id_lookup: Any,
    ) -> Optional[Union[Any, DefaultError]]:
        return _write_cell(
            client=self.client,
            body=body,
            cell_address=cell_address,
            cell_address_lookup=cell_address_lookup,
            reference_id=reference_id,
            reference_id_lookup=reference_id_lookup,
            worksheet_id=worksheet_id,
            worksheet_id_lookup=worksheet_id_lookup,
        )

    async def write_cell_async(
        self,
        *,
        body: WriteCellRequest,
        cell_address: str,
        cell_address_lookup: Any,
        reference_id: str,
        reference_id_lookup: Any,
        worksheet_id: str,
        worksheet_id_lookup: Any,
    ) -> Optional[Union[Any, DefaultError]]:
        return await _write_cell_async(
            client=self.client,
            body=body,
            cell_address=cell_address,
            cell_address_lookup=cell_address_lookup,
            reference_id=reference_id,
            reference_id_lookup=reference_id_lookup,
            worksheet_id=worksheet_id,
            worksheet_id_lookup=worksheet_id_lookup,
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

    def write_column(
        self,
        *,
        body: WriteColumnRequest,
        reference_id: str,
        reference_id_lookup: Any,
        include_headers: Optional[bool] = True,
        include_headers_lookup: Any,
        range_: str,
        range__lookup: Any,
    ) -> Optional[Union[Any, DefaultError]]:
        return _write_column(
            client=self.client,
            body=body,
            reference_id=reference_id,
            reference_id_lookup=reference_id_lookup,
            include_headers=include_headers,
            include_headers_lookup=include_headers_lookup,
            range_=range_,
            range__lookup=range__lookup,
        )

    async def write_column_async(
        self,
        *,
        body: WriteColumnRequest,
        reference_id: str,
        reference_id_lookup: Any,
        include_headers: Optional[bool] = True,
        include_headers_lookup: Any,
        range_: str,
        range__lookup: Any,
    ) -> Optional[Union[Any, DefaultError]]:
        return await _write_column_async(
            client=self.client,
            body=body,
            reference_id=reference_id,
            reference_id_lookup=reference_id_lookup,
            include_headers=include_headers,
            include_headers_lookup=include_headers_lookup,
            range_=range_,
            range__lookup=range__lookup,
        )

    def delete_range(
        self,
        *,
        body: DeleteRangeRequest,
        range_: str,
        range__lookup: Any,
        reference_id: str,
        reference_id_lookup: Any,
    ) -> Optional[Union[Any, DefaultError]]:
        return _delete_range(
            client=self.client,
            body=body,
            range_=range_,
            range__lookup=range__lookup,
            reference_id=reference_id,
            reference_id_lookup=reference_id_lookup,
        )

    async def delete_range_async(
        self,
        *,
        body: DeleteRangeRequest,
        range_: str,
        range__lookup: Any,
        reference_id: str,
        reference_id_lookup: Any,
    ) -> Optional[Union[Any, DefaultError]]:
        return await _delete_range_async(
            client=self.client,
            body=body,
            range_=range_,
            range__lookup=range__lookup,
            reference_id=reference_id,
            reference_id_lookup=reference_id_lookup,
        )

    def get_curated_files(
        self,
        *,
        drive_id: Optional[str] = None,
        drive_id_lookup: Any,
        fields: Optional[str] = None,
        fields_lookup: Any,
        id: Optional[str] = None,
        id_lookup: Any,
        next_page: Optional[str] = None,
        next_page_lookup: Any,
        page_size: Optional[int] = None,
        page_size_lookup: Any,
        path: Optional[str] = None,
        path_lookup: Any,
    ) -> Optional[Union[DefaultError, list["GetCuratedFiles"]]]:
        return _get_curated_files(
            client=self.client,
            drive_id=drive_id,
            drive_id_lookup=drive_id_lookup,
            fields=fields,
            fields_lookup=fields_lookup,
            id=id,
            id_lookup=id_lookup,
            next_page=next_page,
            next_page_lookup=next_page_lookup,
            page_size=page_size,
            page_size_lookup=page_size_lookup,
            path=path,
            path_lookup=path_lookup,
        )

    async def get_curated_files_async(
        self,
        *,
        drive_id: Optional[str] = None,
        drive_id_lookup: Any,
        fields: Optional[str] = None,
        fields_lookup: Any,
        id: Optional[str] = None,
        id_lookup: Any,
        next_page: Optional[str] = None,
        next_page_lookup: Any,
        page_size: Optional[int] = None,
        page_size_lookup: Any,
        path: Optional[str] = None,
        path_lookup: Any,
    ) -> Optional[Union[DefaultError, list["GetCuratedFiles"]]]:
        return await _get_curated_files_async(
            client=self.client,
            drive_id=drive_id,
            drive_id_lookup=drive_id_lookup,
            fields=fields,
            fields_lookup=fields_lookup,
            id=id,
            id_lookup=id_lookup,
            next_page=next_page,
            next_page_lookup=next_page_lookup,
            page_size=page_size,
            page_size_lookup=page_size_lookup,
            path=path,
            path_lookup=path_lookup,
        )

    def get_file_list(
        self,
        id: str,
        id_lookup: Any,
        *,
        drive_id: Optional[str] = None,
        drive_id_lookup: Any,
    ) -> Optional[Union[DefaultError, GetFileListResponse]]:
        return _get_file_list(
            client=self.client,
            id=id,
            id_lookup=id_lookup,
            drive_id=drive_id,
            drive_id_lookup=drive_id_lookup,
        )

    async def get_file_list_async(
        self,
        id: str,
        id_lookup: Any,
        *,
        drive_id: Optional[str] = None,
        drive_id_lookup: Any,
    ) -> Optional[Union[DefaultError, GetFileListResponse]]:
        return await _get_file_list_async(
            client=self.client,
            id=id,
            id_lookup=id_lookup,
            drive_id=drive_id,
            drive_id_lookup=drive_id_lookup,
        )

    def delete_row(
        self,
        *,
        body: DeleteRowRequest,
        range_: str,
        range__lookup: Any,
        reference_id: str,
        reference_id_lookup: Any,
        row: str,
        row_lookup: Any,
    ) -> Optional[Union[Any, DefaultError]]:
        return _delete_row(
            client=self.client,
            body=body,
            range_=range_,
            range__lookup=range__lookup,
            reference_id=reference_id,
            reference_id_lookup=reference_id_lookup,
            row=row,
            row_lookup=row_lookup,
        )

    async def delete_row_async(
        self,
        *,
        body: DeleteRowRequest,
        range_: str,
        range__lookup: Any,
        reference_id: str,
        reference_id_lookup: Any,
        row: str,
        row_lookup: Any,
    ) -> Optional[Union[Any, DefaultError]]:
        return await _delete_row_async(
            client=self.client,
            body=body,
            range_=range_,
            range__lookup=range__lookup,
            reference_id=reference_id,
            reference_id_lookup=reference_id_lookup,
            row=row,
            row_lookup=row_lookup,
        )

    def write_row(
        self,
        *,
        body: WriteRowRequest,
        reference_id: str,
        reference_id_lookup: Any,
        range_: str,
        range__lookup: Any,
        include_headers: Optional[bool] = True,
        include_headers_lookup: Any,
    ) -> Optional[Union[Any, DefaultError]]:
        return _write_row(
            client=self.client,
            body=body,
            reference_id=reference_id,
            reference_id_lookup=reference_id_lookup,
            range_=range_,
            range__lookup=range__lookup,
            include_headers=include_headers,
            include_headers_lookup=include_headers_lookup,
        )

    async def write_row_async(
        self,
        *,
        body: WriteRowRequest,
        reference_id: str,
        reference_id_lookup: Any,
        range_: str,
        range__lookup: Any,
        include_headers: Optional[bool] = True,
        include_headers_lookup: Any,
    ) -> Optional[Union[Any, DefaultError]]:
        return await _write_row_async(
            client=self.client,
            body=body,
            reference_id=reference_id,
            reference_id_lookup=reference_id_lookup,
            range_=range_,
            range__lookup=range__lookup,
            include_headers=include_headers,
            include_headers_lookup=include_headers_lookup,
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
        conflict_behavior_lookup: Any,
    ) -> Optional[Union[CopyFileFolderResponse, DefaultError]]:
        return _copy_file_folder(
            client=self.client,
            body=body,
            conflict_behavior=conflict_behavior,
            conflict_behavior_lookup=conflict_behavior_lookup,
        )

    async def copy_file_folder_async(
        self,
        *,
        body: CopyFileFolderRequest,
        conflict_behavior: Optional[str] = None,
        conflict_behavior_lookup: Any,
    ) -> Optional[Union[CopyFileFolderResponse, DefaultError]]:
        return await _copy_file_folder_async(
            client=self.client,
            body=body,
            conflict_behavior=conflict_behavior,
            conflict_behavior_lookup=conflict_behavior_lookup,
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

    def read_cell(
        self,
        *,
        cell_address: str,
        cell_address_lookup: Any,
        reference_id: str,
        reference_id_lookup: Any,
        worksheet_id: str,
        worksheet_id_lookup: Any,
        fields: Optional[str] = None,
        fields_lookup: Any,
        next_page: Optional[str] = None,
        next_page_lookup: Any,
        page_size: Optional[int] = None,
        page_size_lookup: Any,
        read: Optional[str] = None,
        read_lookup: Any,
    ) -> Optional[Union[DefaultError, list["ReadCell"]]]:
        return _read_cell(
            client=self.client,
            cell_address=cell_address,
            cell_address_lookup=cell_address_lookup,
            reference_id=reference_id,
            reference_id_lookup=reference_id_lookup,
            worksheet_id=worksheet_id,
            worksheet_id_lookup=worksheet_id_lookup,
            fields=fields,
            fields_lookup=fields_lookup,
            next_page=next_page,
            next_page_lookup=next_page_lookup,
            page_size=page_size,
            page_size_lookup=page_size_lookup,
            read=read,
            read_lookup=read_lookup,
        )

    async def read_cell_async(
        self,
        *,
        cell_address: str,
        cell_address_lookup: Any,
        reference_id: str,
        reference_id_lookup: Any,
        worksheet_id: str,
        worksheet_id_lookup: Any,
        fields: Optional[str] = None,
        fields_lookup: Any,
        next_page: Optional[str] = None,
        next_page_lookup: Any,
        page_size: Optional[int] = None,
        page_size_lookup: Any,
        read: Optional[str] = None,
        read_lookup: Any,
    ) -> Optional[Union[DefaultError, list["ReadCell"]]]:
        return await _read_cell_async(
            client=self.client,
            cell_address=cell_address,
            cell_address_lookup=cell_address_lookup,
            reference_id=reference_id,
            reference_id_lookup=reference_id_lookup,
            worksheet_id=worksheet_id,
            worksheet_id_lookup=worksheet_id_lookup,
            fields=fields,
            fields_lookup=fields_lookup,
            next_page=next_page,
            next_page_lookup=next_page_lookup,
            page_size=page_size,
            page_size_lookup=page_size_lookup,
            read=read,
            read_lookup=read_lookup,
        )

    def delete_column(
        self,
        *,
        body: DeleteColumnRequest,
        reference_id: str,
        reference_id_lookup: Any,
        has_headers: bool = False,
        has_headers_lookup: Any,
        range_: str,
        range__lookup: Any,
        column_position: str,
        column_position_lookup: Any,
    ) -> Optional[Union[Any, DefaultError]]:
        return _delete_column(
            client=self.client,
            body=body,
            reference_id=reference_id,
            reference_id_lookup=reference_id_lookup,
            has_headers=has_headers,
            has_headers_lookup=has_headers_lookup,
            range_=range_,
            range__lookup=range__lookup,
            column_position=column_position,
            column_position_lookup=column_position_lookup,
        )

    async def delete_column_async(
        self,
        *,
        body: DeleteColumnRequest,
        reference_id: str,
        reference_id_lookup: Any,
        has_headers: bool = False,
        has_headers_lookup: Any,
        range_: str,
        range__lookup: Any,
        column_position: str,
        column_position_lookup: Any,
    ) -> Optional[Union[Any, DefaultError]]:
        return await _delete_column_async(
            client=self.client,
            body=body,
            reference_id=reference_id,
            reference_id_lookup=reference_id_lookup,
            has_headers=has_headers,
            has_headers_lookup=has_headers_lookup,
            range_=range_,
            range__lookup=range__lookup,
            column_position=column_position,
            column_position_lookup=column_position_lookup,
        )

    def delete_sheet(
        self,
        id: str,
        id_lookup: Any,
        *,
        reference_id: str,
        reference_id_lookup: Any,
    ) -> Optional[Union[Any, DefaultError]]:
        return _delete_sheet(
            client=self.client,
            id=id,
            id_lookup=id_lookup,
            reference_id=reference_id,
            reference_id_lookup=reference_id_lookup,
        )

    async def delete_sheet_async(
        self,
        id: str,
        id_lookup: Any,
        *,
        reference_id: str,
        reference_id_lookup: Any,
    ) -> Optional[Union[Any, DefaultError]]:
        return await _delete_sheet_async(
            client=self.client,
            id=id,
            id_lookup=id_lookup,
            reference_id=reference_id,
            reference_id_lookup=reference_id_lookup,
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

    def rename_sheet(
        self,
        id: str,
        id_lookup: Any,
        *,
        body: RenameSheetRequest,
        reference_id: str,
        reference_id_lookup: Any,
    ) -> Optional[Union[DefaultError, RenameSheetResponse]]:
        return _rename_sheet(
            client=self.client,
            id=id,
            id_lookup=id_lookup,
            body=body,
            reference_id=reference_id,
            reference_id_lookup=reference_id_lookup,
        )

    async def rename_sheet_async(
        self,
        id: str,
        id_lookup: Any,
        *,
        body: RenameSheetRequest,
        reference_id: str,
        reference_id_lookup: Any,
    ) -> Optional[Union[DefaultError, RenameSheetResponse]]:
        return await _rename_sheet_async(
            client=self.client,
            id=id,
            id_lookup=id_lookup,
            body=body,
            reference_id=reference_id,
            reference_id_lookup=reference_id_lookup,
        )

    def create_create_share_link(
        self,
        *,
        body: CreateCreateShareLinkRequest,
    ) -> Optional[Union[CreateCreateShareLinkResponse, DefaultError]]:
        return _create_create_share_link(
            client=self.client,
            body=body,
        )

    async def create_create_share_link_async(
        self,
        *,
        body: CreateCreateShareLinkRequest,
    ) -> Optional[Union[CreateCreateShareLinkResponse, DefaultError]]:
        return await _create_create_share_link_async(
            client=self.client,
            body=body,
        )
