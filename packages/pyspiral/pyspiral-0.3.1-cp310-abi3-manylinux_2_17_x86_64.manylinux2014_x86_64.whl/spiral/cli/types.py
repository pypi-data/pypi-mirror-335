from typing import Annotated

import questionary
import rich
import typer
from questionary import Choice
from typer import Argument

from spiral.api import OrganizationId, ProjectId
from spiral.cli import state


def _project_default():
    projects = list(state.settings.api.project.list())

    if not projects:
        rich.print("[red]No projects found[/red]")
        raise typer.Exit(1)

    return questionary.select(
        "Select a project",
        choices=[
            Choice(title=f"{project.id} - {project.name}" if project.name else project.id, value=project.id)
            for project in projects
        ],
    ).ask()


ProjectArg = Annotated[ProjectId, Argument(help="Project ID", show_default=False, default_factory=_project_default)]


def _org_default():
    memberships = list(state.settings.api.organization.list_user_memberships())

    if not memberships:
        rich.print("[red]No organizations found[/red]")
        raise typer.Exit(1)

    return questionary.select(
        "Select an organization",
        choices=[
            Choice(
                title=f"{m.organization.id} - {m.organization.name}" if m.organization.name else m.organization.id,
                value=m.organization.id,
            )
            for m in memberships
        ],
    ).ask()


OrganizationArg = Annotated[
    OrganizationId, Argument(help="Organization ID", show_default=False, default_factory=_org_default)
]
