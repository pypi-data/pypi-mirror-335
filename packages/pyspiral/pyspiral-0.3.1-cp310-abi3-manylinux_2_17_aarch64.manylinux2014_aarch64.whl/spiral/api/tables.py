from typing import Annotated

from pydantic import AfterValidator, BaseModel, StringConstraints

from . import ArrowSchema, Paged, PagedRequest, PagedResponse, ProjectId, ServiceBase


def _validate_root_uri(uri: str) -> str:
    if uri.endswith("/"):
        raise ValueError("Root URI must not end with a slash.")
    return uri


RootUri = Annotated[str, AfterValidator(_validate_root_uri)]
DatasetName = Annotated[str, StringConstraints(max_length=128, pattern=r"^[a-zA-Z_][a-zA-Z0-9_-]+$")]
TableName = Annotated[str, StringConstraints(max_length=128, pattern=r"^[a-zA-Z_][a-zA-Z0-9_-]+$")]


class TableMetadata(BaseModel):
    root_uri: RootUri
    spfs_mount_id: str | None = None

    key_schema: ArrowSchema

    # TODO(marko): Randomize this on creation of metadata.
    # Column group salt is used to compute column group IDs.
    # It's used to ensure that column group IDs are unique
    # across different tables, even if paths are the same.
    # It's never modified.
    column_group_salt: int = 0


class Table(BaseModel):
    id: str
    project_id: ProjectId
    dataset: DatasetName
    table: TableName
    metadata: TableMetadata


class CreateTable:
    class Request(BaseModel):
        project_id: ProjectId
        dataset: DatasetName
        table: TableName
        key_schema: ArrowSchema
        root_uri: RootUri | None = None
        exist_ok: bool = False

    class Response(BaseModel):
        table: Table


class FindTable:
    class Request(BaseModel):
        project_id: ProjectId
        dataset: DatasetName = None
        table: TableName = None

    class Response(BaseModel):
        table: Table | None


class GetTable:
    class Request(BaseModel):
        id: str

    class Response(BaseModel):
        table: Table


class ListTables:
    class Request(PagedRequest):
        project_id: ProjectId
        dataset: DatasetName | None = None

    class Response(PagedResponse[Table]): ...


class TableService(ServiceBase):
    def create(self, req: CreateTable.Request) -> CreateTable.Response:
        return self.client.post("/table/create", req, CreateTable.Response)

    def find(self, req: FindTable.Request) -> FindTable.Response:
        return self.client.put("/table/find", req, FindTable.Response)

    def get(self, req: GetTable.Request) -> GetTable.Response:
        return self.client.put(f"/table/{req.id}", GetTable.Response)

    def list(self, req: ListTables.Request) -> Paged[Table]:
        return self.client.paged("/table/list", req, ListTables.Response)
