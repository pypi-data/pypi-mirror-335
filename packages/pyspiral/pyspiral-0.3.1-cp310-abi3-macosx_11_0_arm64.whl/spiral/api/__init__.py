import abc
import base64
import logging
import os
import re
import socket
import time
from collections.abc import Iterable, Iterator
from typing import TYPE_CHECKING, Annotated, Generic, TypeVar

import betterproto
import httpx
import pyarrow as pa
from httpx import HTTPStatusError
from pydantic import (
    BaseModel,
    BeforeValidator,
    Field,
    GetPydanticSchema,
    PlainSerializer,
    StringConstraints,
    TypeAdapter,
)

if TYPE_CHECKING:
    from .admin import AdminService
    from .filesystems import FileSystemService
    from .organizations import OrganizationService
    from .projects import ProjectService
    from .tables import TableService
    from .tokens import TokenService
    from .workloads import WorkloadService

log = logging.getLogger(__name__)

RE_ID = re.compile("[a-zA-Z0-9-]+")

OrganizationId = Annotated[str, StringConstraints(min_length=1, max_length=64)]  # , pattern=RE_ID)]
ProjectId = Annotated[str, StringConstraints(min_length=1, max_length=64)]  # , pattern=RE_ID)]
RoleId = str

#: Annotations to implement pa.Schema serde with byte arrays
ArrowSchema = Annotated[
    pa.Schema,
    GetPydanticSchema(lambda tp, handler: handler(object)),
    BeforeValidator(
        lambda v: v
        if isinstance(v, pa.Schema)
        else pa.ipc.read_schema(pa.ipc.read_message(base64.urlsafe_b64decode(v)))
    ),
    PlainSerializer(lambda schema: base64.urlsafe_b64encode(schema.serialize().to_pybytes())),
]

E = TypeVar("E")


class PagedRequest(BaseModel):
    page_token: str | None = None
    page_size: int = 50


class PagedResponse(BaseModel, Generic[E]):
    items: list[E] = Field(default_factory=list)
    next_page_token: str | None = None


PagedReqT = TypeVar("PagedReqT", bound=PagedRequest)


class Paged(Iterable[E], Generic[E]):
    def __init__(
        self,
        client: "_Client",
        path: str,
        request: PagedRequest,
        response_cls: type[PagedResponse[E]],
    ):
        self._client = client
        self._path = path
        self._request: PagedRequest = request
        self._response_cls = response_cls

        self._response: PagedResponse[E] = client.put(path, request, response_cls)

    @property
    def page(self) -> PagedResponse[E]:
        return self._response

    def __iter__(self) -> Iterator[E]:
        while True:
            yield from self._response.items

            if self._response.next_page_token is None:
                break

            self._request = self._request.model_copy(update=dict(page_token=self._response.next_page_token))
            self._response = self._client.put(self._path, self._request, self._response_cls)


class ServiceBase:
    def __init__(self, client: "_Client"):
        self.client = client


class Authn:
    """An abstract class for credential providers."""

    @abc.abstractmethod
    def token(self) -> str | None:
        """Return a token, if available."""


class _Client:
    RequestT = TypeVar("RequestT")
    ResponseT = TypeVar("ResponseT")

    def __init__(self, http: httpx.Client, authn: Authn):
        self.http = http
        self.authn = authn

    def get(self, path: str, response_cls: type[ResponseT]) -> ResponseT:
        return self.request("GET", path, None, response_cls)

    def post(self, path: str, req: RequestT, response_cls: type[ResponseT]) -> ResponseT:
        return self.request("POST", path, req, response_cls)

    def put(self, path: str, req: RequestT, response_cls: type[ResponseT]) -> ResponseT:
        return self.request("PUT", path, req, response_cls)

    def request(self, method: str, path: str, req: RequestT | None, response_cls: type[ResponseT]) -> ResponseT:
        if isinstance(req, betterproto.Message):
            try:
                req = dict(content=bytes(req))
            except:
                raise
        elif req is not None:
            req = dict(json=TypeAdapter(req.__class__).dump_python(req, mode="json") if req is not None else None)
        else:
            req = dict()

        token = self.authn.token()
        resp = self.http.request(method, path, headers={"authorization": f"Bearer {token}" if token else None}, **req)

        try:
            resp.raise_for_status()
        except HTTPStatusError as e:
            # Enrich the exception with the response body
            raise HTTPStatusError(f"{str(e)}: {resp.text}", request=e.request, response=e.response)

        if issubclass(response_cls, betterproto.Message):
            return response_cls().parse(resp.content)
        else:
            return TypeAdapter(response_cls).validate_python(resp.json())

    def paged(self, path: str, req: PagedRequest, response_cls: type[PagedResponse[E]]) -> Paged[E]:
        return Paged(self, path, req, response_cls)


class SpiralAPI:
    def __init__(self, authn: Authn, base_url: str | None = None):
        self.base_url = base_url or os.environ.get("SPIRAL_URL", "https://api.spiraldb.com")
        self.client = _Client(
            httpx.Client(
                base_url=self.base_url,
                timeout=None if ("PYTEST_VERSION" in os.environ or bool(os.environ.get("SPIRAL_DEV", None))) else 60,
            ),
            authn,
        )

    @property
    def _admin(self) -> "AdminService":
        from .admin import AdminService

        return AdminService(self.client)

    @property
    def file_system(self) -> "FileSystemService":
        from .filesystems import FileSystemService

        return FileSystemService(self.client)

    @property
    def organization(self) -> "OrganizationService":
        from .organizations import OrganizationService

        return OrganizationService(self.client)

    @property
    def token(self) -> "TokenService":
        from .tokens import TokenService

        return TokenService(self.client)

    @property
    def project(self) -> "ProjectService":
        from .projects import ProjectService

        return ProjectService(self.client)

    @property
    def table(self) -> "TableService":
        from .tables import TableService

        return TableService(self.client)

    @property
    def workload(self) -> "WorkloadService":
        from .workloads import WorkloadService

        return WorkloadService(self.client)


def wait_for_port(port: int, host: str = "localhost", timeout: float = 5.0):
    """Wait until a port starts accepting TCP connections."""
    start_time = time.time()
    while True:
        try:
            with socket.create_connection((host, port), timeout=timeout):
                break
        except OSError as ex:
            time.sleep(0.01)
            if time.time() - start_time >= timeout:
                raise TimeoutError(
                    f"Waited too long for the port {port} on host {host} to start accepting " "connections."
                ) from ex
