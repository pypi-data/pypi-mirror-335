from .curated_contact import (
    create_basic_contact as _create_basic_contact,
    create_basic_contact_async as _create_basic_contact_async,
)
from ..models.create_basic_contact_request import CreateBasicContactRequest
from ..models.create_basic_contact_response import CreateBasicContactResponse
from ..models.default_error import DefaultError
from typing import cast
from .curated_customer import (
    create_customer as _create_customer,
    create_customer_async as _create_customer_async,
    update_customer as _update_customer,
    update_customer_async as _update_customer_async,
)
from ..models.create_customer_request import CreateCustomerRequest
from ..models.create_customer_response import CreateCustomerResponse
from ..models.update_customer_request import UpdateCustomerRequest
from ..models.update_customer_response import UpdateCustomerResponse
from .curated_support_case import (
    create_supportcase as _create_supportcase,
    create_supportcase_async as _create_supportcase_async,
)
from ..models.create_supportcase_request import CreateSupportcaseRequest
from ..models.create_supportcase_response import CreateSupportcaseResponse
from .curated_vendor import (
    create_vendor as _create_vendor,
    create_vendor_async as _create_vendor_async,
    update_vendor as _update_vendor,
    update_vendor_async as _update_vendor_async,
)
from ..models.create_vendor_request import CreateVendorRequest
from ..models.create_vendor_response import CreateVendorResponse
from ..models.update_vendor_request import UpdateVendorRequest
from ..models.update_vendor_response import UpdateVendorResponse
from .file_download import (
    download_file as _download_file,
    download_file_async as _download_file_async,
)
from ..models.download_file_response import DownloadFileResponse
from ..types import File
from io import BytesIO
from .execute_suite_ql import (
    execute_suite_ql_query as _execute_suite_ql_query,
    execute_suite_ql_query_async as _execute_suite_ql_query_async,
)
from ..models.execute_suite_ql_query_request import ExecuteSuiteQLQueryRequest
from .search_customers import (
    search_customers as _search_customers,
    search_customers_async as _search_customers_async,
)
from ..models.search_customers import SearchCustomers
from .search_inventory_item import (
    search_items as _search_items,
    search_items_async as _search_items_async,
)
from ..models.search_items import SearchItems
from .curated_update_contact import (
    update_basic_contact as _update_basic_contact,
    update_basic_contact_async as _update_basic_contact_async,
)
from ..models.update_basic_contact_request import UpdateBasicContactRequest
from ..models.update_basic_contact_response import UpdateBasicContactResponse
from .curated_update_support_case import (
    update_supportcase as _update_supportcase,
    update_supportcase_async as _update_supportcase_async,
)
from ..models.update_supportcase_request import UpdateSupportcaseRequest
from ..models.update_supportcase_response import UpdateSupportcaseResponse

from pydantic import Field
from typing import Any, Optional, Union

from ..client import Client
import httpx


