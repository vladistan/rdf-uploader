import enum
from abc import ABC, abstractmethod

import httpx


class EndpointType(str, enum.Enum):
    GENERIC = "generic"
    BLAZEGRAPH = "blazegraph"
    MARKLOGIC = "marklogic"
    NEPTUNE = "neptune"
    RDFOX = "rdfox"
    STARDOG = "stardog"


class EndpointStrategy(ABC):
    def __init__(
        self,
        endpoint_url: str,
        timeout: int = 60,
        username: str | None = None,
        password: str | None = None,
    ):
        self.endpoint_url = endpoint_url
        self.timeout = timeout
        self.username = username
        self.password = password

    @abstractmethod
    def get_upload_url(self, graph: str | None = None) -> str:
        pass

    @abstractmethod
    def get_params(self, graph: str | None = None) -> dict[str, str]:
        pass

    def get_auth(self) -> httpx.Auth | None:
        if not (self.username and self.password):
            return None
        return httpx.BasicAuth(self.username, self.password)

    async def upload(
        self,
        data: str,
        graph: str | None = None,
        content_type: str = "text/turtle",
    ) -> tuple[bool, int]:
        url = self.get_upload_url(graph)
        params = self.get_params(graph)
        headers = {"Content-Type": content_type}
        auth = self.get_auth()

        async with httpx.AsyncClient(timeout=self.timeout, auth=auth) as client:
            response = await client.post(
                url,
                params=params,
                content=data,
                headers=headers,
            )
            response.raise_for_status()
            return True, response.status_code


class BlazegraphEndpoint(EndpointStrategy):
    def get_upload_url(self, graph: str | None = None) -> str:
        return f"{self.endpoint_url}/sparql"

    def get_params(self, graph: str | None = None) -> dict[str, str]:
        params: dict[str, str] = {}
        if graph:
            params["context-uri"] = graph
        return params


class MarkLogicEndpoint(EndpointStrategy):
    def get_upload_url(self, graph: str | None = None) -> str:
        base_url = f"{self.endpoint_url}/v1/graphs"
        if graph:
            return f"{base_url}?graph={graph}"
        return f"{base_url}?default"

    def get_params(self, graph: str | None = None) -> dict[str, str]:
        return {}

    def get_auth(self) -> httpx.Auth | None:
        if not (self.username and self.password):
            return None
        return httpx.DigestAuth(self.username, self.password)


class NeptuneEndpoint(EndpointStrategy):
    def get_upload_url(self, graph: str | None = None) -> str:
        return f"{self.endpoint_url}/gsp/"

    def get_params(self, graph: str | None = None) -> dict[str, str]:
        if graph:
            return {"graph": graph}
        return {"default": ""}


class RDFoxEndpoint(EndpointStrategy):
    def __init__(
        self,
        endpoint_url: str,
        timeout: int = 60,
        username: str | None = None,
        password: str | None = None,
        store_name: str | None = None,
    ):
        super().__init__(endpoint_url, timeout, username, password)
        self.store_name = store_name

    def get_upload_url(self, graph: str | None = None) -> str:
        return f"{self.endpoint_url}/datastores/{self.store_name}/content"

    def get_params(self, graph: str | None = None) -> dict[str, str]:
        return {}


class StardogEndpoint(EndpointStrategy):
    def get_upload_url(self, graph: str | None = None) -> str:
        if graph:
            return f"{self.endpoint_url}?graph={graph}"
        return self.endpoint_url

    def get_params(self, graph: str | None = None) -> dict[str, str]:
        return {}


def create_endpoint_strategy(
    endpoint_type: EndpointType,
    endpoint_url: str,
    timeout: int = 60,
    username: str | None = None,
    password: str | None = None,
    store_name: str | None = None,
) -> EndpointStrategy:
    endpoint: EndpointStrategy
    if endpoint_type == EndpointType.BLAZEGRAPH:
        endpoint = BlazegraphEndpoint(endpoint_url, timeout, username, password)
    elif endpoint_type == EndpointType.MARKLOGIC:
        endpoint = MarkLogicEndpoint(endpoint_url, timeout, username, password)
    elif endpoint_type == EndpointType.NEPTUNE:
        endpoint = NeptuneEndpoint(endpoint_url, timeout, username, password)
    elif endpoint_type == EndpointType.RDFOX:
        endpoint = RDFoxEndpoint(endpoint_url, timeout, username, password, store_name)
    elif endpoint_type == EndpointType.STARDOG:
        endpoint = StardogEndpoint(endpoint_url, timeout, username, password)
    return endpoint


class EndpointClient:
    def __init__(
        self,
        endpoint_url: str,
        endpoint_type: EndpointType = EndpointType.GENERIC,
        timeout: int = 60,
        username: str | None = None,
        password: str | None = None,
        content_type: str | None = None,
        store_name: str | None = None,
    ) -> None:
        self._endpoint_type = endpoint_type
        self._endpoint_url = endpoint_url
        self._timeout: int = timeout
        self._username: str | None = username
        self._password: str | None = password
        self._store_name: str | None = store_name
        self.content_type: str | None = content_type

        self.endpoint_strategy = create_endpoint_strategy(
            endpoint_type=endpoint_type,
            endpoint_url=endpoint_url,
            timeout=timeout,
            username=username,
            password=password,
            store_name=store_name,
        )

    @property
    def endpoint_url(self) -> str:
        return self._endpoint_url

    @property
    def endpoint_type(self) -> EndpointType:
        return self._endpoint_type

    @property
    def timeout(self) -> int:
        return self._timeout

    @property
    def username(self) -> str | None:
        return self._username

    @property
    def password(self) -> str | None:
        return self._password

    @property
    def store_name(self) -> str | None:
        return self._store_name

    async def upload_data(
        self,
        data: str,
        graph: str | None = None,
        content_type: str | None = None,
    ) -> tuple[bool, int]:
        actual_content_type = content_type or self.content_type or "text/turtle"

        return await self.endpoint_strategy.upload(
            data=data,
            graph=graph,
            content_type=actual_content_type,
        )
