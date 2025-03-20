import betterproto
import pyarrow as pa

from spiral.proto._.spiral import table as table_
from spiral.proto._.spiral.table import (
    ColumnGroup,
    ConfigurationOp,
    FileFormat,
    KeyExtent,
    KeySpan,
    Level,
    ManifestHandle,
    Schema,
    SchemaBreakOp,
    SchemaEvolutionOp,
    VersionedSchema,
    WriteOp,
)
from spiral.proto._.spiral.table import (
    ColumnGroupMetadata as ColumnGroupMetadata_,
)
from spiral.proto._.spiral.table import (
    Entry as Entry_,
)
from spiral.proto._.spiral.table import (
    WriteAheadLog as WriteAheadLog_,
)

__all__ = [
    "ColumnGroup",
    "ColumnGroupMetadata",
    "ConfigurationOp",
    "Entry",
    "FileFormat",
    "KeyExtent",
    "KeySpan",
    "Level",
    "ManifestHandle",
    "Schema",
    "SchemaBreakOp",
    "SchemaEvolutionOp",
    "VersionedSchema",
    "WriteAheadLog",
    "WriteOp",
]


class ColumnGroupMetadata(ColumnGroupMetadata_):
    @property
    def latest_schema(self) -> pa.Schema:
        if self.schema_versions:
            return pa.ipc.read_schema(pa.py_buffer(self.schema_versions[-1].schema.arrow))
        return pa.schema([])

    def asof(self, asof: int | None) -> "ColumnGroupMetadata":
        """Return the metadata as of the given timestamp."""
        if asof is None:
            return self.model_copy()

        versions = [v for v in self.schema_versions if v.ts <= asof]
        return self.model_copy(update=dict(schema_versions=versions))


class Entry(Entry_):
    @property
    def column_group(self) -> tuple[str, ...] | None:
        match betterproto.which_one_of(self, "operation"):
            case _, op:
                return tuple(op.column_group.parts)


class WriteAheadLog(WriteAheadLog_):
    # TODO(ngates): add a single `filter` function that takes these as kwargs

    def asof(self, asof: int | None) -> "WriteAheadLog":
        """Return the WAL with all entries after the given timestamp removed."""
        if asof is None:
            return self.model_copy()
        return self.model_copy(update=dict(logs=[entry for entry in self.logs if entry.ts <= asof]))

    def since(self, since: int | None) -> "WriteAheadLog":
        """Return the WAL with all entries before the given timestamp removed."""
        if since is None:
            return self.model_copy()
        return self.model_copy(update=dict(logs=[entry for entry in self.logs if entry.ts > since]))

    def for_column_group(self, column_group_path: tuple[str, ...]) -> "WriteAheadLog":
        """Return the WAL with all entries for the given column group."""
        return self.model_copy(
            update=dict(logs=[entry for entry in self.logs if tuple(entry.op.column_group.parts) == column_group_path])
        )


from spiral.proto.util import patch_protos

patch_protos(table_, globals())