class OracleNetsuite:
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

    def create_basic_contact(
        self,
        *,
        body: CreateBasicContactRequest,
    ) -> Optional[Union[CreateBasicContactResponse, DefaultError]]:
        return _create_basic_contact(
            client=self.client,
            body=body,
        )

    async def create_basic_contact_async(
        self,
        *,
        body: CreateBasicContactRequest,
    ) -> Optional[Union[CreateBasicContactResponse, DefaultError]]:
        return await _create_basic_contact_async(
            client=self.client,
            body=body,
        )

    def create_customer(
        self,
        *,
        body: CreateCustomerRequest,
    ) -> Optional[Union[CreateCustomerResponse, DefaultError]]:
        return _create_customer(
            client=self.client,
            body=body,
        )

    async def create_customer_async(
        self,
        *,
        body: CreateCustomerRequest,
    ) -> Optional[Union[CreateCustomerResponse, DefaultError]]:
        return await _create_customer_async(
            client=self.client,
            body=body,
        )

    def update_customer(
        self,
        id: str,
        *,
        body: UpdateCustomerRequest,
    ) -> Optional[Union[DefaultError, UpdateCustomerResponse]]:
        return _update_customer(
            client=self.client,
            id=id,
            body=body,
        )

    async def update_customer_async(
        self,
        id: str,
        *,
        body: UpdateCustomerRequest,
    ) -> Optional[Union[DefaultError, UpdateCustomerResponse]]:
        return await _update_customer_async(
            client=self.client,
            id=id,
            body=body,
        )

    def create_supportcase(
        self,
        *,
        body: CreateSupportcaseRequest,
    ) -> Optional[Union[CreateSupportcaseResponse, DefaultError]]:
        return _create_supportcase(
            client=self.client,
            body=body,
        )

    async def create_supportcase_async(
        self,
        *,
        body: CreateSupportcaseRequest,
    ) -> Optional[Union[CreateSupportcaseResponse, DefaultError]]:
        return await _create_supportcase_async(
            client=self.client,
            body=body,
        )

    def create_vendor(
        self,
        *,
        body: CreateVendorRequest,
    ) -> Optional[Union[CreateVendorResponse, DefaultError]]:
        return _create_vendor(
            client=self.client,
            body=body,
        )

    async def create_vendor_async(
        self,
        *,
        body: CreateVendorRequest,
    ) -> Optional[Union[CreateVendorResponse, DefaultError]]:
        return await _create_vendor_async(
            client=self.client,
            body=body,
        )

    def update_vendor(
        self,
        id: str,
        *,
        body: UpdateVendorRequest,
    ) -> Optional[Union[DefaultError, UpdateVendorResponse]]:
        return _update_vendor(
            client=self.client,
            id=id,
            body=body,
        )

    async def update_vendor_async(
        self,
        id: str,
        *,
        body: UpdateVendorRequest,
    ) -> Optional[Union[DefaultError, UpdateVendorResponse]]:
        return await _update_vendor_async(
            client=self.client,
            id=id,
            body=body,
        )

    def download_file(
        self,
        file_id: str,
    ) -> Optional[Union[DefaultError, File]]:
        return _download_file(
            client=self.client,
            file_id=file_id,
        )

    async def download_file_async(
        self,
        file_id: str,
    ) -> Optional[Union[DefaultError, File]]:
        return await _download_file_async(
            client=self.client,
            file_id=file_id,
        )

    def execute_suite_ql_query(
        self,
        *,
        body: ExecuteSuiteQLQueryRequest,
        limit: Optional[str] = None,
        offset: Optional[str] = None,
    ) -> Optional[Union[Any, DefaultError]]:
        return _execute_suite_ql_query(
            client=self.client,
            body=body,
            limit=limit,
            offset=offset,
        )

    async def execute_suite_ql_query_async(
        self,
        *,
        body: ExecuteSuiteQLQueryRequest,
        limit: Optional[str] = None,
        offset: Optional[str] = None,
    ) -> Optional[Union[Any, DefaultError]]:
        return await _execute_suite_ql_query_async(
            client=self.client,
            body=body,
            limit=limit,
            offset=offset,
        )

    def search_customers(
        self,
        *,
        page_size: Optional[int] = None,
        next_page: Optional[str] = None,
        name: Optional[str] = None,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        external_id: Optional[str] = None,
    ) -> Optional[Union[DefaultError, list["SearchCustomers"]]]:
        return _search_customers(
            client=self.client,
            page_size=page_size,
            next_page=next_page,
            name=name,
            email=email,
            phone=phone,
            external_id=external_id,
        )

    async def search_customers_async(
        self,
        *,
        page_size: Optional[int] = None,
        next_page: Optional[str] = None,
        name: Optional[str] = None,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        external_id: Optional[str] = None,
    ) -> Optional[Union[DefaultError, list["SearchCustomers"]]]:
        return await _search_customers_async(
            client=self.client,
            page_size=page_size,
            next_page=next_page,
            name=name,
            email=email,
            phone=phone,
            external_id=external_id,
        )

    def search_items(
        self,
        *,
        page_size: Optional[int] = None,
        next_page: Optional[str] = None,
        name: Optional[str] = None,
        mpn: Optional[str] = None,
        upc_code: Optional[str] = None,
        external_id: Optional[str] = None,
    ) -> Optional[Union[DefaultError, list["SearchItems"]]]:
        return _search_items(
            client=self.client,
            page_size=page_size,
            next_page=next_page,
            name=name,
            mpn=mpn,
            upc_code=upc_code,
            external_id=external_id,
        )

    async def search_items_async(
        self,
        *,
        page_size: Optional[int] = None,
        next_page: Optional[str] = None,
        name: Optional[str] = None,
        mpn: Optional[str] = None,
        upc_code: Optional[str] = None,
        external_id: Optional[str] = None,
    ) -> Optional[Union[DefaultError, list["SearchItems"]]]:
        return await _search_items_async(
            client=self.client,
            page_size=page_size,
            next_page=next_page,
            name=name,
            mpn=mpn,
            upc_code=upc_code,
            external_id=external_id,
        )

    def update_basic_contact(
        self,
        curated_contact_id: str,
        *,
        body: UpdateBasicContactRequest,
    ) -> Optional[Union[DefaultError, UpdateBasicContactResponse]]:
        return _update_basic_contact(
            client=self.client,
            curated_contact_id=curated_contact_id,
            body=body,
        )

    async def update_basic_contact_async(
        self,
        curated_contact_id: str,
        *,
        body: UpdateBasicContactRequest,
    ) -> Optional[Union[DefaultError, UpdateBasicContactResponse]]:
        return await _update_basic_contact_async(
            client=self.client,
            curated_contact_id=curated_contact_id,
            body=body,
        )

    def update_supportcase(
        self,
        curated_support_case_id: str,
        *,
        body: UpdateSupportcaseRequest,
    ) -> Optional[Union[DefaultError, UpdateSupportcaseResponse]]:
        return _update_supportcase(
            client=self.client,
            curated_support_case_id=curated_support_case_id,
            body=body,
        )

    async def update_supportcase_async(
        self,
        curated_support_case_id: str,
        *,
        body: UpdateSupportcaseRequest,
    ) -> Optional[Union[DefaultError, UpdateSupportcaseResponse]]:
        return await _update_supportcase_async(
            client=self.client,
            curated_support_case_id=curated_support_case_id,
            body=body,
        )
