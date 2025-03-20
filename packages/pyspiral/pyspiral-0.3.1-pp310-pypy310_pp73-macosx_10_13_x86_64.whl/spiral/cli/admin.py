from rich import print

from spiral.api.admin import SyncMemberships, SyncOrgs
from spiral.cli import AsyncTyper, state

app = AsyncTyper()


@app.command()
def sync(orgs: bool = False, memberships: bool = False):
    run_all = True
    if any([orgs, memberships]):
        run_all = False

    if run_all or orgs:
        for org_id in state.settings.api._admin.sync_orgs(SyncOrgs.Request()):
            print(org_id)

    if run_all or memberships:
        for membership in state.settings.api._admin.sync_memberships(SyncMemberships.Request()):
            print(membership)
