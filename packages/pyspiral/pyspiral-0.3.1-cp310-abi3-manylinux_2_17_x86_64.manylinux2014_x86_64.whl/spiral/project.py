from typing import TYPE_CHECKING, Any

import pyarrow as pa

from spiral import Table
from spiral.api.tables import CreateTable, FindTable
from spiral.core.core import Table as CoreTable
from spiral.core.metastore import PyMetastore
from spiral.core.spec import Schema
from spiral.types_ import Uri

if TYPE_CHECKING:
    from spiral.catalog import Spiral


class Project:
    def __init__(self, spiral_db: "Spiral", id: str, name: str | None = None):
        self._spiral_db = spiral_db
        self._id = id
        self._name = name

        self._api = self._spiral_db.config.api

    def __str__(self):
        return self._id

    def __repr__(self):
        return f"Project(id={self._id}{', name=' + self._name if self._name else ''})"

    @property
    def id(self) -> str:
        return self._id

    @property
    def name(self) -> str:
        return self._name or self._id

    def list_table_names(self) -> list[(str, str)]:
        """List tuples of (dataset, table) names in the project."""
        return [(t.dataset, t.table) for t in self._api.table.list(FindTable.Request(project_id=self.id))]

    def list_tables(self) -> list[Table]:
        """List tables in the project."""
        return [
            Table(
                CoreTable(
                    PyMetastore.http(
                        table_id=t.id,
                        root_uri=t.metadata.root_uri,
                        key_schema=Schema.from_arrow(t.metadata.key_schema),
                        base_url=self._api.base_url + "/metastore/",
                        token_provider=self._spiral_db.config.authn.token,
                    ),
                ),
                name=f"{self.id}.{t.dataset}.{t.table}",
            )
            for t in self._api.table.list(FindTable.Request(project_id=self.id))
        ]

    def create_table(
        self,
        identifier: str,
        *,
        key_schema: pa.Schema | Any,
        uri: Uri | None = None,
        exist_ok: bool = False,
    ) -> Table:
        """Create a new table in the project."""
        dataset, table = self._parse_identifier(identifier)

        if not isinstance(key_schema, pa.Schema):
            key_schema = pa.schema(key_schema)

        res = self._api.table.create(
            CreateTable.Request(
                project_id=self.id,
                dataset=dataset,
                table=table,
                key_schema=key_schema,
                root_uri=uri,
                exist_ok=exist_ok,
            )
        )

        # Must have the same schema as provided, even if the table already exists.
        expected_key_schema = res.table.metadata.key_schema
        if key_schema != expected_key_schema:
            raise ValueError(f"Table already exists with different key schema: {expected_key_schema} != {key_schema}")
        if uri and res.table.metadata.root_uri != uri:
            raise ValueError(f"Table already exists with different root URI: {res.table.metadata.root_uri} != {uri}")

        # Set up a metastore backed by SpiralDB
        metastore = PyMetastore.http(
            table_id=res.table.id,
            root_uri=res.table.metadata.root_uri,
            key_schema=Schema.from_arrow(res.table.metadata.key_schema),
            base_url=self._api.base_url + "/metastore/",
            token_provider=self._spiral_db.config.authn.token,
        )

        return Table(CoreTable(metastore), name=f"{self.id}.{res.table.dataset}.{res.table.table}")

    def table(self, identifier: str) -> Table:
        """Open a table with a `dataset.table` identifier, or `table` name using the `default` dataset."""
        dataset, table = self._parse_identifier(identifier)

        # TODO(ngates): why does the client _need_ this information? Can we defer it?
        res = self._api.table.find(
            FindTable.Request(
                project_id=self.id,
                dataset=dataset,
                table=table,
            )
        )
        if res.table is None:
            raise ValueError(f"Table not found: {self.id}.{dataset}.{table}")

        # Set up a metastore backed by SpiralDB
        metastore = PyMetastore.http(
            table_id=res.table.id,
            root_uri=res.table.metadata.root_uri,
            key_schema=Schema.from_arrow(res.table.metadata.key_schema),
            base_url=self._api.base_url + "/metastore/",
            token_provider=self._spiral_db.config.authn.token,
        )

        return Table(CoreTable(metastore), name=f"{self.id}.{res.table.dataset}.{res.table.table}")

    @staticmethod
    def _parse_identifier(identifier: str) -> tuple[str, str]:
        parts = identifier.split(".")
        if len(parts) == 1:
            return "default", parts[0]
        elif len(parts) == 2:
            return parts[0], parts[1]
        else:
            raise ValueError(f"Invalid table identifier: {identifier}")
