from typing import Any

import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.dataset as ds

from spiral import Scan, Table


class TableDataset(ds.Dataset):
    def __init__(self, table: Table):
        self._table = table
        # Once table is converted to a dataset, used pinned snapshot.
        self._asof = table.last_modified_at
        self._schema: pa.Schema = table._table.get_schema(asof=self._asof).to_arrow()

        # We don't actually initialize a Dataset, we just implement enough of the API
        # to fool both DuckDB and Polars.
        # super().__init__()
        self._last_scan = None

    @property
    def schema(self) -> pa.Schema:
        return self._schema

    def count_rows(
        self,
        filter: pc.Expression | None = None,
        batch_size: int | None = None,
        batch_readahead: int | None = None,
        fragment_readahead: int | None = None,
        fragment_scan_options: ds.FragmentScanOptions | None = None,
        use_threads: bool = True,
        memory_pool: pa.MemoryPool = None,
    ):
        return self.scanner(
            None,
            filter,
            batch_size,
            batch_readahead,
            fragment_readahead,
            fragment_scan_options,
            use_threads,
            memory_pool,
        ).count_rows()

    def filter(self, expression: pc.Expression) -> "TableDataset":
        raise NotImplementedError("filter not implemented")

    def get_fragments(self, filter: pc.Expression | None = None):
        """TODO(ngates): perhaps we should return ranges as per our split API?"""
        raise NotImplementedError("get_fragments not implemented")

    def head(
        self,
        num_rows: int,
        columns: list[str] | None = None,
        filter: pc.Expression | None = None,
        batch_size: int | None = None,
        batch_readahead: int | None = None,
        fragment_readahead: int | None = None,
        fragment_scan_options: ds.FragmentScanOptions | None = None,
        use_threads: bool = True,
        memory_pool: pa.MemoryPool = None,
    ):
        return self.scanner(
            columns,
            filter,
            batch_size,
            batch_readahead,
            fragment_readahead,
            fragment_scan_options,
            use_threads,
            memory_pool,
        ).head(num_rows)

    def join(
        self,
        right_dataset,
        keys,
        right_keys=None,
        join_type=None,
        left_suffix=None,
        right_suffix=None,
        coalesce_keys=True,
        use_threads=True,
    ):
        raise NotImplementedError("join not implemented")

    def join_asof(self, right_dataset, on, by, tolerance, right_on=None, right_by=None):
        raise NotImplementedError("join_asof not implemented")

    def replace_schema(self, schema: pa.Schema) -> "TableDataset":
        raise NotImplementedError("replace_schema not implemented")

    def scanner(
        self,
        columns: list[str] | None = None,
        filter: pc.Expression | None = None,
        batch_size: int | None = None,
        batch_readahead: int | None = None,
        fragment_readahead: int | None = None,
        fragment_scan_options: ds.FragmentScanOptions | None = None,
        use_threads: bool = True,
        memory_pool: pa.MemoryPool = None,
    ) -> "TableScanner":
        from .substrait_ import SubstraitConverter

        # Extract the substrait expression so we can convert it to a Spiral expression
        if filter is not None:
            filter = SubstraitConverter(self._table, self._schema, self._table.key_schema).convert(
                filter.to_substrait(self._schema, allow_arrow_extensions=True),
            )

        scan = (
            self._table.scan(
                {c: self._table[c] for c in columns},
                where=filter,
                exclude_keys=True,
                asof=self._asof,
            )
            if columns
            else self._table.scan(where=filter, asof=self._asof)
        )
        self._last_scan = scan

        return TableScanner(scan)

    def sort_by(self, sorting, **kwargs):
        raise NotImplementedError("sort_by not implemented")

    def take(
        self,
        indices: pa.Array | Any,
        columns: list[str] | None = None,
        filter: pc.Expression | None = None,
        batch_size: int | None = None,
        batch_readahead: int | None = None,
        fragment_readahead: int | None = None,
        fragment_scan_options: ds.FragmentScanOptions | None = None,
        use_threads: bool = True,
        memory_pool: pa.MemoryPool = None,
    ):
        return self.scanner(
            columns,
            filter,
            batch_size,
            batch_readahead,
            fragment_readahead,
            fragment_scan_options,
            use_threads,
            memory_pool,
        ).take(indices)

    def to_batches(
        self,
        columns: list[str] | None = None,
        filter: pc.Expression | None = None,
        batch_size: int | None = None,
        batch_readahead: int | None = None,
        fragment_readahead: int | None = None,
        fragment_scan_options: ds.FragmentScanOptions | None = None,
        use_threads: bool = True,
        memory_pool: pa.MemoryPool = None,
    ):
        return self.scanner(
            columns,
            filter,
            batch_size,
            batch_readahead,
            fragment_readahead,
            fragment_scan_options,
            use_threads,
            memory_pool,
        ).to_batches()

    def to_table(
        self,
        columns=None,
        filter: pc.Expression | None = None,
        batch_size: int | None = None,
        batch_readahead: int | None = None,
        fragment_readahead: int | None = None,
        fragment_scan_options: ds.FragmentScanOptions | None = None,
        use_threads: bool = True,
        memory_pool: pa.MemoryPool = None,
    ):
        return self.scanner(
            columns,
            filter,
            batch_size,
            batch_readahead,
            fragment_readahead,
            fragment_scan_options,
            use_threads,
            memory_pool,
        ).to_table()


