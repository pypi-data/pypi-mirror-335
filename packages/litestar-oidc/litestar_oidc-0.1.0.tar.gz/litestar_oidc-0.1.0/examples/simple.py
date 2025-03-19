import os

import uvicorn
from litestar import Litestar, Request, get
from litestar.datastructures.state import State
from litestar.exceptions.http_exceptions import NotAuthorizedException
from litestar.middleware.session.client_side import CookieBackendConfig
from litestar.response import Redirect
from litestar.security.session_auth import SessionAuth
from typing_extensions import TypeAlias

from litestar_oidc.auth import retrieve_user_handler
from litestar_oidc.config import OIDCCredentials, OIDCPluginConfig, OIDCProvider
from litestar_oidc.data import Token, UserInfo
from litestar_oidc.middleware import OIDCSessionAuthMiddleware
from litestar_oidc.plugin import OIDCInitPlugin

RequestT: TypeAlias = Request[UserInfo, Token, State]


@get(path="/")
def index(request: RequestT) -> str:
    return f"Hello, {request.user.name}!"


def redirect_to_login(request: Request, _: Exception) -> Redirect:
    # Since only a single provider is configured, we can hardcode the provider name
    # This could be loaded from a configuration or user input. Eg: via a selection view.
    login_url = request.url_for("oidc:login", provider="authentik")

    return Redirect(login_url)


def create_app() -> Litestar:
    session_config = CookieBackendConfig(secret=os.environ["APP__SECRET_KEY"].encode())

    # TODO: Can this be moved to the plugin? session_config is not hashable which is a problem in the plugin registry
    session_auth = SessionAuth(
        retrieve_user_handler=retrieve_user_handler,
        session_backend_config=session_config,
        authentication_middleware_class=OIDCSessionAuthMiddleware,
    )  # type: ignore[var-annotated]

    return Litestar(
        debug=True,
        route_handlers=[index],
        on_app_init=[
            session_auth.on_app_init,
        ],
        exception_handlers={
            NotAuthorizedException: redirect_to_login,
        },
        plugins=[
            OIDCInitPlugin(
                config=OIDCPluginConfig(
                    providers=tuple(
                        [
                            OIDCProvider(
                                name="authentik",
                                discovery_endpoint=os.environ["APP__OIDC__AUTHENTIK__DISCOVERY_ENDPOINT"],
                                credentials=OIDCCredentials(
                                    client_id=os.environ["APP__OIDC__AUTHENTIK__CLIENT_ID"],
                                    client_secret=os.environ["APP__OIDC__AUTHENTIK__CLIENT_SECRET"],
                                ),
                            )
                        ],
                    ),
                ),
            )
        ],
        middleware=[
            session_config.middleware,
        ],
    )


if __name__ == "__main__":
    uvicorn.run(create_app())
