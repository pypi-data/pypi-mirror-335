import dataclasses
import urllib.parse
from typing import Dict, List, Optional, Tuple, cast

import httpx
import jwt
from jwt.algorithms import RSAAlgorithm
from jwt.exceptions import InvalidTokenError

from .config import OIDCCredentials
from .data import Token
from .exceptions import to_exception


@dataclasses.dataclass(frozen=True)
class WellKnownConfig:
    issuer: str
    authorization_endpoint: str
    token_endpoint: str
    jwks_uri: str
    response_types_supported: List[str]
    grant_types_supported: List[str]
    id_token_signing_alg_values_supported: List[str]
    scopes_supported: List[str]
    claims_supported: List[str]
    userinfo_endpoint: Optional[str] = None
    end_session_endpoint: Optional[str] = None
    introspection_endpoint: Optional[str] = None
    revocation_endpoint: Optional[str] = None
    device_authorization_endpoint: Optional[str] = None
    response_modes_supported: Optional[List[str]] = None
    id_token_encryption_alg_values_supported: Optional[List[str]] = None
    id_token_encryption_enc_values_supported: Optional[List[str]] = None
    subject_types_supported: List[str] = dataclasses.field(default_factory=lambda: ["public"])
    token_endpoint_auth_methods_supported: Optional[List[str]] = None
    acr_values_supported: Optional[List[str]] = None
    request_parameter_supported: bool = False
    claims_parameter_supported: bool = False
    code_challenge_methods_supported: Optional[List[str]] = None
    mtls_endpoint_aliases: Optional[Dict[str, str]] = None
    service_documentation: Optional[str] = None
    op_policy_uri: Optional[str] = None
    op_tos_uri: Optional[str] = None


DEFAULT_SCOPES = tuple(
    [
        "openid",
        "profile",
        "entitlements",
    ]
)


@dataclasses.dataclass
class OIDCService:
    config: WellKnownConfig
    credentials: OIDCCredentials

    _jwks: Optional[dict] = None

    def authorization_url(self, state: str, redirect_uri: str, scopes: Tuple[str, ...] = DEFAULT_SCOPES) -> str:
        query = {
            "redirect_uri": redirect_uri,
            "state": state,
            "scope": " ".join(scopes),
            "client_id": self.credentials.client_id,
            "response_type": "code",
        }

        return self.config.authorization_endpoint + "?" + urllib.parse.urlencode(query)

    def logout_url(self, token: Token, post_logout_redirect_uri: Optional[str] = None) -> str:
        if self.config.end_session_endpoint is None:
            raise ValueError(
                "Cannot build logout URL without end_session_endpoint in the well known config, "
                "is logout supported by the provider?"
            )
        query = {
            "id_token_hint": token.id_token,
            "client_id": self.credentials.client_id,
        }

        if post_logout_redirect_uri is not None:
            query["post_logout_redirect_uri"] = post_logout_redirect_uri

        return self.config.end_session_endpoint + "?" + urllib.parse.urlencode(query)

    async def exchange_code_for_token(
        self, code: str, redirect_uri: str, scopes: Tuple[str, ...] = DEFAULT_SCOPES
    ) -> Token:
        payload = {
            "client_id": self.credentials.client_id,
            "client_secret": self.credentials.client_secret,
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri,
            "scope": " ".join(scopes),
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.config.token_endpoint,
                data=payload,
                headers={
                    "Content-Type": "application/x-www-form-urlencoded",
                },
            )

        if response.status_code != 200:
            raise to_exception(response.json())

        return Token(**response.json())

    async def user_info(self, token: Token) -> dict:
        jwks = await self.fetch_jwks()

        unverified_header = jwt.get_unverified_header(token.id_token)
        rsa_key = {}
        for key in jwks["keys"]:
            if key["kid"] == unverified_header["kid"]:
                rsa_key = {
                    "kty": key["kty"],
                    "kid": key["kid"],
                    "use": key["use"],
                    "n": key["n"],
                    "e": key["e"],
                }

        if not rsa_key:
            raise InvalidTokenError("Unable to find appropriate key")

        return cast(
            dict,
            jwt.decode(
                token.id_token,
                key=RSAAlgorithm.from_jwk(rsa_key),
                algorithms=self.config.id_token_signing_alg_values_supported,
                audience=self.credentials.client_id,
                issuer=self.config.issuer,
            ),
        )

    async def fetch_jwks(self) -> dict:
        if self._jwks:
            return self._jwks

        async with httpx.AsyncClient() as client:
            response = await client.get(self.config.jwks_uri)
            response.raise_for_status()

            return cast("dict", response.json())