class TableScanner(ds.Scanner):
    """A PyArrow Dataset Scanner that reads from a Spiral Table."""

    def __init__(
        self,
        scan: Scan,
        key_table: pa.Table | pa.RecordBatchReader | None = None,
    ):
        self._scan = scan
        self._schema = scan.schema
        self.key_table = key_table

        # We don't actually initialize a Dataset, we just implement enough of the API
        # to fool both DuckDB and Polars.
        # super().__init__()

    @property
    def schema(self):
        return self._schema

    def count_rows(self):
        # TODO(ngates): is there a faster way to count rows?
        return sum(len(batch) for batch in self.to_reader())

    def head(self, num_rows: int):
        """Return the first `num_rows` rows of the dataset."""
        reader = self.to_reader()
        batches = []
        row_count = 0
        for batch in reader:
            if row_count + len(batch) > num_rows:
                batches.append(batch.slice(0, num_rows - row_count))
                break
            row_count += len(batch)
            batches.append(batch)
        return pa.Table.from_batches(batches, schema=reader.schema)

    def scan_batches(self):
        raise NotImplementedError("scan_batches not implemented")

    def take(self, indices):
        # TODO(ngates): can we defer take until after we've constructed the scan?
        #  Or should this we delay constructing the Spiral Table.scan?
        raise NotImplementedError("take not implemented")

    def to_batches(self):
        return self.to_reader()

    def to_reader(self):
        return self._scan.to_record_batches(key_table=self.key_table)

    def to_table(self):
        return self.to_reader().read_all()


