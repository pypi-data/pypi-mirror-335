from .attachment_link import (
    add_file_to_record as _add_file_to_record,
    add_file_to_record_async as _add_file_to_record_async,
)
from ..models.add_file_to_record_request import AddFileToRecordRequest
from ..models.add_file_to_record_response import AddFileToRecordResponse
from ..models.default_error import DefaultError
from typing import cast
from .curated_account import (
    create_account as _create_account,
    create_account_async as _create_account_async,
    get_account_by_id as _get_account_by_id,
    get_account_by_id_async as _get_account_by_id_async,
    update_account as _update_account,
    update_account_async as _update_account_async,
)
from ..models.create_account_request import CreateAccountRequest
from ..models.create_account_response import CreateAccountResponse
from ..models.get_account_by_id_response import GetAccountByIDResponse
from ..models.update_account_request import UpdateAccountRequest
from ..models.update_account_response import UpdateAccountResponse
from .create_bulk_job import (
    create_bulk_job as _create_bulk_job,
    create_bulk_job_async as _create_bulk_job_async,
)
from ..models.create_bulk_job_body import CreateBulkJobBody
from ..models.create_bulk_job_response import CreateBulkJobResponse
from .curated_contact import (
    create_contact as _create_contact,
    create_contact_async as _create_contact_async,
    get_contact_by_id as _get_contact_by_id,
    get_contact_by_id_async as _get_contact_by_id_async,
    update_contact as _update_contact,
    update_contact_async as _update_contact_async,
)
from ..models.create_contact_request import CreateContactRequest
from ..models.create_contact_response import CreateContactResponse
from ..models.get_contact_by_id_response import GetContactByIDResponse
from ..models.update_contact_request import UpdateContactRequest
from ..models.update_contact_response import UpdateContactResponse
from .curated_lead import (
    create_lead as _create_lead,
    create_lead_async as _create_lead_async,
    get_lead_by_id as _get_lead_by_id,
    get_lead_by_id_async as _get_lead_by_id_async,
    update_lead as _update_lead,
    update_lead_async as _update_lead_async,
)
from ..models.create_lead_request import CreateLeadRequest
from ..models.create_lead_response import CreateLeadResponse
from ..models.get_lead_by_id_response import GetLeadByIDResponse
from ..models.update_lead_request import UpdateLeadRequest
from ..models.update_lead_response import UpdateLeadResponse
from .curated_opportunity import (
    create_opportunity as _create_opportunity,
    create_opportunity_async as _create_opportunity_async,
    get_opportunity_by_id as _get_opportunity_by_id,
    get_opportunity_by_id_async as _get_opportunity_by_id_async,
)
from ..models.create_opportunity_request import CreateOpportunityRequest
from ..models.create_opportunity_response import CreateOpportunityResponse
from ..models.get_opportunity_by_id_response import GetOpportunityByIdResponse
from .create_query_job import (
    create_query_job as _create_query_job,
    create_query_job_async as _create_query_job_async,
)
from ..models.create_query_job_request import CreateQueryJobRequest
from ..models.create_query_job_response import CreateQueryJobResponse
from .attachment_download import (
    download_file as _download_file,
    download_file_async as _download_file_async,
)
from ..models.download_file_response import DownloadFileResponse
from ..types import File
from io import BytesIO
from .download_soql_bulk_job_results import (
    download_soql_bulk_job_results as _download_soql_bulk_job_results,
    download_soql_bulk_job_results_async as _download_soql_bulk_job_results_async,
)
from ..models.download_soql_bulk_job_results_response import (
    DownloadSOQLBulkJobResultsResponse,
)
from .download_unprocessed_records_of_bulk_job import (
    download_unprocessed_records_of_bulk_job as _download_unprocessed_records_of_bulk_job,
    download_unprocessed_records_of_bulk_job_async as _download_unprocessed_records_of_bulk_job_async,
)
from ..models.download_unprocessed_records_of_bulk_job_response import (
    DownloadUnprocessedRecordsOfBulkJobResponse,
)
from .curated_soql_query import (
    execute_query as _execute_query,
    execute_query_async as _execute_query_async,
)
from ..models.execute_query_request import ExecuteQueryRequest
from .report import (
    get_report as _get_report,
    get_report_async as _get_report_async,
)
from ..models.get_report_response import GetReportResponse
from .get_bulk_job_info import (
    get_bulk_upload_job_info as _get_bulk_upload_job_info,
    get_bulk_upload_job_info_async as _get_bulk_upload_job_info_async,
)
from ..models.get_bulk_upload_job_info_response import GetBulkUploadJobInfoResponse
from .get_object_fieldnames import (
    get_object_field_names as _get_object_field_names,
    get_object_field_names_async as _get_object_field_names_async,
)
from ..models.get_object_field_names_response import GetObjectFieldNamesResponse
from .parameterized_search_post import (
    parameterized_search as _parameterized_search,
    parameterized_search_async as _parameterized_search_async,
)
from ..models.parameterized_search import ParameterizedSearch
from ..models.parameterized_search_request import ParameterizedSearchRequest
from .start_or_abort_bulk_job import (
    start_or_abort_bulk_job as _start_or_abort_bulk_job,
    start_or_abort_bulk_job_async as _start_or_abort_bulk_job_async,
)
from ..models.start_or_abort_bulk_job_request import StartOrAbortBulkJobRequest
from .curated_upload_attachments import (
    upload_attachment as _upload_attachment,
    upload_attachment_async as _upload_attachment_async,
)
from ..models.upload_attachment_body import UploadAttachmentBody
from ..models.upload_attachment_request import UploadAttachmentRequest
from ..models.upload_attachment_response import UploadAttachmentResponse

