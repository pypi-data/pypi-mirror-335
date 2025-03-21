from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response
from ... import errors

from ...models.create_bulk_job_body import CreateBulkJobBody
from ...models.create_bulk_job_response import CreateBulkJobResponse
from ...models.default_error import DefaultError


def _get_kwargs(
    *,
    body: CreateBulkJobBody,
    column_delimiter: Optional[str] = "COMMA",
    line_ending: Optional[str] = "LF",
    operation: str,
    object_: str,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    params: dict[str, Any] = {}

    params["columnDelimiter"] = column_delimiter

    params["lineEnding"] = line_ending

    params["operation"] = operation

    params["object"] = object_

    params = {k: v for k, v in params.items() if v is not None}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/create_bulk_job",
        "params": params,
    }

    _body = body.to_multipart()

    _kwargs["files"] = _body

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[CreateBulkJobResponse, DefaultError]]:
    if response.status_code == 200:
        response_200 = CreateBulkJobResponse.from_dict(response.json())

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
) -> Response[Union[CreateBulkJobResponse, DefaultError]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: CreateBulkJobBody,
    column_delimiter: Optional[str] = "COMMA",
    line_ending: Optional[str] = "LF",
    operation: str,
    object_: str,
    object__lookup: Any,
) -> Response[Union[CreateBulkJobResponse, DefaultError]]:
    """Create Bulk Upload Job

     Create records asynchronously in bulk for a salesforce object by providing a CSV file

    Args:
        column_delimiter (Optional[str]): Column delimiter used in CSV file. Default is COMMA
            Default: 'COMMA'.
        line_ending (Optional[str]): Line ending used in CSV file, marking the end of a data row.
            Default is LF Default: 'LF'.
        operation (str): Type of CRUD operation to be performed
        object_ (str): Select any standard or custom object
        body (CreateBulkJobBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[CreateBulkJobResponse, DefaultError]]
    """

    if not object_ and object__lookup:
        lookup_response_raw = client.get_httpx_client().request(
            method="get", url="/standard-objects"
        )
        lookup_response = lookup_response_raw.json()

        found_items = []
        for item in lookup_response:
            if object__lookup in item["displayName"]:
                found_items.append(item)

        if not found_items:
            raise ValueError("No matches found for object__lookup in standard-objects")
        if len(found_items) > 1:
            print(
                "Warning: Multiple matches found for object__lookup in standard-objects. Using the first match."
            )

        object_ = found_items[0]["name"]

    kwargs = _get_kwargs(
        body=body,
        column_delimiter=column_delimiter,
        line_ending=line_ending,
        operation=operation,
        object_=object_,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: Union[AuthenticatedClient, Client],
    body: CreateBulkJobBody,
    column_delimiter: Optional[str] = "COMMA",
    line_ending: Optional[str] = "LF",
    operation: str,
    object_: str,
    object__lookup: Any,
) -> Optional[Union[CreateBulkJobResponse, DefaultError]]:
    """Create Bulk Upload Job

     Create records asynchronously in bulk for a salesforce object by providing a CSV file

    Args:
        column_delimiter (Optional[str]): Column delimiter used in CSV file. Default is COMMA
            Default: 'COMMA'.
        line_ending (Optional[str]): Line ending used in CSV file, marking the end of a data row.
            Default is LF Default: 'LF'.
        operation (str): Type of CRUD operation to be performed
        object_ (str): Select any standard or custom object
        body (CreateBulkJobBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[CreateBulkJobResponse, DefaultError]
    """

    return sync_detailed(
        client=client,
        body=body,
        column_delimiter=column_delimiter,
        line_ending=line_ending,
        operation=operation,
        object_=object_,
        object__lookup=object__lookup,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: CreateBulkJobBody,
    column_delimiter: Optional[str] = "COMMA",
    line_ending: Optional[str] = "LF",
    operation: str,
    object_: str,
    object__lookup: Any,
) -> Response[Union[CreateBulkJobResponse, DefaultError]]:
    """Create Bulk Upload Job

     Create records asynchronously in bulk for a salesforce object by providing a CSV file

    Args:
        column_delimiter (Optional[str]): Column delimiter used in CSV file. Default is COMMA
            Default: 'COMMA'.
        line_ending (Optional[str]): Line ending used in CSV file, marking the end of a data row.
            Default is LF Default: 'LF'.
        operation (str): Type of CRUD operation to be performed
        object_ (str): Select any standard or custom object
        body (CreateBulkJobBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[CreateBulkJobResponse, DefaultError]]
    """

    if not object_ and object__lookup:
        lookup_response_raw = await client.get_async_httpx_client().request(
            method="get", url="/standard-objects"
        )
        lookup_response = lookup_response_raw.json()

        found_items = []
        for item in lookup_response:
            if object__lookup in item["displayName"]:
                found_items.append(item)

        if not found_items:
            raise ValueError("No matches found for object__lookup in standard-objects")
        if len(found_items) > 1:
            print(
                "Warning: Multiple matches found for object__lookup in standard-objects. Using the first match."
            )

        object_ = found_items[0]["name"]

    kwargs = _get_kwargs(
        body=body,
        column_delimiter=column_delimiter,
        line_ending=line_ending,
        operation=operation,
        object_=object_,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    body: CreateBulkJobBody,
    column_delimiter: Optional[str] = "COMMA",
    line_ending: Optional[str] = "LF",
    operation: str,
    object_: str,
    object__lookup: Any,
) -> Optional[Union[CreateBulkJobResponse, DefaultError]]:
    """Create Bulk Upload Job

     Create records asynchronously in bulk for a salesforce object by providing a CSV file

    Args:
        column_delimiter (Optional[str]): Column delimiter used in CSV file. Default is COMMA
            Default: 'COMMA'.
        line_ending (Optional[str]): Line ending used in CSV file, marking the end of a data row.
            Default is LF Default: 'LF'.
        operation (str): Type of CRUD operation to be performed
        object_ (str): Select any standard or custom object
        body (CreateBulkJobBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[CreateBulkJobResponse, DefaultError]
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
            column_delimiter=column_delimiter,
            line_ending=line_ending,
            operation=operation,
            object_=object_,
            object__lookup=object__lookup,
        )
    ).parsed
