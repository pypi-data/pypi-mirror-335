from typing import TYPE_CHECKING, Optional
from typing_extensions import Self

if TYPE_CHECKING:
    from tiptree.client import TiptreeClient


class ClientBind:
    @property
    def client(self) -> Optional["TiptreeClient"]:
        return getattr(self, "__client", None)

    @client.setter
    def client(self, value: "TiptreeClient"):
        setattr(self, "__client", value)

    def bind_client(self, client: "TiptreeClient") -> Self:
        self.client = client
        return self

    def ensure_client_bound(self) -> Self:
        client = self.client
        if client is None:
            raise ValueError("Client not bound to instance")
        return self
