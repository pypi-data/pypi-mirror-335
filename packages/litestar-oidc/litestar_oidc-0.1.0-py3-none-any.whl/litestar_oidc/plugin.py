import dataclasses

from litestar import Request
from litestar.config.app import AppConfig
from litestar.di import Provide
from litestar.exceptions.http_exceptions import NotAuthorizedException
from litestar.plugins import InitPluginProtocol
from litestar.response import Redirect

from litestar_oidc.config import OIDCPluginConfig
from litestar_oidc.routers import oidc_router

from .providers import make_oidc_provider


def redirect_to_login(request: Request, _: Exception) -> Redirect:
    login_url = request.url_for("oidc:login")

    return Redirect(login_url)


@dataclasses.dataclass(frozen=True)
class OIDCInitPlugin(InitPluginProtocol):
    config: OIDCPluginConfig

    def on_app_init(self, app_config: AppConfig) -> AppConfig:
        app_config.dependencies.update(
            {
                "oidc": Provide(make_oidc_provider(self.config.providers)),
                "oidc_plugin_config": Provide(lambda: self.config, sync_to_thread=False),
            }
        )

        app_config.exception_handlers.setdefault(NotAuthorizedException, redirect_to_login)

        if self.config.register_router:
            app_config.route_handlers.append(oidc_router)

        return app_config
