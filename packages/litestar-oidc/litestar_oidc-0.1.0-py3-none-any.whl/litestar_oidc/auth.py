from typing import Any, Dict, Optional

from jwt.exceptions import InvalidTokenError
from litestar.connection import ASGIConnection
from litestar.exceptions import NotAuthorizedException

from .data import Token, UserInfo
from .plugin import OIDCInitPlugin
from .providers import make_oidc_provider
from .services import OIDCService


async def retrieve_user_handler(
    session: Dict[str, Any],
    connection: ASGIConnection[Any, Any, Any, Any],
) -> Optional[UserInfo]:
    oidc_data = session.get("oidc", None)
    if oidc_data is None:
        return None

    token = Token(**oidc_data["token"])
    plugin = connection.app.plugins.get(OIDCInitPlugin)

    oidc: OIDCService = await make_oidc_provider(
        plugin.config.providers,
    )(provider=oidc_data["provider"])

    try:
        claims = await oidc.user_info(token)
    except InvalidTokenError as e:
        raise NotAuthorizedException("Unable to decode token") from e

    return UserInfo(claims)
