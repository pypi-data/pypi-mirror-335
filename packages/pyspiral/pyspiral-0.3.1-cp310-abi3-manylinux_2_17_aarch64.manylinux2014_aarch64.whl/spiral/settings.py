import functools
import hashlib
import os
from collections.abc import Callable, Mapping
from pathlib import Path
from typing import Any

import jwt
import typer
from pydantic import BaseModel, Field
from pydantic_settings import (
    BaseSettings,
    InitSettingsSource,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    TomlConfigSettingsSource,
)

from spiral.api import SpiralAPI
from spiral.authn.authn import (
    DeviceAuthProvider,
    EnvironmentAuthn,
    FallbackAuthn,
    TokenAuthn,
    TokenExchangeProvider,
)
from spiral.authn.device import DeviceAuth
from spiral.authn.github_ import GitHubActionsProvider
from spiral.authn.modal_ import ModalProvider

DEV = "PYTEST_VERSION" in os.environ or bool(os.environ.get("SPIRAL_DEV", None))
FILE_FORMAT = os.environ.get("SPIRAL_FILE_FORMAT", "parquet")

APP_DIR = Path(typer.get_app_dir("pyspiral"))
LOG_DIR = APP_DIR / "logs"
CONFIG_FILE = APP_DIR / "config.toml"


class AuthSettings(BaseSettings):
    model_config = SettingsConfigDict(frozen=True)

    domain: str = "https://device.spiraldb.com"
    client_id: str = "client_01J1CRS967RFQY7JSE8XZ44ATR" if DEV else "client_01J1CRS9MGF103FKTKZDCNJVM3"


class AccessToken(BaseModel):
    token: str

    @functools.cached_property
    def payload(self) -> dict:
        return jwt.decode(self.token, options={"verify_signature": False})


class SpiralDBSettings(BaseSettings):
    model_config = SettingsConfigDict(frozen=True)

    host: str = "localhost" if DEV else "api.spiraldb.com"
    port: int = 4279 if DEV else 443
    ssl: bool = not DEV
    auth: AuthSettings = Field(default_factory=AuthSettings)
    token: str | None = None

    @property
    def uri(self) -> str:
        return f"{'https' if self.ssl else 'http'}://{self.host}:{self.port}"

    @property
    def uri_scandal(self) -> str:
        # TODO(marko): Scandal will be a different service. For now, gRPC API is hosted on the SpiralDB service.
        return f"{'grpc+tls' if self.ssl else 'grpc'}://{self.host}:{self.port}"

    @property
    def uri_iceberg(self) -> str:
        return self.uri + "/iceberg"

    def device_auth(self) -> DeviceAuth:
        auth_file = (
            APP_DIR / hashlib.md5(f"{self.auth.domain}/{self.auth.client_id}".encode()).hexdigest() / "auth.json"
        )
        return DeviceAuth(auth_file=auth_file, domain=self.auth.domain, client_id=self.auth.client_id)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        toml_file=CONFIG_FILE,
        env_nested_delimiter="__",
        env_prefix="SPIRAL__",
        frozen=True,
    )

    spiraldb: SpiralDBSettings = Field(default_factory=SpiralDBSettings)

    @functools.cached_property
    def api(self) -> "SpiralAPI":
        from spiral.api import SpiralAPI

        return SpiralAPI(self.authn, base_url=self.spiraldb.uri)

    @functools.cached_property
    def authn(self):
        if self.spiraldb.token:
            return TokenAuthn(self.spiraldb.token)

        return FallbackAuthn(
            [
                GitHubActionsProvider(),
                ModalProvider(),
                # TODO(marko): Github and Modal should also be behind token exchanged.
                TokenExchangeProvider(EnvironmentAuthn(), self.spiraldb.uri),
                DeviceAuthProvider(self.spiraldb.device_auth()),
            ]
        )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        init_settings: InitSettingsSource,
        **kwargs,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return env_settings, dotenv_settings, TomlConfigSettingsSource(settings_cls), init_settings


class _LazyDict(Mapping):
    def __init__(self, lazy_values: dict[str, Any | Callable[[], Any]]):
        self._lazy_values = lazy_values

    def _dict(self):
        return {k: v() if callable(v) else v for k, v in self._lazy_values.items()}

    def __getitem__(self, key, /):
        return self._lazy_values[key]()

    def get(self, key, /, default=None):
        return self._lazy_values.get(key, lambda: default)()

    def items(self):
        return self._dict().items()

    def keys(self):
        return self._lazy_values.keys()

    def values(self):
        return self._dict().values()

    def __contains__(self, key, /):
        return key in self._lazy_values

    def __eq__(self, other, /):
        return False

    def __iter__(self):
        return iter(self._dict())

    def __len__(self):
        return len(self._lazy_values)


@functools.cache
def settings() -> Settings:
    return Settings()
