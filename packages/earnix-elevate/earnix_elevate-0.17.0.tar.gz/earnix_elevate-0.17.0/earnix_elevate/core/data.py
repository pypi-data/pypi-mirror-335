from typing import Any

from ..clients.data import ApiClient, Configuration, DataTableServiceApi
from .auth import AuthClient, inject_auth_header_injector
from .const import API_CLIENT_CONF_KEY, SERVER_TPL, USER_AGENT


class DataClient(ApiClient):
    _route = "/api/data"

    @property
    def auth(self) -> AuthClient:
        return self._auth

    @auth.setter
    def auth(self, auth_client: AuthClient) -> None:
        self._auth = auth_client

    def __init__(self, server: str, *args: Any, **kwargs: Any) -> None:
        base_url = SERVER_TPL.format(server) + self.__class__._route
        kwargs[API_CLIENT_CONF_KEY] = Configuration(host=base_url)
        super().__init__(*args, **kwargs)
        self.user_agent = USER_AGENT


class DataTableService(DataTableServiceApi):
    def __init__(
        self,
        server: str,
        client_id: str,
        secret_key: str,
    ) -> None:
        self.api_client = DataClient(server)
        self.api_client.auth = AuthClient(server, client_id, secret_key)
        inject_auth_header_injector(holder=self)
