import pyarrow as pa
from spiral.core.spec import FileFormat, FragmentLevel, KeyExtent, KeyMap, KeyRange, KeySpan
from spiral.types_ import Timestamp

class FragmentManifest:
    def __len__(self): ...
    def __getitem__(self, idx: int): ...
    def to_arrow(self) -> pa.RecordBatchReader: ...
    @staticmethod
    def compute_schema(data_schema: pa.Schema) -> pa.Schema: ...
    @staticmethod
    def from_fragment(fragment_file: FragmentFile) -> FragmentManifest: ...
    @staticmethod
    def from_arrow(reader: pa.RecordBatchReader) -> FragmentManifest: ...
    @staticmethod
    def empty() -> FragmentManifest: ...

class FragmentFile:
    id: str
    committed_at: Timestamp | None
    compacted_at: Timestamp | None
    format: FileFormat
    format_metadata: bytes | None
    size_bytes: int
    # NOTE: Empty for keyspace file.
    column_ids: list[str]
    fs_id: str
    fs_level: FragmentLevel
    ks_id: str
    key_span: KeySpan
    key_extent: KeyExtent
    key_map: KeyMap | None

    def __init__(
        self,
        *,
        id: str,
        committed_at: Timestamp | None,
        compacted_at: Timestamp | None,
        format: FileFormat,
        format_metadata: bytes,
        size_bytes: int,
        column_ids: list[str],
        fs_id: str,
        fs_level: FragmentLevel,
        ks_id: str,
        key_span: KeySpan,
        key_extent: KeyExtent,
        key_map: KeyMap | None,
        stats: pa.StructArray,
    ): ...
    @property
    def key_range(self) -> KeyRange: ...
