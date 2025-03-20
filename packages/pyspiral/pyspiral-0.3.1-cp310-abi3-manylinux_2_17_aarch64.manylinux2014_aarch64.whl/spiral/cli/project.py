from typing import Annotated

import rich
import typer
from typer import Option

from spiral.api.organizations import OrganizationRole
from spiral.api.projects import CreateProject, Grant, GrantRole, ListGrants, Project
from spiral.cli import AsyncTyper, OptionalStr, printer, state
from spiral.cli.org import current_org_id
from spiral.cli.types import ProjectArg

app = AsyncTyper()


@app.command(help="List projects.")
def ls():
    projects = list(state.settings.api.project.list())
    rich.print(printer.table_of_models(Project, projects))


@app.command(help="Create a new project.")
def create(
    id_prefix: Annotated[
        OptionalStr, Option(help="An optional ID prefix to which a random number will be appended.")
    ] = None,
    org_id: Annotated[OptionalStr, Option(help="Organization ID in which to create the project.")] = None,
    name: Annotated[OptionalStr, Option(help="Friendly name for the project.")] = None,
):
    res = state.settings.api.project.create(
        CreateProject.Request(organization_id=org_id or current_org_id(), id_prefix=id_prefix, name=name)
    )
    rich.print(f"Created project {res.project.id}")


@app.command(help="Grant a role on a project.")
def grant(
    project: ProjectArg,
    role: Annotated[str, Option(help="Role to grant.")],
    org_id: Annotated[
        OptionalStr, Option(help="Pass an organization ID to grant a role to an organization user(s).")
    ] = None,
    user_id: Annotated[
        OptionalStr, Option(help="Pass a user ID when using --org-id to grant a role to grant a role to a user.")
    ] = None,
    org_role: Annotated[
        OptionalStr,
        Option(help="Pass an organization role when using --org-id to grant a role to all users with that role."),
    ] = None,
    workload_id: Annotated[OptionalStr, Option(help="Pass a workload ID to grant a role to a workload.")] = None,
    github: Annotated[
        OptionalStr, Option(help="Pass an `<org>/<repo>` string to grant a role to a job running in GitHub Actions.")
    ] = None,
    modal: Annotated[
        OptionalStr,
        Option(help="Pass a `<workspace_id>/<env_name>` string to grant a role to a job running in Modal environment."),
    ] = None,
    conditions: list[str] | None = Option(
        default=None,
        help="`<key>=<value>` token conditions to apply to the grant when using --github or --modal.",
    ),
):
    conditions = conditions or []

    # Check mutual exclusion
    if sum(int(bool(opt)) for opt in {org_id, workload_id, github, modal}) != 1:
        raise typer.BadParameter("Only one of --org-id, --github or --modal may be specified.")

    if github:
        org, repo = github.split("/", 1)
        conditions = {GrantRole.GitHubClaim(k): v for k, v in dict(c.split("=", 1) for c in conditions).items()}
        principal = GrantRole.GitHubPrincipal(org=org, repo=repo, conditions=conditions)
    elif modal:
        workspace_id, environment_name = modal.split("/", 1)
        conditions = {GrantRole.ModalClaim(k): v for k, v in dict(c.split("=", 1) for c in conditions).items()}
        principal = GrantRole.ModalPrincipal(
            workspace_id=workspace_id, environment_name=environment_name, conditions=conditions
        )
    elif org_id:
        # Check mutual exclusion
        if sum(int(bool(opt)) for opt in {user_id, org_role}) != 1:
            raise typer.BadParameter("Only one of --user-id or --org-role may be specified.")

        if user_id is not None:
            principal = GrantRole.OrgUserPrincipal(org_id=org_id, user_id=user_id)
        elif org_role is not None:
            principal = GrantRole.OrgRolePrincipal(org_id=org_id, role=OrganizationRole(org_role))
        else:
            raise NotImplementedError("Only user or role principal is supported at this time.")
    elif workload_id:
        principal = GrantRole.WorkloadPrincipal(workload_id=workload_id)
    else:
        raise NotImplementedError("Only organization, GitHub or Modal principal is supported at this time.")

    state.settings.api.project.grant_role(
        GrantRole.Request(
            project_id=project,
            role_id=role,
            principal=principal,
        )
    )

    rich.print(f"Granted role {role} on project {project}")


@app.command(help="List project grants.")
def grants(project: ProjectArg):
    project_grants = list(state.settings.api.project.list_grants(ListGrants.Request(project_id=project)))
    rich.print(printer.table_of_models(Grant, project_grants, title="Project Grants"))
