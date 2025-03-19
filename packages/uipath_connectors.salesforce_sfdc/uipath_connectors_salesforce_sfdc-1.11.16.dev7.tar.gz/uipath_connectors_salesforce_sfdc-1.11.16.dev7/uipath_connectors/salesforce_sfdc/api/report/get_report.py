from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response
from ... import errors

from ...models.default_error import DefaultError
from ...models.get_report_response import GetReportResponse


def _get_kwargs(
    report_id: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/report/{report_id}".format(
            report_id=report_id,
        ),
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[DefaultError, GetReportResponse]]:
    if response.status_code == 200:
        response_200 = GetReportResponse.from_dict(response.json())

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
) -> Response[Union[DefaultError, GetReportResponse]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    report_id: str,
    report_id_lookup: Any,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[Union[DefaultError, GetReportResponse]]:
    """Get Report

     Runs a report immediately and returns the latest summary data

    Args:
        report_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[DefaultError, GetReportResponse]]
    """

    if not report_id and report_id_lookup:
        lookup_response_raw = client.get_httpx_client().request(
            method="get", url="/reports"
        )
        lookup_response = lookup_response_raw.json()

        found_items = []
        for item in lookup_response:
            if report_id_lookup in item["id"] or report_id_lookup in item["name"]:
                found_items.append(item)

        if not found_items:
            raise ValueError("No matches found for report_id_lookup in reports")
        if len(found_items) > 1:
            print(
                "Warning: Multiple matches found for report_id_lookup in reports. Using the first match."
            )

        report_id = found_items[0]["id"]

    kwargs = _get_kwargs(
        report_id=report_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    report_id: str,
    report_id_lookup: Any,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[Union[DefaultError, GetReportResponse]]:
    """Get Report

     Runs a report immediately and returns the latest summary data

    Args:
        report_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[DefaultError, GetReportResponse]
    """

    return sync_detailed(
        report_id=report_id,
        report_id_lookup=report_id_lookup,
        client=client,
    ).parsed


async def asyncio_detailed(
    report_id: str,
    report_id_lookup: Any,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[Union[DefaultError, GetReportResponse]]:
    """Get Report

     Runs a report immediately and returns the latest summary data

    Args:
        report_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[DefaultError, GetReportResponse]]
    """

    if not report_id and report_id_lookup:
        lookup_response_raw = await client.get_async_httpx_client().request(
            method="get", url="/reports"
        )
        lookup_response = lookup_response_raw.json()

        found_items = []
        for item in lookup_response:
            if report_id_lookup in item["id"] or report_id_lookup in item["name"]:
                found_items.append(item)

        if not found_items:
            raise ValueError("No matches found for report_id_lookup in reports")
        if len(found_items) > 1:
            print(
                "Warning: Multiple matches found for report_id_lookup in reports. Using the first match."
            )

        report_id = found_items[0]["id"]

    kwargs = _get_kwargs(
        report_id=report_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    report_id: str,
    report_id_lookup: Any,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[Union[DefaultError, GetReportResponse]]:
    """Get Report

     Runs a report immediately and returns the latest summary data

    Args:
        report_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[DefaultError, GetReportResponse]
    """

    return (
        await asyncio_detailed(
            report_id=report_id,
            report_id_lookup=report_id_lookup,
            client=client,
        )
    ).parsed
