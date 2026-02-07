"""Sample API Client."""

from __future__ import annotations

import socket
from typing import Any

import aiohttp
import async_timeout


class MyWaterApiClientError(Exception):
    """Exception to indicate a general API error."""


class MyWaterApiClientCommunicationError(
    MyWaterApiClientError,
):
    """Exception to indicate a communication error."""


class MyWaterApiClientAuthenticationError(
    MyWaterApiClientError,
):
    """Exception to indicate an authentication error."""


def _verify_response_or_raise(response: aiohttp.ClientResponse) -> None:
    """Verify that the response is valid."""
    if response.status in (401, 403):
        msg = "Invalid credentials"
        raise MyWaterApiClientAuthenticationError(
            msg,
        )
    response.raise_for_status()


class MyWaterApiClient:
    """Sample API Client."""

    def __init__(
        self,
        api_username: str,
        api_password: str,
        user_username: str,
        user_password: str,
        session: aiohttp.ClientSession,
    ) -> None:
        """Sample API Client."""
        self._api_username = api_username
        self._api_password = api_password
        self._user_username = user_username
        self._user_password = user_password
        self._session = session

    async def async_get_data(self) -> Any:
        """Get data from the API."""
        return await self._api_wrapper(
            method="get",
            url="https://jsonplaceholder.typicode.com/posts/1",
        )

    async def async_set_title(self, value: str) -> Any:
        """Get data from the API."""
        return await self._api_wrapper(
            method="patch",
            url="https://jsonplaceholder.typicode.com/posts/1",
            data={"title": value},
            headers={"Content-type": "application/json; charset=UTF-8"},
        )

    async def _api_wrapper(
        self,
        method: str,
        url: str,
        data: dict | None = None,
        headers: dict | None = None,
    ) -> Any:
        """Get information from the API."""
        try:
            async with async_timeout.timeout(10):
                response = await self._session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=data,
                )
                _verify_response_or_raise(response)
                return await response.json()

        except TimeoutError as exception:
            msg = f"Timeout error fetching information - {exception}"
            raise MyWaterApiClientCommunicationError(
                msg,
            ) from exception
        except (aiohttp.ClientError, socket.gaierror) as exception:
            msg = f"Error fetching information - {exception}"
            raise MyWaterApiClientCommunicationError(
                msg,
            ) from exception
        except Exception as exception:  # pylint: disable=broad-except
            msg = f"Something really wrong happened! - {exception}"
            raise MyWaterApiClientError(
                msg,
            ) from exception

    async def _get_api_token(self, url: str) -> None:
        async with (
            aiohttp.ClientSession(
                auth=aiohttp.BasicAuth(
                    login=self._api_username, password=self._api_password
                )
            ) as token_session,
            async_timeout.timeout(10),
        ):
            response = await token_session.request(method="POST", url=url)

    async def check_api_token(self, api_token: str | None = None) -> bool:
        """Check if the API token is valid."""
        if api_token is not None:
            self._api_token = api_token
        return True
