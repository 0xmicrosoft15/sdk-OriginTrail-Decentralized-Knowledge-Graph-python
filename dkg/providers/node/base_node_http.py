from abc import ABC, abstractmethod
from dkg.dataclasses import HTTPRequestMethod, NodeResponseDict
from typing import Any
from dkg.types import URI


class BaseNodeHTTPProvider(ABC):
    def __init__(
        self,
        endpoint_uri: URI | str,
        api_version: str = "v1",
        auth_token: str | None = None,
    ):
        self.url = f"{URI(endpoint_uri)}/{api_version}"
        self.headers = {"Authorization": f"Bearer {auth_token}"} if auth_token else {}

    @abstractmethod
    async def make_request(
        self,
        method: HTTPRequestMethod,
        path: str,
        params: dict[str, Any] = {},
        data: dict[str, Any] = {},
    ) -> NodeResponseDict:
        raise NotImplementedError("Subclasses must implement make_request")
