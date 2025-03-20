import base64
import logging
import os

from spiral.api import Authn, SpiralAPI

ENV_TOKEN_ID = "SPIRAL_TOKEN_ID"
ENV_TOKEN_SECRET = "SPIRAL_TOKEN_SECRET"

log = logging.getLogger(__name__)


class FallbackAuthn(Authn):
    """Credential provider that tries multiple providers in order."""

    def __init__(self, providers: list[Authn]):
        self._providers = providers

    def token(self) -> str | None:
        for provider in self._providers:
            token = provider.token()
            if token is not None:
                return token
        return None


class TokenAuthn(Authn):
    """Credential provider that returns a fixed token."""

    def __init__(self, token: str):
        self._token = token

    def token(self) -> str:
        return self._token


class EnvironmentAuthn(Authn):
    """Credential provider that returns a basic token from the environment.

    NOTE: Returns basic token. Must be exchanged.
    """

    def token(self) -> str | None:
        if ENV_TOKEN_ID not in os.environ:
            return None
        if ENV_TOKEN_SECRET not in os.environ:
            raise ValueError(f"{ENV_TOKEN_SECRET} is missing.")

        token_id = os.environ[ENV_TOKEN_ID]
        token_secret = os.environ[ENV_TOKEN_SECRET]
        basic_token = base64.b64encode(f"{token_id}:{token_secret}".encode()).decode("utf-8")

        return basic_token


class DeviceAuthProvider(Authn):
    """Auth provider that uses the device flow to authenticate a Spiral user."""

    def __init__(self, device_auth):
        # NOTE(ngates): device_auth: spiral.auth.device_code.DeviceAuth
        #  We don't type it to satisfy our import linter
        self._device_auth = device_auth

    def token(self) -> str | None:
        # TODO(ngates): only run this if we're in a notebook, CLI, or otherwise on the user's machine.
        return self._device_auth.authenticate().access_token


class TokenExchangeProvider(Authn):
    """Auth provider that exchanges a basic token for a Spiral token."""

    def __init__(self, authn: Authn, base_url: str):
        self._authn = authn
        self._token_service = SpiralAPI(authn, base_url).token

        self._sp_token = None

    def token(self) -> str | None:
        if self._sp_token is not None:
            return self._sp_token

        # Don't try to exchange if token is not discovered.
        if self._authn.token() is None:
            return None

        log.debug("Exchanging token")
        self._sp_token = self._token_service.exchange().token

        return self._sp_token
