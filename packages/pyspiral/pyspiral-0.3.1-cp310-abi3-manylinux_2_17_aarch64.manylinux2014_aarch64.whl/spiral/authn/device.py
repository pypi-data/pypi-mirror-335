import logging
import sys
import textwrap
import time
import webbrowser
from pathlib import Path

import httpx
import jwt
from pydantic import BaseModel

log = logging.getLogger(__name__)


class TokensModel(BaseModel):
    access_token: str
    refresh_token: str

    @property
    def organization_id(self) -> str | None:
        return self.unverified_access_token().get("org_id")

    def unverified_access_token(self):
        return jwt.decode(self.access_token, options={"verify_signature": False})


class AuthModel(BaseModel):
    tokens: TokensModel | None = None


class DeviceAuth:
    def __init__(
        self,
        auth_file: Path,
        domain: str,
        client_id: str,
        http: httpx.Client = None,
    ):
        self._auth_file = auth_file
        self._domain = domain
        self._client_id = client_id
        self._http = http or httpx.Client()

        if self._auth_file.exists():
            with self._auth_file.open("r") as f:
                self._auth = AuthModel.model_validate_json(f.read())
        else:
            self._auth = AuthModel()

        self._default_scope = ["email", "profile"]

    def is_authenticated(self) -> bool:
        """Check if the user is authenticated."""
        tokens = self._auth.tokens
        if tokens is None:
            return False

        # Give ourselves a 30-second buffer before the token expires.
        return tokens.unverified_access_token()["exp"] - 30 > time.time()

    def authenticate(self, force: bool = False, refresh: bool = False, organization_id: str = None) -> TokensModel:
        """Blocking call to authenticate the user.

        Triggers a device code flow and polls for the user to login.
        """
        if force:
            return self._device_code(organization_id)

        if refresh:
            if self._auth.tokens is None:
                raise ValueError("No tokens to refresh.")
            tokens = self._refresh(self._auth.tokens, organization_id)
            if not tokens:
                raise ValueError("Failed to refresh token.")
            return tokens

        # Check for mis-matched organization.
        if organization_id is not None:
            tokens = self._auth.tokens
            if tokens is not None and tokens.unverified_access_token().get("org_id") != organization_id:
                tokens = self._refresh(self._auth.tokens, organization_id)
                if tokens is None:
                    return self._device_code(organization_id)

        if self.is_authenticated():
            return self._auth.tokens

        # Try to refresh.
        tokens = self._auth.tokens
        if tokens is not None:
            tokens = self._refresh(tokens)
            if tokens is not None:
                return tokens

        # Otherwise, we kick off the device code flow.
        return self._device_code(organization_id)

    def logout(self):
        self._remove_tokens()

    def _device_code(self, organization_id: str | None):
        scope = " ".join(self._default_scope)
        res = self._http.post(
            f"{self._domain}/auth/device/code",
            data={
                "client_id": self._client_id,
                "scope": scope,
                "organization_id": organization_id,
            },
        )
        res = res.raise_for_status().json()
        device_code = res["device_code"]
        user_code = res["user_code"]
        expires_at = res["expires_in"] + time.time()
        interval = res["interval"]
        verification_uri_complete = res["verification_uri_complete"]

        # We need to detect if the user is running in a terminal, in Jupyter, etc.
        # For now, we'll try to open the browser.
        sys.stderr.write(
            textwrap.dedent(
                f"""
                Please login here: {verification_uri_complete}
                Your code is {user_code}.
            """
            )
        )

        # Try to open the browser (this also works if the Jupiter notebook is running on the user's machine).
        opened = webbrowser.open(verification_uri_complete)

        # If we have a server-side Jupyter notebook, we can try to open with client-side JavaScript.
        if not opened and _in_notebook():
            from IPython.display import Javascript, display

            display(Javascript(f'window.open("{verification_uri_complete}");'))

        # In the meantime, we need to poll for the user to login.
        while True:
            if time.time() > expires_at:
                raise TimeoutError("Login timed out.")
            time.sleep(interval)
            res = self._http.post(
                f"{self._domain}/auth/token",
                data={
                    "client_id": self._client_id,
                    "device_code": device_code,
                    "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
                },
            )
            if not res.is_success:
                continue

            tokens = TokensModel(
                access_token=res.json()["access_token"],
                refresh_token=res.json()["refresh_token"],
            )
            self._save_tokens(tokens)
            return self._auth.tokens

    def _refresh(self, tokens: TokensModel, organization_id: str = None) -> TokensModel | None:
        """Attempt to use the refresh token."""
        log.debug("Refreshing token %s", self._client_id)

        res = self._http.post(
            f"{self._domain}/auth/refresh",
            data={
                "client_id": self._client_id,
                "grant_type": "refresh_token",
                "refresh_token": tokens.refresh_token,
                "organization_id": organization_id,
            },
        )
        if not res.is_success:
            print("Failed to refresh token", res.status_code, res.text)
            return None

        tokens = TokensModel(
            access_token=res.json()["access_token"],
            refresh_token=res.json()["refresh_token"],
        )
        self._save_tokens(tokens)
        return tokens

    def _save_tokens(self, tokens: TokensModel):
        self._auth = self._auth.model_copy(update={"tokens": tokens})
        self._auth_file.parent.mkdir(parents=True, exist_ok=True)
        with self._auth_file.open("w") as f:
            f.write(self._auth.model_dump_json(exclude_defaults=True))

    def _remove_tokens(self):
        self._auth_file.unlink(missing_ok=True)
        self._auth = self._auth.model_copy(update={"tokens": None})


def _in_notebook():
    try:
        from IPython import get_ipython

        if "IPKernelApp" not in get_ipython().config:  # pragma: no cover
            return False
    except ImportError:
        return False
    except AttributeError:
        return False
    return True
