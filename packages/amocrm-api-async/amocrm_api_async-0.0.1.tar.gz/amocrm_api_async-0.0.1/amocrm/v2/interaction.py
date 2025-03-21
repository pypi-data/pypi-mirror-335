from typing import Tuple

import aiohttp

from . import exceptions
from .filters import Filter
from .tokens import default_token_manager


class BaseInteraction:
    _default_headers = {
        "User-Agent": "amocrm-py/v2",
    }

    def __init__(
        self,
        token_manager=default_token_manager,
        headers=_default_headers,
    ):
        self._token_manager = token_manager
        self._default_headers = headers

    async def get_headers(self):
        headers = {}
        headers.update(self._default_headers)
        headers.update(await self._get_auth_headers())
        return headers

    async def _get_auth_headers(self):
        return {"Authorization": "Bearer " + await self._token_manager.get_access_token()}

    def _get_url(self, path):
        return "https://{subdomain}.amocrm.ru/api/v4/{path}".format(
            subdomain=self._token_manager.subdomain, path=path
        )

    async def _request(self, method, path, data=None, params=None, headers=None):
        headers = headers or {}
        headers.update(await self.get_headers())
        try:
            async with aiohttp.ClientSession(headers=headers) as session:
                response = await session.request(
                    method, url=self._get_url(path), json=data, params={k : v or "" for k, v in params.items()}
                )
        except aiohttp.ClientConnectionError as e:
            raise exceptions.AmoApiException(
                e.args[0].args[0]
            )  # Sometimes Connection aborted.
        if response.status == 204:
            return None, 204
        if response.status < 300 or response.status == 400:
            return await response.json(), response.status
        if response.status == 401:
            raise exceptions.UnAuthorizedException()
        if response.status == 403:
            raise exceptions.PermissionsDenyException()
        if response.status == 402:
            raise ValueError("Тариф не позволяет включать покупателей")
        raise exceptions.AmoApiException(
            "Wrong status {} ({})".format(response.status, await response.text)
        )

    async def request(
        self, method, path, data=None, params=None, headers=None, include=None
    ):
        params = params or {}
        if include:
            params["with"] = ",".join(include)
        return await self._request(
            method, path, data=data, params=params, headers=headers
        )

    async def _list(
        self,
        path,
        page,
        include=None,
        limit=250,
        query=None,
        filters: Tuple[Filter] = (),
        order=None,
    ):
        assert order is None or len(order) == 1
        assert limit <= 250
        params = {
            "page": page,
            "limit": limit,
            "query": query,
        }
        if order:
            field, value = list(order.items())[0]
            params["order[{}]".format(field)] = value
        for _filter in filters:
            params.update(_filter._as_params())
        return await self.request("get", path, params=params, include=include)

    async def _all(
        self,
        path,
        include=None,
        query=None,
        filters: Tuple[Filter] = (),
        order=None,
        limit=250,
    ):
        page = 1
        while True:
            response, _ = await self._list(
                path,
                page,
                include=include,
                query=query,
                filters=filters,
                order=order,
                limit=limit,
            )
            if response is None:
                return
            yield response["_embedded"]
            if "next" not in response.get("_links", []):
                return
            page += 1


class GenericInteraction(BaseInteraction):
    path = ""
    field = None

    def __init__(self, *args, path=None, field=None, **kwargs):
        super().__init__(*args, **kwargs)
        if path is not None:
            self.path = path
        if field is not None:
            self.field = field

    def _get_field(self):
        return self.field or self.path

    def _get_path(self):
        return self.path

    async def get_list(
        self, page, include=None, limit=250, query=None, filters=None, order=None
    ):
        response, _ = await self._list(
            self._get_path(),
            page,
            include=include,
            limit=limit,
            query=query,
            filters=filters,
            order=order,
        )
        return response["_embedded"][self._get_field()]

    async def get_all(self, include=None, query=None, filters=(), order=None):
        async for data in self._all(
            self._get_path(), include=include, query=query, filters=filters, order=order
        ):
            for i in data[self._get_field()]:
                yield i

    async def get(self, object_id, include=None):
        path = "{}/{}".format(self._get_path(), object_id)
        response, status = await self.request("get", path, include=include)
        if status == 204:
            raise exceptions.NotFound()
        return response

    async def create(self, data):
        response, status = await self.request("post", self._get_path(), data=[data])
        if status == 400:
            raise exceptions.ValidationError(response)
        return response["_embedded"][self._get_field()][0]

    async def update(self, object_id, data):
        path = "{}/{}".format(self._get_path(), object_id)
        response, status = await self.request("patch", path, data=data)
        if status == 400:
            raise exceptions.ValidationError(response)
        return response
