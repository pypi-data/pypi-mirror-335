from pydantic import BaseModel, Field

from . import Paged, PagedRequest, PagedResponse, ProjectId, ServiceBase


class Workload(BaseModel):
    id: str
    project_id: ProjectId
    name: str | None = None


class CreateWorkload:
    class Request(BaseModel):
        project_id: str
        name: str | None = Field(default=None, description="Optional human-readable name for the workload")

    class Response(BaseModel):
        workload: Workload


class IssueToken:
    class Request(BaseModel):
        workload_id: str

    class Response(BaseModel):
        token_id: str
        token_secret: str


class ListWorkloads:
    class Request(PagedRequest):
        project_id: str

    class Response(PagedResponse[Workload]): ...


class WorkloadService(ServiceBase):
    def create(self, request: CreateWorkload.Request) -> CreateWorkload.Response:
        return self.client.post("/workload/create", request, CreateWorkload.Response)

    def issue_token(self, request: IssueToken.Request) -> IssueToken.Response:
        return self.client.post("/workload/issue-token", request, IssueToken.Response)

    def list(self, request: ListWorkloads.Request) -> Paged[Workload]:
        return self.client.paged("/workload/list", request, ListWorkloads.Response)