class ScanDataset(ds.Dataset):
    def __init__(
        self,
        scan: Scan,
        key_table: pa.Table | pa.RecordBatchReader | None = None,
    ):
        self._scan = scan
        self._schema: pa.Schema = scan.schema.to_arrow()
        self._key_table = key_table

        # We don't actually initialize a Dataset, we just implement enough of the API
        # to fool both DuckDB and Polars.
        # super().__init__()

    @property
    def schema(self) -> pa.Schema:
        return self._schema

    def count_rows(
        self,
        filter: pc.Expression | None = None,
        batch_size: int | None = None,
        batch_readahead: int | None = None,
        fragment_readahead: int | None = None,
        fragment_scan_options: ds.FragmentScanOptions | None = None,
        use_threads: bool = True,
        memory_pool: pa.MemoryPool = None,
    ):
        return self.scanner(
            None,
            filter,
            batch_size,
            batch_readahead,
            fragment_readahead,
            fragment_scan_options,
            use_threads,
            memory_pool,
        ).count_rows()

    def filter(self, expression: pc.Expression) -> "TableDataset":
        raise NotImplementedError("filter not implemented")

    def get_fragments(self, filter: pc.Expression | None = None):
        """TODO(ngates): perhaps we should return ranges as per our split API?"""
        raise NotImplementedError("get_fragments not implemented")

    def head(
        self,
        num_rows: int,
        columns: list[str] | None = None,
        filter: pc.Expression | None = None,
        batch_size: int | None = None,
        batch_readahead: int | None = None,
        fragment_readahead: int | None = None,
        fragment_scan_options: ds.FragmentScanOptions | None = None,
        use_threads: bool = True,
        memory_pool: pa.MemoryPool = None,
    ):
        return self.scanner(
            columns,
            filter,
            batch_size,
            batch_readahead,
            fragment_readahead,
            fragment_scan_options,
            use_threads,
            memory_pool,
        ).head(num_rows)

    def join(
        self,
        right_dataset,
        keys,
        right_keys=None,
        join_type=None,
        left_suffix=None,
        right_suffix=None,
        coalesce_keys=True,
        use_threads=True,
    ):
        raise NotImplementedError("join not implemented")

    def join_asof(self, right_dataset, on, by, tolerance, right_on=None, right_by=None):
        raise NotImplementedError("join_asof not implemented")

    def replace_schema(self, schema: pa.Schema) -> "TableDataset":
        raise NotImplementedError("replace_schema not implemented")

    def scanner(
        self,
        columns: list[str] | None = None,
        filter: pc.Expression | None = None,
        batch_size: int | None = None,
        batch_readahead: int | None = None,
        fragment_readahead: int | None = None,
        fragment_scan_options: ds.FragmentScanOptions | None = None,
        use_threads: bool = True,
        memory_pool: pa.MemoryPool = None,
    ) -> "TableScanner":
        if columns is not None:
            columns = set(columns)
            names = set(self.schema.names)
            if len(columns - names) != 0 or len(names - columns) != 0:
                raise NotImplementedError("columns", columns, self.schema)
        if filter is not None:
            raise NotImplementedError("filter")
        if batch_size is not None:
            raise NotImplementedError("batch_size")
        if batch_readahead is not None:
            raise NotImplementedError("batch_readahead")
        if fragment_readahead is not None:
            raise NotImplementedError("fragment_readahead")
        if fragment_scan_options is not None:
            raise NotImplementedError("fragment_scan_options")

        return TableScanner(self._scan, key_table=self._key_table)

    def sort_by(self, sorting, **kwargs):
        raise NotImplementedError("sort_by not implemented")

    def take(
        self,
        indices: pa.Array | Any,
        columns: list[str] | None = None,
        filter: pc.Expression | None = None,
        batch_size: int | None = None,
        batch_readahead: int | None = None,
        fragment_readahead: int | None = None,
        fragment_scan_options: ds.FragmentScanOptions | None = None,
        use_threads: bool = True,
        memory_pool: pa.MemoryPool = None,
    ):
        return self.scanner(
            columns,
            filter,
            batch_size,
            batch_readahead,
            fragment_readahead,
            fragment_scan_options,
            use_threads,
            memory_pool,
        ).take(indices)

    def to_batches(
        self,
        columns: list[str] | None = None,
        filter: pc.Expression | None = None,
        batch_size: int | None = None,
        batch_readahead: int | None = None,
        fragment_readahead: int | None = None,
        fragment_scan_options: ds.FragmentScanOptions | None = None,
        use_threads: bool = True,
        memory_pool: pa.MemoryPool = None,
    ):
        return self.scanner(
            columns,
            filter,
            batch_size,
            batch_readahead,
            fragment_readahead,
            fragment_scan_options,
            use_threads,
            memory_pool,
        ).to_batches()

    def to_table(
        self,
        columns=None,
        filter: pc.Expression | None = None,
        batch_size: int | None = None,
        batch_readahead: int | None = None,
        fragment_readahead: int | None = None,
        fragment_scan_options: ds.FragmentScanOptions | None = None,
        use_threads: bool = True,
        memory_pool: pa.MemoryPool = None,
    ):
        return self.scanner(
            columns,
            filter,
            batch_size,
            batch_readahead,
            fragment_readahead,
            fragment_scan_options,
            use_threads,
            memory_pool,
        ).to_table()