from pydantic import Field
from typing import Any, Optional, Union

from ..client import Client
import httpx


class SalesforceSfdc:
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

    def add_file_to_record(
        self,
        *,
        body: AddFileToRecordRequest,
    ) -> Optional[Union[AddFileToRecordResponse, DefaultError]]:
        return _add_file_to_record(
            client=self.client,
            body=body,
        )

    async def add_file_to_record_async(
        self,
        *,
        body: AddFileToRecordRequest,
    ) -> Optional[Union[AddFileToRecordResponse, DefaultError]]:
        return await _add_file_to_record_async(
            client=self.client,
            body=body,
        )

    def create_account(
        self,
        *,
        body: CreateAccountRequest,
    ) -> Optional[Union[CreateAccountResponse, DefaultError]]:
        return _create_account(
            client=self.client,
            body=body,
        )

    async def create_account_async(
        self,
        *,
        body: CreateAccountRequest,
    ) -> Optional[Union[CreateAccountResponse, DefaultError]]:
        return await _create_account_async(
            client=self.client,
            body=body,
        )

    def get_account_by_id(
        self,
        curated_account_id: str,
        curated_account_id_lookup: Any,
    ) -> Optional[Union[DefaultError, GetAccountByIDResponse]]:
        return _get_account_by_id(
            client=self.client,
            curated_account_id=curated_account_id,
            curated_account_id_lookup=curated_account_id_lookup,
        )

    async def get_account_by_id_async(
        self,
        curated_account_id: str,
        curated_account_id_lookup: Any,
    ) -> Optional[Union[DefaultError, GetAccountByIDResponse]]:
        return await _get_account_by_id_async(
            client=self.client,
            curated_account_id=curated_account_id,
            curated_account_id_lookup=curated_account_id_lookup,
        )

    def update_account(
        self,
        curated_account_id: str,
        curated_account_id_lookup: Any,
        *,
        body: UpdateAccountRequest,
    ) -> Optional[Union[DefaultError, UpdateAccountResponse]]:
        return _update_account(
            client=self.client,
            curated_account_id=curated_account_id,
            curated_account_id_lookup=curated_account_id_lookup,
            body=body,
        )

    async def update_account_async(
        self,
        curated_account_id: str,
        curated_account_id_lookup: Any,
        *,
        body: UpdateAccountRequest,
    ) -> Optional[Union[DefaultError, UpdateAccountResponse]]:
        return await _update_account_async(
            client=self.client,
            curated_account_id=curated_account_id,
            curated_account_id_lookup=curated_account_id_lookup,
            body=body,
        )

    def create_bulk_job(
        self,
        *,
        body: CreateBulkJobBody,
        column_delimiter: Optional[str] = "COMMA",
        line_ending: Optional[str] = "LF",
        operation: str,
        object_: str,
        object__lookup: Any,
    ) -> Optional[Union[CreateBulkJobResponse, DefaultError]]:
        return _create_bulk_job(
            client=self.client,
            body=body,
            column_delimiter=column_delimiter,
            line_ending=line_ending,
            operation=operation,
            object_=object_,
            object__lookup=object__lookup,
        )

    async def create_bulk_job_async(
        self,
        *,
        body: CreateBulkJobBody,
        column_delimiter: Optional[str] = "COMMA",
        line_ending: Optional[str] = "LF",
        operation: str,
        object_: str,
        object__lookup: Any,
    ) -> Optional[Union[CreateBulkJobResponse, DefaultError]]:
        return await _create_bulk_job_async(
            client=self.client,
            body=body,
            column_delimiter=column_delimiter,
            line_ending=line_ending,
            operation=operation,
            object_=object_,
            object__lookup=object__lookup,
        )

    def create_contact(
        self,
        *,
        body: CreateContactRequest,
    ) -> Optional[Union[CreateContactResponse, DefaultError]]:
        return _create_contact(
            client=self.client,
            body=body,
        )

    async def create_contact_async(
        self,
        *,
        body: CreateContactRequest,
    ) -> Optional[Union[CreateContactResponse, DefaultError]]:
        return await _create_contact_async(
            client=self.client,
            body=body,
        )

    def get_contact_by_id(
        self,
        curated_contact_id: str,
        curated_contact_id_lookup: Any,
    ) -> Optional[Union[DefaultError, GetContactByIDResponse]]:
        return _get_contact_by_id(
            client=self.client,
            curated_contact_id=curated_contact_id,
            curated_contact_id_lookup=curated_contact_id_lookup,
        )

    async def get_contact_by_id_async(
        self,
        curated_contact_id: str,
        curated_contact_id_lookup: Any,
    ) -> Optional[Union[DefaultError, GetContactByIDResponse]]:
        return await _get_contact_by_id_async(
            client=self.client,
            curated_contact_id=curated_contact_id,
            curated_contact_id_lookup=curated_contact_id_lookup,
        )

    def update_contact(
        self,
        curated_contact_id: str,
        curated_contact_id_lookup: Any,
        *,
        body: UpdateContactRequest,
    ) -> Optional[Union[DefaultError, UpdateContactResponse]]:
        return _update_contact(
            client=self.client,
            curated_contact_id=curated_contact_id,
            curated_contact_id_lookup=curated_contact_id_lookup,
            body=body,
        )

    async def update_contact_async(
        self,
        curated_contact_id: str,
        curated_contact_id_lookup: Any,
        *,
        body: UpdateContactRequest,
    ) -> Optional[Union[DefaultError, UpdateContactResponse]]:
        return await _update_contact_async(
            client=self.client,
            curated_contact_id=curated_contact_id,
            curated_contact_id_lookup=curated_contact_id_lookup,
            body=body,
        )

    def create_lead(
        self,
        *,
        body: CreateLeadRequest,
    ) -> Optional[Union[CreateLeadResponse, DefaultError]]:
        return _create_lead(
            client=self.client,
            body=body,
        )

    async def create_lead_async(
        self,
        *,
        body: CreateLeadRequest,
    ) -> Optional[Union[CreateLeadResponse, DefaultError]]:
        return await _create_lead_async(
            client=self.client,
            body=body,
        )

    def get_lead_by_id(
        self,
        curated_lead_id: str,
        curated_lead_id_lookup: Any,
    ) -> Optional[Union[DefaultError, GetLeadByIDResponse]]:
        return _get_lead_by_id(
            client=self.client,
            curated_lead_id=curated_lead_id,
            curated_lead_id_lookup=curated_lead_id_lookup,
        )

    async def get_lead_by_id_async(
        self,
        curated_lead_id: str,
        curated_lead_id_lookup: Any,
    ) -> Optional[Union[DefaultError, GetLeadByIDResponse]]:
        return await _get_lead_by_id_async(
            client=self.client,
            curated_lead_id=curated_lead_id,
            curated_lead_id_lookup=curated_lead_id_lookup,
        )

    def update_lead(
        self,
        curated_lead_id: str,
        curated_lead_id_lookup: Any,
        *,
        body: UpdateLeadRequest,
    ) -> Optional[Union[DefaultError, UpdateLeadResponse]]:
        return _update_lead(
            client=self.client,
            curated_lead_id=curated_lead_id,
            curated_lead_id_lookup=curated_lead_id_lookup,
            body=body,
        )

    async def update_lead_async(
        self,
        curated_lead_id: str,
        curated_lead_id_lookup: Any,
        *,
        body: UpdateLeadRequest,
    ) -> Optional[Union[DefaultError, UpdateLeadResponse]]:
        return await _update_lead_async(
            client=self.client,
            curated_lead_id=curated_lead_id,
            curated_lead_id_lookup=curated_lead_id_lookup,
            body=body,
        )

    def create_opportunity(
        self,
        *,
        body: CreateOpportunityRequest,
    ) -> Optional[Union[CreateOpportunityResponse, DefaultError]]:
        return _create_opportunity(
            client=self.client,
            body=body,
        )

    async def create_opportunity_async(
        self,
        *,
        body: CreateOpportunityRequest,
    ) -> Optional[Union[CreateOpportunityResponse, DefaultError]]:
        return await _create_opportunity_async(
            client=self.client,
            body=body,
        )

    def get_opportunity_by_id(
        self,
        curated_opportunity_id: str,
        curated_opportunity_id_lookup: Any,
    ) -> Optional[Union[DefaultError, GetOpportunityByIdResponse]]:
        return _get_opportunity_by_id(
            client=self.client,
            curated_opportunity_id=curated_opportunity_id,
            curated_opportunity_id_lookup=curated_opportunity_id_lookup,
        )

    async def get_opportunity_by_id_async(
        self,
        curated_opportunity_id: str,
        curated_opportunity_id_lookup: Any,
    ) -> Optional[Union[DefaultError, GetOpportunityByIdResponse]]:
        return await _get_opportunity_by_id_async(
            client=self.client,
            curated_opportunity_id=curated_opportunity_id,
            curated_opportunity_id_lookup=curated_opportunity_id_lookup,
        )

    def create_query_job(
        self,
        *,
        body: CreateQueryJobRequest,
    ) -> Optional[Union[CreateQueryJobResponse, DefaultError]]:
        return _create_query_job(
            client=self.client,
            body=body,
        )

    async def create_query_job_async(
        self,
        *,
        body: CreateQueryJobRequest,
    ) -> Optional[Union[CreateQueryJobResponse, DefaultError]]:
        return await _create_query_job_async(
            client=self.client,
            body=body,
        )

    def download_file(
        self,
        id: str,
        id_lookup: Any,
    ) -> Optional[Union[DefaultError, File]]:
        return _download_file(
            client=self.client,
            id=id,
            id_lookup=id_lookup,
        )

    async def download_file_async(
        self,
        id: str,
        id_lookup: Any,
    ) -> Optional[Union[DefaultError, File]]:
        return await _download_file_async(
            client=self.client,
            id=id,
            id_lookup=id_lookup,
        )

    def download_soql_bulk_job_results(
        self,
        id: str,
    ) -> Optional[Union[DefaultError, File]]:
        return _download_soql_bulk_job_results(
            client=self.client,
            id=id,
        )

    async def download_soql_bulk_job_results_async(
        self,
        id: str,
    ) -> Optional[Union[DefaultError, File]]:
        return await _download_soql_bulk_job_results_async(
            client=self.client,
            id=id,
        )

    def download_unprocessed_records_of_bulk_job(
        self,
        id: str,
    ) -> Optional[Union[DefaultError, File]]:
        return _download_unprocessed_records_of_bulk_job(
            client=self.client,
            id=id,
        )

    async def download_unprocessed_records_of_bulk_job_async(
        self,
        id: str,
    ) -> Optional[Union[DefaultError, File]]:
        return await _download_unprocessed_records_of_bulk_job_async(
            client=self.client,
            id=id,
        )

    def execute_query(
        self,
        *,
        body: ExecuteQueryRequest,
        next_page: Optional[str] = None,
        page_size: Optional[int] = None,
    ) -> Optional[Union[Any, DefaultError]]:
        return _execute_query(
            client=self.client,
            body=body,
            next_page=next_page,
            page_size=page_size,
        )

    async def execute_query_async(
        self,
        *,
        body: ExecuteQueryRequest,
        next_page: Optional[str] = None,
        page_size: Optional[int] = None,
    ) -> Optional[Union[Any, DefaultError]]:
        return await _execute_query_async(
            client=self.client,
            body=body,
            next_page=next_page,
            page_size=page_size,
        )

    def get_report(
        self,
        report_id: str,
        report_id_lookup: Any,
    ) -> Optional[Union[DefaultError, GetReportResponse]]:
        return _get_report(
            client=self.client,
            report_id=report_id,
            report_id_lookup=report_id_lookup,
        )

    async def get_report_async(
        self,
        report_id: str,
        report_id_lookup: Any,
    ) -> Optional[Union[DefaultError, GetReportResponse]]:
        return await _get_report_async(
            client=self.client,
            report_id=report_id,
            report_id_lookup=report_id_lookup,
        )

    def get_bulk_upload_job_info(
        self,
        id: str,
        *,
        jobtype: str,
    ) -> Optional[Union[DefaultError, GetBulkUploadJobInfoResponse]]:
        return _get_bulk_upload_job_info(
            client=self.client,
            id=id,
            jobtype=jobtype,
        )

    async def get_bulk_upload_job_info_async(
        self,
        id: str,
        *,
        jobtype: str,
    ) -> Optional[Union[DefaultError, GetBulkUploadJobInfoResponse]]:
        return await _get_bulk_upload_job_info_async(
            client=self.client,
            id=id,
            jobtype=jobtype,
        )

    def get_object_field_names(
        self,
        object_name: str,
        object_name_lookup: Any,
    ) -> Optional[Union[DefaultError, GetObjectFieldNamesResponse]]:
        return _get_object_field_names(
            client=self.client,
            object_name=object_name,
            object_name_lookup=object_name_lookup,
        )

    async def get_object_field_names_async(
        self,
        object_name: str,
        object_name_lookup: Any,
    ) -> Optional[Union[DefaultError, GetObjectFieldNamesResponse]]:
        return await _get_object_field_names_async(
            client=self.client,
            object_name=object_name,
            object_name_lookup=object_name_lookup,
        )

    def parameterized_search(
        self,
        *,
        body: ParameterizedSearchRequest,
    ) -> Optional[Union[DefaultError, list["ParameterizedSearch"]]]:
        return _parameterized_search(
            client=self.client,
            body=body,
        )

    async def parameterized_search_async(
        self,
        *,
        body: ParameterizedSearchRequest,
    ) -> Optional[Union[DefaultError, list["ParameterizedSearch"]]]:
        return await _parameterized_search_async(
            client=self.client,
            body=body,
        )

    def start_or_abort_bulk_job(
        self,
        id: str,
        *,
        body: StartOrAbortBulkJobRequest,
        jobtype: str,
    ) -> Optional[Union[Any, DefaultError]]:
        return _start_or_abort_bulk_job(
            client=self.client,
            id=id,
            body=body,
            jobtype=jobtype,
        )

    async def start_or_abort_bulk_job_async(
        self,
        id: str,
        *,
        body: StartOrAbortBulkJobRequest,
        jobtype: str,
    ) -> Optional[Union[Any, DefaultError]]:
        return await _start_or_abort_bulk_job_async(
            client=self.client,
            id=id,
            body=body,
            jobtype=jobtype,
        )

    def upload_attachment(
        self,
        *,
        body: UploadAttachmentBody,
    ) -> Optional[Union[DefaultError, UploadAttachmentResponse]]:
        return _upload_attachment(
            client=self.client,
            body=body,
        )

    async def upload_attachment_async(
        self,
        *,
        body: UploadAttachmentBody,
    ) -> Optional[Union[DefaultError, UploadAttachmentResponse]]:
        return await _upload_attachment_async(
            client=self.client,
            body=body,
        )
