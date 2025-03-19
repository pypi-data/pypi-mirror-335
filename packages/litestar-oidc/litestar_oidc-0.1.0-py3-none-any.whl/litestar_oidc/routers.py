from litestar import Router

from .handlers import callback, login, logout, logout_shortcut

oidc_router = Router(
    path="/_",
    route_handlers=[login, logout, callback, logout_shortcut],
    opt={"exclude_from_auth": True},
)
