from typing import Awaitable, Callable, Dict, Tuple

import httpx

from .config import OIDCProvider
from .services import OIDCService, WellKnownConfig


def make_oidc_provider(
    providers: Tuple[OIDCProvider, ...],
) -> Callable[..., Awaitable[OIDCService]]:
    provider_map: Dict[str, OIDCProvider] = {provider.name: provider for provider in providers}

    async def oidc_provider(provider: str) -> OIDCService:
        provider_config = provider_map[provider]

        async with httpx.AsyncClient() as client:
            response = await client.get(provider_config.discovery_endpoint)
            config = WellKnownConfig(**response.json())

        return OIDCService(config, provider_config.credentials)

    return oidc_provider
