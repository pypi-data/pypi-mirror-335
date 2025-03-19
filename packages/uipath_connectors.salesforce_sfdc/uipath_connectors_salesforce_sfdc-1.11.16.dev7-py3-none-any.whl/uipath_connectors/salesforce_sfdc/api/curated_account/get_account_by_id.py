from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response
from ... import errors

from ...models.default_error import DefaultError
from ...models.get_account_by_id_response import GetAccountByIDResponse


def _get_kwargs(
    curated_account_id: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/curated_account/{curated_account_id}".format(
            curated_account_id=curated_account_id,
        ),
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[DefaultError, GetAccountByIDResponse]]:
    if response.status_code == 200:
        response_200 = GetAccountByIDResponse.from_dict(response.json())

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
) -> Response[Union[DefaultError, GetAccountByIDResponse]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    curated_account_id: str,
    curated_account_id_lookup: Any,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[Union[DefaultError, GetAccountByIDResponse]]:
    """Get Account

     Retrieve the information of an account

    Args:
        curated_account_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[DefaultError, GetAccountByIDResponse]]
    """

    if not curated_account_id and curated_account_id_lookup:
        filter = curated_account_id_lookup
        lookup_response_raw = client.get_httpx_client().request(
            method="get",
            url=f"/curated_account?fields=Name,Id?where=Name like '%{filter}%'",
        )
        lookup_response = lookup_response_raw.json()

        found_items = lookup_response

        if not found_items:
            raise ValueError(
                "No matches found for curated_account_id_lookup in curated_account"
            )
        if len(found_items) > 1:
            print(
                "Warning: Multiple matches found for curated_account_id_lookup in curated_account. Using the first match."
            )

        curated_account_id = found_items[0]["Id"]

    kwargs = _get_kwargs(
        curated_account_id=curated_account_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    curated_account_id: str,
    curated_account_id_lookup: Any,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[Union[DefaultError, GetAccountByIDResponse]]:
    """Get Account

     Retrieve the information of an account

    Args:
        curated_account_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[DefaultError, GetAccountByIDResponse]
    """

    return sync_detailed(
        curated_account_id=curated_account_id,
        curated_account_id_lookup=curated_account_id_lookup,
        client=client,
    ).parsed


async def asyncio_detailed(
    curated_account_id: str,
    curated_account_id_lookup: Any,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[Union[DefaultError, GetAccountByIDResponse]]:
    """Get Account

     Retrieve the information of an account

    Args:
        curated_account_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[DefaultError, GetAccountByIDResponse]]
    """

    if not curated_account_id and curated_account_id_lookup:
        filter = curated_account_id_lookup
        lookup_response_raw = await client.get_async_httpx_client().request(
            method="get",
            url=f"/curated_account?fields=Name,Id?where=Name like '%{filter}%'",
        )
        lookup_response = lookup_response_raw.json()

        found_items = lookup_response

        if not found_items:
            raise ValueError(
                "No matches found for curated_account_id_lookup in curated_account"
            )
        if len(found_items) > 1:
            print(
                "Warning: Multiple matches found for curated_account_id_lookup in curated_account. Using the first match."
            )

        curated_account_id = found_items[0]["Id"]

    kwargs = _get_kwargs(
        curated_account_id=curated_account_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    curated_account_id: str,
    curated_account_id_lookup: Any,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[Union[DefaultError, GetAccountByIDResponse]]:
    """Get Account

     Retrieve the information of an account

    Args:
        curated_account_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[DefaultError, GetAccountByIDResponse]
    """

    return (
        await asyncio_detailed(
            curated_account_id=curated_account_id,
            curated_account_id_lookup=curated_account_id_lookup,
            client=client,
        )
    ).parsed
