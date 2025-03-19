from .delete_sheet import (
    delete_sheet as _delete_sheet,
    delete_sheet_async as _delete_sheet_async,
)
from ..models.default_error import DefaultError
from ..models.delete_sheet_request import DeleteSheetRequest
from ..models.delete_sheet_response import DeleteSheetResponse
from typing import cast
from .create_spreadsheet import (
    create_spreadsheet as _create_spreadsheet,
    create_spreadsheet_async as _create_spreadsheet_async,
)
from ..models.create_spreadsheet_request import CreateSpreadsheetRequest
from ..models.create_spreadsheet_response import CreateSpreadsheetResponse
from .rename_sheet import (
    rename_sheet as _rename_sheet,
    rename_sheet_async as _rename_sheet_async,
)
from ..models.rename_sheet_request import RenameSheetRequest
from ..models.rename_sheet_response import RenameSheetResponse
from .add_sheet import (
    add_sheet as _add_sheet,
    add_sheet_async as _add_sheet_async,
)
from ..models.add_sheet_request import AddSheetRequest
from ..models.add_sheet_response import AddSheetResponse

from pydantic import Field
from typing import Any, Optional, Union

from ..client import Client
import httpx


class GoogleSheets:
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

    def delete_sheet(
        self,
        *,
        body: DeleteSheetRequest,
        spreadsheet_id: str,
        spreadsheet_id_lookup: Any,
    ) -> Optional[Union[DefaultError, DeleteSheetResponse]]:
        return _delete_sheet(
            client=self.client,
            body=body,
            spreadsheet_id=spreadsheet_id,
            spreadsheet_id_lookup=spreadsheet_id_lookup,
        )

    async def delete_sheet_async(
        self,
        *,
        body: DeleteSheetRequest,
        spreadsheet_id: str,
        spreadsheet_id_lookup: Any,
    ) -> Optional[Union[DefaultError, DeleteSheetResponse]]:
        return await _delete_sheet_async(
            client=self.client,
            body=body,
            spreadsheet_id=spreadsheet_id,
            spreadsheet_id_lookup=spreadsheet_id_lookup,
        )

    def create_spreadsheet(
        self,
        *,
        body: CreateSpreadsheetRequest,
    ) -> Optional[Union[CreateSpreadsheetResponse, DefaultError]]:
        return _create_spreadsheet(
            client=self.client,
            body=body,
        )

    async def create_spreadsheet_async(
        self,
        *,
        body: CreateSpreadsheetRequest,
    ) -> Optional[Union[CreateSpreadsheetResponse, DefaultError]]:
        return await _create_spreadsheet_async(
            client=self.client,
            body=body,
        )

    def rename_sheet(
        self,
        *,
        body: RenameSheetRequest,
        spreadsheet_id: str,
        spreadsheet_id_lookup: Any,
    ) -> Optional[Union[DefaultError, RenameSheetResponse]]:
        return _rename_sheet(
            client=self.client,
            body=body,
            spreadsheet_id=spreadsheet_id,
            spreadsheet_id_lookup=spreadsheet_id_lookup,
        )

    async def rename_sheet_async(
        self,
        *,
        body: RenameSheetRequest,
        spreadsheet_id: str,
        spreadsheet_id_lookup: Any,
    ) -> Optional[Union[DefaultError, RenameSheetResponse]]:
        return await _rename_sheet_async(
            client=self.client,
            body=body,
            spreadsheet_id=spreadsheet_id,
            spreadsheet_id_lookup=spreadsheet_id_lookup,
        )

    def add_sheet(
        self,
        *,
        body: AddSheetRequest,
        spreadsheet: str,
        spreadsheet_lookup: Any,
    ) -> Optional[Union[AddSheetResponse, DefaultError]]:
        return _add_sheet(
            client=self.client,
            body=body,
            spreadsheet=spreadsheet,
            spreadsheet_lookup=spreadsheet_lookup,
        )

    async def add_sheet_async(
        self,
        *,
        body: AddSheetRequest,
        spreadsheet: str,
        spreadsheet_lookup: Any,
    ) -> Optional[Union[AddSheetResponse, DefaultError]]:
        return await _add_sheet_async(
            client=self.client,
            body=body,
            spreadsheet=spreadsheet,
            spreadsheet_lookup=spreadsheet_lookup,
        )
