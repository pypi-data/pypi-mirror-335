from collections.abc import Iterator
from datetime import datetime
from typing import TYPE_CHECKING, Any

import pyarrow as pa
from opentelemetry import trace

from spiral.core.core import TableScan
from spiral.core.spec import KeyRange, Schema
from spiral.expressions.base import ExprLike

if TYPE_CHECKING:
    import dask.dataframe as dd
    import pandas as pd
    import polars as pl
    import pyarrow
    import pyarrow.dataset
    from datasets import iterable_dataset

tracer = trace.get_tracer("pyspiral.client.scan")


def scan(
    *projections: ExprLike,
    where: ExprLike | None = None,
    asof: datetime | int | str = None,
    exclude_keys: bool = False,
) -> "Scan":
    """Starts a read transaction on the spiral.

    Args:
        projections: a set of expressions that return struct arrays.
        where: a query expression to apply to the data.
        asof: only data written before the given timestamp will be returned, caveats around compaction.
        exclude_keys: whether to exclude the key columns in the scan result, defaults to False.
            Note that if a projection includes a key column, it will be included in the result.
    """
    from spiral import expressions as se

    # Combine all projections into a single struct.
    projection = se.merge(*projections)
    if where is not None:
        where = se.lift(where)

    return Scan(
        TableScan(
            projection.__expr__,
            filter=where.__expr__ if where else None,
            asof=asof,
            exclude_keys=exclude_keys,
        ),
        # config=config,
    )


class Scan:
    """Scan object."""

    def __init__(
        self,
        scan: TableScan,
    ):
        # NOTE(ngates): this API is a little weird. e.g. if the query doesn't define an asof, it is resolved
        #  when we wrap it into a core.Scan. Should we expose a Query object in the Python API that's reusable
        #  and will re-resolve the asof? Or should we just expose a scan that fixes the asof at construction time?
        self._scan = scan

    @property
    def metrics(self) -> dict[str, Any]:
        """Returns metrics about the scan."""
        return self._scan.metrics()

    @property
    def schema(self) -> Schema:
        """Returns the schema of the scan."""
        return self._scan.schema()

    def is_empty(self) -> bool:
        """Check if the Spiral is empty for the given key range.

        **IMPORTANT**: False negatives are possible, but false positives are not,
            i.e. is_empty can return False and scan can return zero rows.
        """
        return self._scan.is_empty()

    def to_dataset(
        self,
        key_table: pa.Table | pa.RecordBatchReader | None = None,
    ) -> "pyarrow.dataset.Dataset":
        """Returns a PyArrow Dataset representing the scan.

        Args:
            key_table: a table of keys to "take" (including aux columns for cell-push-down).
                If None, the scan will be executed without a key table.
        """
        from .dataset import ScanDataset

        return ScanDataset(self, key_table=key_table)

    def to_record_batches(
        self,
        key_table: pa.Table | pa.RecordBatchReader | None = None,
        batch_size: int | None = None,
        batch_readahead: int | None = None,
    ) -> pa.RecordBatchReader:
        """Read as a stream of RecordBatches.

        Args:
            key_table: a table of keys to "take" (including aux columns for cell-push-down).
                If None, the scan will be executed without a key table.
            batch_size: the maximum number of rows per returned batch.
                IMPORTANT: This is currently only respected when the key_table is used. If key table is a
                    RecordBatchReader, the batch_size argument must be None, and the existing batching is respected.
            batch_readahead: the number of batches to prefetch in the background.
        """
        if isinstance(key_table, pa.RecordBatchReader):
            if batch_size is not None:
                raise ValueError(
                    "batch_size must be None when key_table is a RecordBatchReader, the existing batching is respected."
                )
        elif isinstance(key_table, pa.Table):
            key_table = key_table.to_reader(max_chunksize=batch_size)

        return self._scan.to_record_batches(key_table=key_table, batch_readahead=batch_readahead)

    def to_table(
        self,
        key_table: pa.Table | pa.RecordBatchReader | None = None,
    ) -> pa.Table:
        """Read into a single PyArrow Table.

        Args:
            key_table: a table of keys to "take" (including aux columns for cell-push-down).
                If None, the scan will be executed without a key table.
        """
        return self.to_record_batches(key_table=key_table).read_all()

    def to_dask(self) -> "dd.DataFrame":
        """Read into a Dask DataFrame.

        Requires the `dask` package to be installed.
        """
        import dask.dataframe as dd
        import pandas as pd

        def _read_key_range(key_range: KeyRange) -> pd.DataFrame:
            # TODO(ngates): we need a way to preserve the existing asofs? Should we copy CoreScan instead of Query?
            raise NotImplementedError()

        # Fetch a set of partition ranges
        return dd.from_map(_read_key_range, self.split())

    def to_pandas(
        self,
        key_table: pa.Table | pa.RecordBatchReader | None = None,
    ) -> "pd.DataFrame":
        """Read into a Pandas DataFrame.

        Requires the `pandas` package to be installed.

        Args:
            key_table: a table of keys to "take" (including aux columns for cell-push-down).
                If None, the scan will be executed without a key table.
        """
        return self.to_table(key_table=key_table).to_pandas()

    def to_polars(self, key_table: pa.Table | pa.RecordBatchReader | None = None) -> "pl.LazyFrame":
        """Read into a Polars LazyFrame.

        Requires the `polars` package to be installed.

        Args:
            key_table: a table of keys to "take" (including aux columns for cell-push-down).
                If None, the scan will be executed without a key table.
        """
        import polars as pl

        return pl.scan_pyarrow_dataset(self.to_dataset(key_table=key_table))

    def to_pytorch(
        self,
        key_table: pa.Table | pa.RecordBatchReader | None = None,
        batch_readahead: int | None = None,
    ) -> "iterable_dataset.IterableDataset":
        """Returns an iterable dataset that can be used to build a `pytorch.DataLoader`.

        Requires the `datasets` package to be installed.

        Args:
            key_table: a table of keys to "take" (including aux columns for cell-push-down).
                If None, the scan will be executed without a key table.
            batch_readahead: the number of batches to prefetch in the background.
        """
        from datasets.iterable_dataset import ArrowExamplesIterable, IterableDataset

        def _generate_tables(**kwargs) -> Iterator[tuple[int, pa.Table]]:
            # Use batch size 1 when iterating samples, unless batch reader is already used.
            stream = self.to_record_batches(
                key_table, batch_size=1 if isinstance(key_table, pa.Table) else None, batch_readahead=batch_readahead
            )

            # This key is unused when training with IterableDataset.
            # Default implementation returns shard id, e.g. parquet row group id.
            for i, rb in enumerate(stream):
                yield i, pa.Table.from_batches([rb], stream.schema)

        # NOTE: Type annotation Callable[..., tuple[str, pa.Table]] is wrong. The return value must be iterable.
        ex_iterable = ArrowExamplesIterable(generate_tables_fn=_generate_tables, kwargs={})
        return IterableDataset(ex_iterable=ex_iterable)

    def split(self) -> list[KeyRange]:
        return self._scan.split()

    def debug(self):
        # Visualizes the scan, mainly for debugging purposes.
        # NOTE: This is not part of the API and may disappear at any moment.
        from spiral.debug import show_scan

        show_scan(self._scan)
