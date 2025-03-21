from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response
from ... import errors

from ...models.default_error import DefaultError
from ...models.execute_query_request import ExecuteQueryRequest


def _get_kwargs(
    *,
    body: ExecuteQueryRequest,
    next_page: Optional[str] = None,
    page_size: Optional[int] = None,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    params: dict[str, Any] = {}

    params["nextPage"] = next_page

    params["pageSize"] = page_size

    params = {k: v for k, v in params.items() if v is not None}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/curated_soqlQuery",
        "params": params,
    }

    _body = body.to_dict()

    _kwargs["json"] = _body
    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Any, DefaultError]]:
    if response.status_code == 200:
        response_200 = cast(Any, None)
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
) -> Response[Union[Any, DefaultError]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: ExecuteQueryRequest,
    next_page: Optional[str] = None,
    page_size: Optional[int] = None,
) -> Response[Union[Any, DefaultError]]:
    """Search using SOQL

     Retrieve records by using Salesforce Object Query Language (SOQL)

    Args:
        next_page (Optional[str]): The Next page to get from set of bulk results
        page_size (Optional[int]): Page Size is optional. If not supplied the entire file is
            returned. Use this along with next page to paginate the bulk results. If paging is done
            results are always a JSON array
        body (ExecuteQueryRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, DefaultError]]
    """

    kwargs = _get_kwargs(
        body=body,
        next_page=next_page,
        page_size=page_size,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: Union[AuthenticatedClient, Client],
    body: ExecuteQueryRequest,
    next_page: Optional[str] = None,
    page_size: Optional[int] = None,
) -> Optional[Union[Any, DefaultError]]:
    """Search using SOQL

     Retrieve records by using Salesforce Object Query Language (SOQL)

    Args:
        next_page (Optional[str]): The Next page to get from set of bulk results
        page_size (Optional[int]): Page Size is optional. If not supplied the entire file is
            returned. Use this along with next page to paginate the bulk results. If paging is done
            results are always a JSON array
        body (ExecuteQueryRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, DefaultError]
    """

    return sync_detailed(
        client=client,
        body=body,
        next_page=next_page,
        page_size=page_size,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: ExecuteQueryRequest,
    next_page: Optional[str] = None,
    page_size: Optional[int] = None,
) -> Response[Union[Any, DefaultError]]:
    """Search using SOQL

     Retrieve records by using Salesforce Object Query Language (SOQL)

    Args:
        next_page (Optional[str]): The Next page to get from set of bulk results
        page_size (Optional[int]): Page Size is optional. If not supplied the entire file is
            returned. Use this along with next page to paginate the bulk results. If paging is done
            results are always a JSON array
        body (ExecuteQueryRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, DefaultError]]
    """

    kwargs = _get_kwargs(
        body=body,
        next_page=next_page,
        page_size=page_size,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    body: ExecuteQueryRequest,
    next_page: Optional[str] = None,
    page_size: Optional[int] = None,
) -> Optional[Union[Any, DefaultError]]:
    """Search using SOQL

     Retrieve records by using Salesforce Object Query Language (SOQL)

    Args:
        next_page (Optional[str]): The Next page to get from set of bulk results
        page_size (Optional[int]): Page Size is optional. If not supplied the entire file is
            returned. Use this along with next page to paginate the bulk results. If paging is done
            results are always a JSON array
        body (ExecuteQueryRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, DefaultError]
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
            next_page=next_page,
            page_size=page_size,
        )
    ).parsed
