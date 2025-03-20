import webbrowser
from typing import Annotated

import jwt
import rich
import typer
from rich.table import Table
from typer import Option

from spiral.api.organizations import CreateOrganization, InviteUser, OrganizationRole, PortalLink
from spiral.cli import AsyncTyper, OptionalStr, state
from spiral.cli.types import OrganizationArg

app = AsyncTyper()


@app.command(help="Switch the active organization.")
def switch(org_id: OrganizationArg):
    state.settings.spiraldb.device_auth().authenticate(refresh=True, organization_id=org_id)
    rich.print(f"Switched to organization: {org_id}")


@app.command(help="Create a new organization.")
def create(
    name: Annotated[OptionalStr, Option(help="The human-readable name of the organization.")] = None,
):
    res = state.settings.api.organization.create_organization(CreateOrganization.Request(name=name))

    # Authenticate to the new organization
    state.settings.spiraldb.device_auth().authenticate(refresh=True, organization_id=res.organization.id)

    rich.print(f"{res.organization.name} [dim]{res.organization.id}[/dim]")


@app.command(help="List organizations.")
def ls():
    org_id = current_org_id()

    table = Table("", "id", "name", "role", title="Organizations")
    for m in state.settings.api.organization.list_user_memberships():
        table.add_row("👉" if m.organization.id == org_id else "", m.organization.id, m.organization.name, m.role)

    rich.print(table)


@app.command(help="Invite a user to the organization.")
def invite(email: str, role: OrganizationRole = "member", expires_in_days: int = 7):
    state.settings.api.organization.invite_user(
        InviteUser.Request(email=email, role=role, expires_in_days=expires_in_days)
    )
    rich.print(f"Invited {email} as a {role.value}.")


@app.command(help="Configure single sign-on for your organization.")
def sso():
    _do_action(PortalLink.Intent.SSO)


@app.command(help="Configure directory services for your organization.")
def directory():
    _do_action(PortalLink.Intent.DIRECTORY)


@app.command(help="Configure audit logs for your organization.")
def audit_logs():
    _do_action(PortalLink.Intent.AUDIT_LOGS)


@app.command(help="Configure log streams for your organization.")
def log_streams():
    _do_action(PortalLink.Intent.LOG_STREAMS)


@app.command(help="Configure domains for your organization.")
def domains():
    _do_action(PortalLink.Intent.DOMAIN_VERIFICATION)


def _do_action(intent: PortalLink.Intent):
    res = state.settings.api.organization.portal_link(PortalLink.Request(intent=intent))
    rich.print(f"Opening the configuration portal:\n{res.url}")
    webbrowser.open(res.url)


def current_org_id():
    org_id = jwt.decode(state.settings.authn.token(), options={"verify_signature": False}).get("org_id")
    if not org_id:
        rich.print("[red]You are not logged in to an organization.[/red]")
        raise typer.Exit(1)
    return org_id
