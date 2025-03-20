from rich import print

from spiral.cli import OptionalStr, state


def command(org_id: OptionalStr = None, force: bool = False, refresh: bool = False):
    tokens = state.settings.spiraldb.device_auth().authenticate(force=force, refresh=refresh, organization_id=org_id)
    print(tokens)


def logout():
    state.settings.spiraldb.device_auth().logout()
    print("Logged out.")
