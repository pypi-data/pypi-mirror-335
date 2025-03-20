"""The SpiralDB metastore API."""

from collections.abc import Callable

from spiral.core.spec import ColumnGroup, ColumnGroupMetadata, FileFormat, LogEntry, Schema, WriteAheadLog
from spiral.types_ import Timestamp, Uri
from spiraldb.proto.spiral.table import ManifestHandle

class FileHandle:
    def __init__(self, *, uri: str, format: FileFormat, spfs_token: str | None): ...

    uri: str
    format: FileFormat
    spfs_token: str | None

class FileRef:
    def __init__(self, *, id: str, file_type: FileType, file_format: FileFormat): ...

    id: str
    file_type: FileType
    file_format: FileFormat

    def resolve_uri(self, root_uri: str) -> str:
        """Resolves the file reference URI given the root URI."""

class FileType:
    FragmentFile: FileType
    FragmentManifest: FileType
    ReferenceFile: FileType

    def __int__(self) -> int:
        """Returns the protobuf enum int value."""

class PyMetastore:
    """Rust implementation of the metastore API."""

    @property
    def table_id(self) -> str: ...
    @property
    def root_uri(self) -> Uri: ...
    @property
    def key_schema(self) -> Schema: ...
    def get_wal(self) -> WriteAheadLog:
        """Return the log for the table."""
        ...

    def append_wal(self, prev_last_modified_at: Timestamp, entries: list[LogEntry]) -> WriteAheadLog:
        """Append additional entries into the write-ahead log given the previous write-ahead log timestamp.

        The given entries should have a timestamp of zero and will be assigned an actual timestamp by the server.

        This API is designed to support both a trivial compare-and-swap on the WAL, and also to support more advanced
        conflict resolution within the metastore.
        """
        ...

    def update_wal(
        self,
        prev_ks_manifest_handle_id: str,
        truncate_ts_max: Timestamp | None = None,
        new_ks_manifest_handle: ManifestHandle | None = None,
    ) -> WriteAheadLog:
        """Update the write-ahead log atomically.

        Supports WAL truncation and manifest handle updates necessary for flushing.
        """
        ...

    def get_column_group_metadata(self, column_group: ColumnGroup) -> ColumnGroupMetadata:
        """Return the metadata for column group."""
        ...

    def update_column_group_metadata(
        self, prev_last_modified_at: Timestamp, column_group_metadata: ColumnGroupMetadata
    ) -> ColumnGroupMetadata:
        """Update the column group metadata to the metastore given the previous metadata timestamp."""
        ...

    def list_column_groups(self) -> tuple[list[ColumnGroup], Timestamp]:
        """List all column groups in the table, or None if no index is available."""
        ...

    @staticmethod
    def http(
        table_id: str, root_uri: str, key_schema: Schema, base_url: str, token_provider: Callable[[], str]
    ) -> PyMetastore:
        """Construct a PyMetastore backed by an HTTP metastore service."""

    @staticmethod
    def test(table_id: str, root_uri: str, key_schema: Schema) -> PyMetastore:
        """Construct a PyMetastore backed by an in-memory mock metastore service."""
