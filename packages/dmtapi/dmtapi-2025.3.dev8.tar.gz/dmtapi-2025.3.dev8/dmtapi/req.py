from typing import Union, Any, Optional
from urllib.parse import urlencode

import httpx


class RequestMaker:
    def __init__(self, api_base_url: str):
        self.api_base_url = api_base_url
        self.client = httpx.AsyncClient(
            timeout=60,
            headers={"Accept-Encoding": "gzip", "Content-Type": "application/json"},
            http2=True
        )

    def build_url(self, url: str, params: Optional[dict] = None) -> str:
        url = f"{self.api_base_url}{url}"
        if not params:
            return url
        filtered_params = {k: v for k, v in params.items() if v is not None}
        return f"{url}?{urlencode(filtered_params)}"

    @staticmethod
    def get_headers(
        *,
        extra_headers: Optional[dict] = None,
        access_token: Optional[str] = None,
        login: Optional[int] = None,
        server: Optional[str] = None,
        api_key: Optional[str] = None,
    ) -> dict:
        headers = {}

        if access_token:
            headers["ACCESS-TOKEN"] = access_token

        if login and server:
            headers["TRADER-LOGIN"] = str(login)
            headers["TRADER-SERVER"] = server

        if api_key:
            headers["USER-API-KEY"] = api_key

        if extra_headers:
            headers.update(extra_headers)

        return headers

    async def get(
        self,
        *,
        path: str,
        params: Optional[dict[str, str]] = None,
        extra_headers: Optional[dict] = None,
        access_token: Optional[str] = None,
        login: Optional[int] = None,
        server: Optional[str] = None,
        api_key: Optional[str] = None,
    ) -> Any:
        full_url = self.build_url(path, params)
        headers = self.get_headers(
            extra_headers=extra_headers,
            access_token=access_token,
            login=login,
            server=server,
            api_key=api_key,
        )

        response = await self.client.get(full_url, headers=headers)
        if response.status_code == 422:
            raise ValueError(response.json())
        elif response.status_code == 400:
            raise ValueError(response.text)

        response.raise_for_status()
        return response.json()

    async def post(
        self,
        *,
        path: str,
        params: Optional[dict[str, str]] = None,
        data: Optional[Union[dict, str]] = None,
        json: Optional[Union[dict, str]] = None,
        extra_headers: Optional[dict] = None,
        access_token: Optional[str] = None,
        login: Optional[int] = None,
        server: Optional[str] = None,
        api_key: Optional[str] = None,
    ) -> Any:
        full_url = self.build_url(path, params)
        headers = self.get_headers(
            extra_headers=extra_headers,
            access_token=access_token,
            login=login,
            server=server,
            api_key=api_key,
        )

        response = await self.client.post(
            full_url, data=data, json=json, headers=headers
        )
        if response.status_code == 422:
            raise ValueError(response.json())
        elif response.status_code == 400:
            raise ValueError(response.text)

        response.raise_for_status()
        return response.json()

    async def close_http_client(self):
        """Properly close the session when done."""
        await self.client.aclose()
