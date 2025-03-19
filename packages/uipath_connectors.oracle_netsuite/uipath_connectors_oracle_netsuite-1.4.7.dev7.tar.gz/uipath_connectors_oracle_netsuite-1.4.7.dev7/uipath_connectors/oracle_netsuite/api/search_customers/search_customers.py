from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response
from ... import errors

from ...models.default_error import DefaultError
from ...models.search_customers import SearchCustomers


def _get_kwargs(
    *,
    email: Optional[str] = None,
    external_id: Optional[str] = None,
    fields: Optional[str] = None,
    name: Optional[str] = None,
    next_page: Optional[str] = None,
    page_size: Optional[int] = None,
    phone: Optional[str] = None,
    where: Optional[str] = None,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["email"] = email

    params["externalId"] = external_id

    params["fields"] = fields

    params["name"] = name

    params["nextPage"] = next_page

    params["pageSize"] = page_size

    params["phone"] = phone

    params["where"] = where

    params = {k: v for k, v in params.items() if v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/SearchCustomers",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[DefaultError, list["SearchCustomers"]]]:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for componentsschemas_search_customers_list_item_data in _response_200:
            componentsschemas_search_customers_list_item = SearchCustomers.from_dict(
                componentsschemas_search_customers_list_item_data
            )

            response_200.append(componentsschemas_search_customers_list_item)

        return response_200
    if response.status_code == 400:
        response_400 = DefaultError.from_dict(response.json())

        return response_400
    if response.status_code == 401:
        response_401 = DefaultError.from_dict(response.json())

        return response_401
    if response.status_code == 403:
        response_403 = DefaultError.from_dict(response.json())

        return response_403
    if response.status_code == 404:
        response_404 = DefaultError.from_dict(response.json())

        return response_404
    if response.status_code == 405:
        response_405 = DefaultError.from_dict(response.json())

        return response_405
    if response.status_code == 406:
        response_406 = DefaultError.from_dict(response.json())

        return response_406
    if response.status_code == 409:
        response_409 = DefaultError.from_dict(response.json())

        return response_409
    if response.status_code == 415:
        response_415 = DefaultError.from_dict(response.json())

        return response_415
    if response.status_code == 500:
        response_500 = DefaultError.from_dict(response.json())

        return response_500
    if response.status_code == 402:
        response_402 = DefaultError.from_dict(response.json())

        return response_402
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[DefaultError, list["SearchCustomers"]]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    email: Optional[str] = None,
    email_lookup: Any,
    external_id: Optional[str] = None,
    external_id_lookup: Any,
    fields: Optional[str] = None,
    fields_lookup: Any,
    name: Optional[str] = None,
    name_lookup: Any,
    next_page: Optional[str] = None,
    next_page_lookup: Any,
    page_size: Optional[int] = None,
    page_size_lookup: Any,
    phone: Optional[str] = None,
    phone_lookup: Any,
    where: Optional[str] = None,
    where_lookup: Any,
) -> Response[Union[DefaultError, list["SearchCustomers"]]]:
    """Search Customers

     Search customers in Oracle Netsuite

    Args:
        email (Optional[str]):
        external_id (Optional[str]):
        fields (Optional[str]):
        name (Optional[str]):
        next_page (Optional[str]):
        page_size (Optional[int]):
        phone (Optional[str]):
        where (Optional[str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[DefaultError, list['SearchCustomers']]]
    """

    kwargs = _get_kwargs(
        email=email,
        external_id=external_id,
        fields=fields,
        name=name,
        next_page=next_page,
        page_size=page_size,
        phone=phone,
        where=where,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: Union[AuthenticatedClient, Client],
    email: Optional[str] = None,
    email_lookup: Any,
    external_id: Optional[str] = None,
    external_id_lookup: Any,
    fields: Optional[str] = None,
    fields_lookup: Any,
    name: Optional[str] = None,
    name_lookup: Any,
    next_page: Optional[str] = None,
    next_page_lookup: Any,
    page_size: Optional[int] = None,
    page_size_lookup: Any,
    phone: Optional[str] = None,
    phone_lookup: Any,
    where: Optional[str] = None,
    where_lookup: Any,
) -> Optional[Union[DefaultError, list["SearchCustomers"]]]:
    """Search Customers

     Search customers in Oracle Netsuite

    Args:
        email (Optional[str]):
        external_id (Optional[str]):
        fields (Optional[str]):
        name (Optional[str]):
        next_page (Optional[str]):
        page_size (Optional[int]):
        phone (Optional[str]):
        where (Optional[str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[DefaultError, list['SearchCustomers']]
    """

    return sync_detailed(
        client=client,
        email=email,
        email_lookup=email_lookup,
        external_id=external_id,
        external_id_lookup=external_id_lookup,
        fields=fields,
        fields_lookup=fields_lookup,
        name=name,
        name_lookup=name_lookup,
        next_page=next_page,
        next_page_lookup=next_page_lookup,
        page_size=page_size,
        page_size_lookup=page_size_lookup,
        phone=phone,
        phone_lookup=phone_lookup,
        where=where,
        where_lookup=where_lookup,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    email: Optional[str] = None,
    email_lookup: Any,
    external_id: Optional[str] = None,
    external_id_lookup: Any,
    fields: Optional[str] = None,
    fields_lookup: Any,
    name: Optional[str] = None,
    name_lookup: Any,
    next_page: Optional[str] = None,
    next_page_lookup: Any,
    page_size: Optional[int] = None,
    page_size_lookup: Any,
    phone: Optional[str] = None,
    phone_lookup: Any,
    where: Optional[str] = None,
    where_lookup: Any,
) -> Response[Union[DefaultError, list["SearchCustomers"]]]:
    """Search Customers

     Search customers in Oracle Netsuite

    Args:
        email (Optional[str]):
        external_id (Optional[str]):
        fields (Optional[str]):
        name (Optional[str]):
        next_page (Optional[str]):
        page_size (Optional[int]):
        phone (Optional[str]):
        where (Optional[str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[DefaultError, list['SearchCustomers']]]
    """

    kwargs = _get_kwargs(
        email=email,
        external_id=external_id,
        fields=fields,
        name=name,
        next_page=next_page,
        page_size=page_size,
        phone=phone,
        where=where,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    email: Optional[str] = None,
    email_lookup: Any,
    external_id: Optional[str] = None,
    external_id_lookup: Any,
    fields: Optional[str] = None,
    fields_lookup: Any,
    name: Optional[str] = None,
    name_lookup: Any,
    next_page: Optional[str] = None,
    next_page_lookup: Any,
    page_size: Optional[int] = None,
    page_size_lookup: Any,
    phone: Optional[str] = None,
    phone_lookup: Any,
    where: Optional[str] = None,
    where_lookup: Any,
) -> Optional[Union[DefaultError, list["SearchCustomers"]]]:
    """Search Customers

     Search customers in Oracle Netsuite

    Args:
        email (Optional[str]):
        external_id (Optional[str]):
        fields (Optional[str]):
        name (Optional[str]):
        next_page (Optional[str]):
        page_size (Optional[int]):
        phone (Optional[str]):
        where (Optional[str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[DefaultError, list['SearchCustomers']]
    """

    return (
        await asyncio_detailed(
            client=client,
            email=email,
            email_lookup=email_lookup,
            external_id=external_id,
            external_id_lookup=external_id_lookup,
            fields=fields,
            fields_lookup=fields_lookup,
            name=name,
            name_lookup=name_lookup,
            next_page=next_page,
            next_page_lookup=next_page_lookup,
            page_size=page_size,
            page_size_lookup=page_size_lookup,
            phone=phone,
            phone_lookup=phone_lookup,
            where=where,
            where_lookup=where_lookup,
        )
    ).parsed
