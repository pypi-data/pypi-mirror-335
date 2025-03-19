from __future__ import annotations

from typing import Any

from litestar.connection import ASGIConnection
from litestar.middleware.authentication import (
    AuthenticationResult,
)
from litestar.security.session_auth import SessionAuthMiddleware

from litestar_oidc.data import Token


class OIDCSessionAuthMiddleware(SessionAuthMiddleware):
    async def authenticate_request(self, connection: ASGIConnection[Any, Any, Any, Any]) -> AuthenticationResult:
        auth_result = await super().authenticate_request(connection)

        token = Token(**auth_result.auth["oidc"]["token"])

        return AuthenticationResult(user=auth_result.user, auth=token)
