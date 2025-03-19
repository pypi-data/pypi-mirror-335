import secrets

from litestar import Request, get, post, status_codes
from litestar.response import Redirect

from .config import OIDCPluginConfig
from .exceptions import StateMismatchException
from .services import OIDCService


@get("/login/{provider:str}", name="oidc:login")
async def login(request: Request, provider: str, oidc: OIDCService) -> Redirect:
    request.session["state"] = state = secrets.token_urlsafe(32)
    authorization_url = oidc.authorization_url(
        state=state,
        redirect_uri=request.url_for("oidc:callback", provider=provider),
    )

    return Redirect(authorization_url)


@get("/callback/{provider:str}", name="oidc:callback")
async def callback(request: Request, provider: str, oidc: OIDCService) -> Redirect:
    state = request.session.pop("state", None)
    if state != request.query_params["state"]:
        raise StateMismatchException

    token = await oidc.exchange_code_for_token(
        code=request.query_params["code"],
        redirect_uri=request.url_for("oidc:callback", provider=provider),
    )

    request.session["oidc"] = {
        "token": token,
        "provider": provider,
    }
    request.session["token"] = token
    next_url = request.session.pop("_next", "/")

    return Redirect(next_url)


@post("/logout", name="oidc:logout", sync_to_thread=False)
def logout_shortcut(request: Request) -> Redirect:
    real_logout_url = request.url_for("oidc:logout", provider=request.session["oidc"]["provider"])

    return Redirect(real_logout_url, status_code=status_codes.HTTP_303_SEE_OTHER)


@post(
    "/logout/{provider:str}",
    name="oidc:logout:provider",
    opt={"exclude_from_auth": False},
    sync_to_thread=False,
)
def logout(request: Request, oidc: OIDCService, oidc_plugin_config: OIDCPluginConfig) -> Redirect:
    logout_url = oidc.logout_url(
        token=request.auth,
        post_logout_redirect_uri=oidc_plugin_config.post_logout_redirect_uri,
    )

    return Redirect(logout_url, status_code=status_codes.HTTP_303_SEE_OTHER)
