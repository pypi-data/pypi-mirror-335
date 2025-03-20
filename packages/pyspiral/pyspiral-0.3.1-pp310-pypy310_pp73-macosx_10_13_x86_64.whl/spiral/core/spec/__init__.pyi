"""Type definitions for the spiral.core.spec module shipped as part of the native library."""

import pyarrow as pa

class ColumnGroup:
    def __init__(self, path: list[str]): ...
    @property
    def table_id(self) -> str: ...
    @property
    def path(self) -> list[str]: ...
    def identifier(self, salt: int) -> str:
        """Return the column group identifier based on the given salt."""

    @staticmethod
    def from_str(path: str) -> ColumnGroup: ...

class ColumnGroupMetadata:
    def __init__(
        self,
        *,
        column_group: ColumnGroup,
        manifest_handle: ManifestHandle | None,
        last_modified_at: int,
        schema_versions: list[VersionedSchema] | None,
        immutable_schema: bool,
        schema_salt: int,
    ): ...

    column_group: ColumnGroup
    manifest_handle: ManifestHandle | None
    last_modified_at: int
    schema_versions: list[VersionedSchema]
    immutable_schema: bool
    schema_salt: int

    def latest_schema(self) -> VersionedSchema:
        """Returns the latest schema of the column group."""
        ...

    def asof(self, asof: int) -> ColumnGroupMetadata:
        """Returns the metadata as of a given timestamp. Currently just filtering versioned schemas."""
        ...

    def apply_wal(self, wal: WriteAheadLog) -> ColumnGroupMetadata:
        """Applies the given WAL to the metadata."""

    def __bytes__(self):
        """Serializes the ColumnGroupMetadata to a protobuf buffer."""

    @staticmethod
    def from_proto(buffer: bytes) -> ColumnGroupMetadata:
        """Deserializes a ColumnGroupMetadata from a protobuf buffer."""
        ...

class LogEntry:
    ts: int
    operation: KeySpaceWriteOp | FragmentSetWriteOp | ConfigurationOp | SchemaEvolutionOp | SchemaBreakOp

    def column_group(self) -> ColumnGroup | None:
        """Returns the column group of the entry if it is associated with one."""

class FileFormat:
    def __init__(self, value: int): ...

    Parquet: FileFormat
    Protobuf: FileFormat
    BinaryArray: FileFormat
    Vortex: FileFormat

    def __int__(self) -> int:
        """Returns the protobuf enum int value."""
        ...

class FragmentLevel:
    L0: FragmentLevel
    L1: FragmentLevel

    def __int__(self) -> int:
        """Returns the protobuf enum int value."""
        ...

class Key:
    def __init__(self, key: bytes): ...

    key: bytes

    def __add__(self, other: Key) -> Key:
        """Concatenates two keys.

        TODO(ngates): remove this function. It should not be necessary to concatenate keys."""

    def __bytes__(self): ...
    def step(self) -> Key:
        """Returns the next key in the key space."""

    @staticmethod
    def min() -> Key: ...
    @staticmethod
    def max() -> Key: ...
    @staticmethod
    def from_array_tuple(array_tuple: tuple[pa.Array]) -> Key: ...

class KeyExtent:
    """An inclusive range of keys."""

    def __init__(self, *, min: Key, max: Key): ...

    min: Key
    max: Key

    def to_range(self) -> KeyRange:
        """Turn this inclusive key extent into an exclusive key range."""

    def union(self, key_extent: KeyExtent) -> KeyExtent: ...
    def __or__(self, other: KeyExtent) -> KeyExtent: ...
    def intersection(self, key_extent: KeyExtent) -> KeyExtent | None: ...
    def __and__(self, other: KeyExtent) -> KeyExtent | None: ...
    def contains(self, item: Key) -> bool: ...
    def __contains__(self, item: Key) -> bool: ...

class KeyRange:
    """A right-exclusive range of keys."""

    def __init__(self, *, begin: Key, end: Key): ...

    begin: Key
    end: Key

    def union(self, other: KeyRange) -> KeyRange: ...
    def __or__(self, other: KeyRange) -> KeyRange: ...
    def intersection(self, key_extent: KeyRange) -> KeyRange | None: ...
    def __and__(self, other: KeyRange) -> KeyRange | None: ...
    def contains(self, item: Key) -> bool: ...
    def __contains__(self, item: Key) -> bool: ...
    def is_disjoint(self, key_range: KeyRange) -> bool:
        return self.end <= key_range.begin or self.begin >= key_range.end

    @staticmethod
    def beginning_with(begin: Key) -> KeyRange: ...
    @staticmethod
    def ending_with(end: Key) -> KeyRange: ...
    @staticmethod
    def full() -> KeyRange: ...

class KeySpan:
    """An exclusive range of keys as indexed by their position in a key space."""

    def __init__(self, *, begin: int, end: int): ...

    begin: int
    end: int

    def __len__(self) -> int: ...
    def shift(self, offset: int) -> KeySpan: ...
    def union(self, other: KeySpan) -> KeySpan: ...
    def __or__(self, other: KeySpan) -> KeySpan: ...

class KeyMap:
    """Displacement map."""

class ManifestHandle:
    def __init__(self, id: str, format: FileFormat, file_size: int, spfs_format_metadata: bytes | None): ...

    id: str
    format: FileFormat
    file_size: int
    spfs_format_metadata: bytes | None

class Schema:
    def to_arrow(self) -> pa.Schema:
        """Returns the Arrow schema."""
        ...
    @staticmethod
    def from_arrow(arrow: pa.Schema) -> Schema:
        """Creates a Schema from an Arrow schema."""
        ...
    def __len__(self):
        """Returns the number of columns in the schema."""
        ...
    @property
    def names(self) -> list[str]:
        """Returns the names of the columns in the schema."""
        ...

class VersionedSchema:
    ts: int
    schema: Schema
    column_ids: list[str]

class KeySpaceWriteOp:
    ks_id: str
    manifest_handle: ManifestHandle

class FragmentSetWriteOp:
    column_group: ColumnGroup
    fs_id: str
    fs_level: FragmentLevel
    manifest_handle: ManifestHandle
    key_span: KeySpan
    key_extent: KeyExtent
    column_ids: list[str]

class ConfigurationOp:
    column_group: ColumnGroup

class SchemaEvolutionOp:
    column_group: ColumnGroup

class SchemaBreakOp:
    column_group: ColumnGroup

class WriteAheadLog:
    def __init__(
        self,
        *,
        entries: list[LogEntry] | None = None,
        truncated_up_to: int = 0,
    ): ...

    entries: list[LogEntry]
    truncated_up_to: int
    ks_manifest_handle: ManifestHandle | None

    @property
    def last_modified_at(self) -> int:
        """Returns the timestamp of the last modification of the log."""

    def filter(
        self, asof: int | None = None, since: int | None = None, column_group: ColumnGroup | None = None
    ) -> WriteAheadLog:
        """Filters the WAL to entries by the given parameters."""

    def __bytes__(self):
        """Serializes the ColumnGroupMetadata to a protobuf buffer."""

    @staticmethod
    def from_proto(buffer: bytes) -> WriteAheadLog:
        """Deserializes a WriteAheadLog from a protobuf buffer."""
        ...
