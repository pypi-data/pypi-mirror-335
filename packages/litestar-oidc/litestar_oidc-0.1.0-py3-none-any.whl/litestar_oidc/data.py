import dataclasses
from typing import Any, Dict, Optional, cast


@dataclasses.dataclass(frozen=True)
class Token:
    access_token: str
    token_type: str
    scope: str
    expires_in: int
    id_token: str


class UserInfo:
    def __init__(self, scopes: Dict[str, Any]):
        self.scopes = scopes

    @property
    def sub(self) -> Optional[str]:
        return self.scopes.get("sub")

    @property
    def iss(self) -> Optional[str]:
        return self.scopes.get("iss")

    @property
    def name(self) -> str:
        return cast(str, self.get_required_scope("name"))

    @property
    def email(self) -> str:
        return cast(str, self.get_required_scope("email"))

    def get_required_scope(self, name: str) -> Any:
        try:
            value = self.scopes["name"]

            if value is None:
                raise KeyError(name)
        except KeyError as e:
            raise AttributeError(f"{self.__class__.__name__} object has no attribute '{name}'") from e
