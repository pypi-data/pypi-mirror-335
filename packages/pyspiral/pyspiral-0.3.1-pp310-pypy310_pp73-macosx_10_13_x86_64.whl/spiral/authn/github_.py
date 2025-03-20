import os

import httpx

from spiral.api import Authn


class GitHubActionsProvider(Authn):
    AUDIENCE = "https://iss.spiraldb.com"

    def __init__(self):
        self._gh_token = None

    def token(self) -> str | None:
        if self._gh_token is not None:
            return self._gh_token

        if os.environ.get("GITHUB_ACTIONS") == "true":
            # Next, we check to see if we're running in GitHub actions and if so, grab an ID token.
            if "ACTIONS_ID_TOKEN_REQUEST_TOKEN" in os.environ and "ACTIONS_ID_TOKEN_REQUEST_URL" in os.environ:
                if not hasattr(self, "__gh_token"):
                    resp = httpx.get(
                        f"{os.environ['ACTIONS_ID_TOKEN_REQUEST_URL']}&audience={self.AUDIENCE}",
                        headers={"Authorization": f'Bearer {os.environ["ACTIONS_ID_TOKEN_REQUEST_TOKEN"]}'},
                    )
                    if not resp.is_success:
                        raise ValueError(f"Failed to get GitHub Actions ID token: {resp.text}", resp)
                    self._gh_token = resp.json()["value"]
            else:
                raise ValueError("Please set 'id-token: write' permission for this GitHub Actions workflow.")

        # For now, we don't exchange the token for a Spiral one.
        return self._gh_token
