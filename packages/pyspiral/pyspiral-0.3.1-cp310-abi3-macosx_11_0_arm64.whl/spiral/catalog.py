from typing import TYPE_CHECKING

import jwt

from spiral.api import SpiralAPI
from spiral.api.projects import CreateProject
from spiral.settings import Settings, settings

if TYPE_CHECKING:
    from pyiceberg import catalog

    from spiral.project import Project
    from spiral.table import Table

_default = object()


class Spiral:
    def __init__(self, config: Settings | None = None):
        self._config = config or settings()
        self._api = self._config.api

        self._org = None

    @property
    def config(self) -> Settings:
        return self._config

    @property
    def api(self) -> SpiralAPI:
        return self._api

    @property
    def organization(self) -> str:
        if self._org is None:
            token_payload = jwt.decode(self._config.authn.token(), options={"verify_signature": False})
            if "org_id" not in token_payload:
                raise ValueError("Please create an organization.")
            self._org = token_payload["org_id"]
        return self._org

    def list_projects(self) -> list["Project"]:
        """List project IDs."""
        from .project import Project

        return [Project(self, id=p.id, name=p.name) for p in self.api.project.list()]

    def list_project_ids(self) -> list[str]:
        """List project IDs."""
        return [p.id for p in self.list_projects()]

    def create_project(
        self,
        id_prefix: str | None = None,
        *,
        org: str | None = None,
        name: str | None = None,
    ) -> "Project":
        """Create a project in the current, or given, organization."""
        from .project import Project

        org = org or self.organization
        res = self.api.project.create(CreateProject.Request(organization_id=org, id_prefix=id_prefix, name=name))
        return Project(self, res.project.id, name=res.project.name)

    def project(self, project_id: str) -> "Project":
        """Open an existing project."""
        from .project import Project

        # We avoid an API call since we'd just be fetching a human-readable name. Seems a waste in most cases.
        return Project(self, id=project_id, name=project_id)

    def table(self, identifier: str) -> "Table":
        """Open a table with a "project.dataset.table" identifier."""
        parts = identifier.split(".")
        if len(parts) != 3:
            raise ValueError(f"Invalid table identifier: {identifier}")
        project_id, dataset, table = parts

        return self.project(project_id).table(f"{dataset}.{table}")

    def iceberg_catalog(self) -> "catalog.Catalog":
        """Open the Iceberg catalog."""
        from pyiceberg.catalog import load_catalog

        return load_catalog(
            "default",
            **{
                "type": "rest",
                "uri": self._config.spiraldb.uri_iceberg,
                "token": self._config.authn.token(),
            },
        )
