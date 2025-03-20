import os

from spiral.api import Authn


class ModalProvider(Authn):
    def __init__(self):
        self._modal_token = None

    def token(self) -> str | None:
        if self._modal_token is not None:
            return self._modal_token

        if os.environ.get("MODAL_IDENTITY_TOKEN") is not None:
            self._modal_token = os.environ["MODAL_IDENTITY_TOKEN"]

        # For now, we don't exchange the token for a Spiral one.
        return self._modal_token
