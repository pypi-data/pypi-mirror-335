from datetime import timedelta
from enum import Enum
from typing import Annotated, Literal

from pydantic import AfterValidator, BaseModel, Field

from . import ProjectId, ServiceBase


class BuiltinFileSystem(BaseModel):
    type: Literal["builtin"] = "builtin"
    provider: str


FileSystem = Annotated[BuiltinFileSystem, Field(discriminator="type")]


def _validate_file_path(path: str) -> str:
    if "//" in path:
        raise ValueError("FilePath must not contain multiple slashes")
    if not path.startswith("/"):
        raise ValueError("FilePath must start with /")
    if path.endswith("/"):
        raise ValueError("FilePath must not end with /")
    return path


FilePath = Annotated[
    str,
    AfterValidator(_validate_file_path),
    Field(description="A path to an individual file in the file system. Must not end with a slash."),
]


def _validate_prefix(path: str) -> str:
    if "//" in path:
        raise ValueError("Prefix must not contain multiple slashes")
    if not path.startswith("/"):
        raise ValueError("Prefix must start with /")
    if not path.endswith("/"):
        raise ValueError("Prefix must end with /")
    return path


Prefix = Annotated[
    str,
    AfterValidator(_validate_prefix),
    Field(description="A prefix in a file system. Must end with a slash."),
]


class Mode(Enum):
    READ_ONLY = "ro"
    READ_WRITE = "rw"


class Mount(BaseModel):
    id: str
    project_id: ProjectId
    prefix: Prefix
    mode: Mode
    principal: str


class GetFileSystem:
    class Request(BaseModel):
        project_id: ProjectId

    class Response(BaseModel):
        file_system: FileSystem


class UpdateFileSystem:
    class Request(BaseModel):
        project_id: ProjectId
        file_system: FileSystem

    class Response(BaseModel):
        file_system: FileSystem


class ListProviders:
    class Response(BaseModel):
        providers: list[str]


class CreateMount:
    class Request(BaseModel):
        project_id: ProjectId
        prefix: Prefix
        mode: Mode
        principal: str

    class Response(BaseModel):
        mount: Mount


class CreateMountToken:
    class Request(BaseModel):
        mount_id: str
        mode: Mode
        path: FilePath | Prefix
        ttl: int = Field(default_factory=lambda: int(timedelta(hours=1).total_seconds()))

    class Response(BaseModel):
        token: str


class FileSystemService(ServiceBase):
    def get_file_system(self, request: GetFileSystem.Request) -> GetFileSystem.Response:
        """Get the file system currently configured for a project."""
        return self.client.put("/file-system/get", request, GetFileSystem.Response)

    def update_file_system(self, request: UpdateFileSystem.Request) -> UpdateFileSystem.Response:
        """Update the file system for a project."""
        return self.client.put("/file-system/update", request, UpdateFileSystem.Response)

    def list_providers(self) -> ListProviders.Response:
        return self.client.put("/file-system/list-providers", None, ListProviders.Response)

    def create_mount(self, request: CreateMount.Request) -> CreateMount.Response:
        return self.client.post("/file-system/create-mount", request, CreateMount.Response)

    def create_mount_token(self, request: CreateMountToken.Request) -> CreateMountToken.Response:
        return self.client.post("/file-system/mount-token", request, CreateMountToken.Response)
