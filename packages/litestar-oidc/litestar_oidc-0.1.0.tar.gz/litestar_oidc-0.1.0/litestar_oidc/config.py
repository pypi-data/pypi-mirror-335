import dataclasses
from typing import Optional, Tuple


@dataclasses.dataclass(frozen=True)
class OIDCCredentials:
    client_id: str
    client_secret: str


@dataclasses.dataclass(frozen=True)
class OIDCProvider:
    name: str
    discovery_endpoint: str
    credentials: OIDCCredentials


@dataclasses.dataclass(frozen=True)
class OIDCPluginConfig:
    providers: Tuple[OIDCProvider, ...]

    register_router: bool = True
    post_logout_redirect_uri: Optional[str] = None
