from enum import Enum
from typing import Annotated, Literal, Union

from pydantic import BaseModel, Field

from . import OrganizationId, Paged, PagedRequest, PagedResponse, ProjectId, RoleId, ServiceBase
from .organizations import OrganizationRole


class Project(BaseModel):
    id: ProjectId
    organization_id: OrganizationId
    name: str | None = None


class Grant(BaseModel):
    id: str
    project_id: ProjectId
    role_id: RoleId
    principal: str


class CreateProject:
    class Request(BaseModel):
        organization_id: OrganizationId
        id_prefix: str | None = Field(default=None, description="Optional prefix for a random project ID")
        name: str | None = Field(default=None, description="Optional human-readable name for the project")

        id: str | None = Field(
            default=None,
            description="Exact project ID to use. Requires elevated permissions.",
        )

    class Response(BaseModel):
        project: Project


class GetProject:
    class Request(BaseModel):
        id: ProjectId

    class Response(BaseModel):
        project: Project


class ListProjects:
    class Request(PagedRequest): ...

    class Response(PagedResponse[Project]): ...


class ListGrants:
    class Request(PagedRequest):
        project_id: ProjectId

    class Response(PagedResponse[Grant]): ...


class GrantRole:
    class Request(BaseModel):
        project_id: ProjectId
        role_id: RoleId
        principal: Annotated[
            Union[
                "GrantRole.OrgRolePrincipal",
                "GrantRole.OrgUserPrincipal",
                "GrantRole.WorkloadPrincipal",
                "GrantRole.GitHubPrincipal",
                "GrantRole.ModalPrincipal",
            ],
            Field(discriminator="type"),
        ]

    class Response(BaseModel): ...

    class OrgRolePrincipal(BaseModel):
        type: Literal["org"] = "org"

        org_id: OrganizationId
        role: OrganizationRole

    class OrgUserPrincipal(BaseModel):
        type: Literal["org_user"] = "org_user"

        org_id: OrganizationId
        user_id: str

    class WorkloadPrincipal(BaseModel):
        type: Literal["workload"] = "workload"

        workload_id: str

    class GitHubClaim(Enum):
        environment = "environment"
        ref = "ref"
        sha = "sha"
        repository = "repository"
        repository_owner = "repository_owner"
        actor_id = "actor_id"
        repository_visibility = "repository_visibility"
        repository_id = "repository_id"
        repository_owner_id = "repository_owner_id"
        run_id = "run_id"
        run_number = "run_number"
        run_attempt = "run_attempt"
        runner_environment = "runner_environment"
        actor = "actor"
        workflow = "workflow"
        head_ref = "head_ref"
        base_ref = "base_ref"
        event_name = "event_name"
        ref_type = "ref_type"
        job_workflow_ref = "job_workflow_ref"

    class GitHubPrincipal(BaseModel):
        type: Literal["github"] = "github"

        org: str
        repo: str
        conditions: dict["GrantRole.GitHubClaim", str] | None = None

    class ModalClaim(Enum):
        workspace_id = "workspace_id"
        environment_id = "environment_id"
        environment_name = "environment_name"
        app_id = "app_id"
        app_name = "app_name"
        function_id = "function_id"
        function_name = "function_name"
        container_id = "container_id"

    class ModalPrincipal(BaseModel):
        type: Literal["modal"] = "modal"

        workspace_id: str
        # Environments are sub-divisions of workspaces. Name is unique within a workspace.
        # See https://modal.com/docs/guide/environments
        environment_name: str
        # A Modal App is a group of functions and classes that are deployed together.
        # See https://modal.com/docs/guide/apps. Nick and Marko discussed having an app_name
        # here as well and decided to leave it out for now with the assumption that people
        # will want to authorize the whole Modal environment to access Spiral (their data).
        conditions: dict["GrantRole.ModalClaim", str] | None = None


class ProjectService(ServiceBase):
    def get(self, request: GetProject.Request) -> GetProject.Response:
        return self.client.put("/project/get", request, GetProject.Response)

    def create(self, request: CreateProject.Request) -> CreateProject.Response:
        return self.client.post("/project/create", request, CreateProject.Response)

    def list(self) -> Paged[Project]:
        return self.client.paged("/project/list", ListProjects.Request(), ListProjects.Response)

    def list_grants(self, request: ListGrants.Request) -> Paged[Grant]:
        return self.client.paged("/project/list-grants", request, ListGrants.Response)

    def grant_role(self, request: GrantRole.Request) -> GrantRole.Response:
        return self.client.post("/project/grant-role", request, GrantRole.Response)
