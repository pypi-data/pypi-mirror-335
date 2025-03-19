from typing import TypedDict


class LitestarOIDCException(Exception): ...


class StateMismatchException(LitestarOIDCException): ...


class ErrorResponse(TypedDict):
    error: str
    error_description: str


class TokenException(LitestarOIDCException): ...


class InvalidGrant(TokenException): ...


def to_exception(payload: ErrorResponse) -> LitestarOIDCException:
    map = {
        "invalid_grant": InvalidGrant,
    }

    if payload["error"] not in map:
        return TokenException(payload["error_description"])

    return map[payload["error"]](payload["error_description"])
