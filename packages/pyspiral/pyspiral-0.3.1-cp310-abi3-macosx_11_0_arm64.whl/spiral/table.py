from datetime import datetime
from typing import TYPE_CHECKING, Literal

import pyarrow as pa

from spiral.core.core import Table as CoreTable
from spiral.core.core import TableMaintenance, TableTransaction
from spiral.core.spec import Schema
from spiral.expressions.base import Expr, ExprLike
from spiral.maintenance import Maintenance
from spiral.settings import FILE_FORMAT
from spiral.txn import Transaction

if TYPE_CHECKING:
    import duckdb
    import polars as pl
    import pyarrow.dataset

    from spiral.scan_ import Scan


class Table(Expr):
    """API for interacting with a SpiralDB's Table.

    Different catalog implementations should ultimately construct a Table object.
    """

    def __init__(
        self,
        table: CoreTable,
        name: str | None = None,
    ):
        super().__init__(table.__expr__)

        self._table = table
        self._name = name or self._table.id
        self._key_schema = self._table.key_schema.to_arrow()
        self._key_columns = set(self._key_schema.names)

    @property
    def table_id(self) -> str:
        return self._table.id

    @property
    def last_modified_at(self) -> int:
        return self._table.get_wal(asof=None).last_modified_at

    def __str__(self):
        return self._name

    def __repr__(self):
        return f'Table("{self._name}")'

    def __getitem__(self, item: str) -> Expr:
        from spiral import expressions as se

        if item in self._key_columns:
            return se.key(name=item)

        return super().__getitem__(item)

    def select(self, *paths: str, exclude: list[str] = None) -> "Expr":
        # Override an expression select in the root column group to split between keys and columns.
        if exclude is not None:
            if set(exclude) & self._key_columns:
                raise ValueError(
                    "Cannot use 'exclude' arg with key columns. Use 'exclude_keys' and an explicit select of keys."
                )

        key_paths = set(paths) & self._key_columns
        other_paths = set(paths) - key_paths
        if not key_paths:
            return super().select(*paths, exclude=exclude)

        from spiral import expressions as se

        return se.merge(se.pack({key: se.key(key) for key in key_paths}), super().select(*other_paths, exclude=exclude))

    @property
    def key_schema(self) -> pa.Schema:
        """Returns the key schema of the table."""
        return self._key_schema

    @property
    def schema(self) -> Schema:
        """Returns the FULL schema of the table.

        NOTE: This can be expensive for large tables.
        """
        return self._table.get_schema(asof=None)

    def to_dataset(self) -> "pyarrow.dataset.Dataset":
        """Returns a PyArrow Dataset representing the table."""
        from .dataset import TableDataset

        return TableDataset(self)

    def to_polars(self) -> "pl.LazyFrame":
        """Returns a Polars LazyFrame for the Spiral table."""
        import polars as pl

        return pl.scan_pyarrow_dataset(self.to_dataset())

    def to_duckdb(self) -> "duckdb.DuckDBPyRelation":
        """Returns a DuckDB relation for the Spiral table."""
        import duckdb

        return duckdb.from_arrow(self.to_dataset())

    def scan(
        self,
        *projections: ExprLike,
        where: ExprLike | None = None,
        asof: datetime | int | str = None,
        exclude_keys: bool = False,
    ) -> "Scan":
        """Reads the table. If projections are not provided, the entire table is read.

        See `spiral.scan` for more information.
        """
        from spiral.scan_ import scan

        if not projections:
            projections = [self]

        return scan(
            *projections,
            where=where,
            asof=asof,
            exclude_keys=exclude_keys,
        )

    # NOTE: "vortex" is valid format. We don't want that visible in the API docs.
    def write(
        self,
        expr: ExprLike,
        *,
        format: Literal["parquet"] | None = None,
        partition_size_bytes: int | None = None,
    ) -> None:
        """Write an item to the table inside a single transaction.

        :param expr: The expression to write. Must evaluate to a struct array.
        :param format: the format to write the data in. Defaults to "parquet".
        :param partition_size_bytes: The maximum partition size in bytes.
        """
        format = format or FILE_FORMAT

        with self.txn(format=format) as txn:
            txn.write(
                expr,
                partition_size_bytes=partition_size_bytes,
            )

    # NOTE: "vortex" is valid format. We don't want that visible in the API docs.
    def txn(self, format: Literal["parquet"] | None = None) -> Transaction:
        """Begins a new transaction. Transaction must be committed for writes to become visible.

        IMPORTANT: While transaction can be used to atomically write data to the table,
             it is important that the primary key columns are unique within the transaction.

        :param format: The format to use for the transaction. Defaults to "parquet".
        """
        return Transaction(TableTransaction(self._table.metastore, format or FILE_FORMAT))

    def maintenance(self, format: Literal["parquet"] | None = None) -> Maintenance:
        """Maintenance tasks for the table.

        :param format: The format to use. Defaults to "parquet".
        """
        return Maintenance(TableMaintenance(self._table.metastore, format or FILE_FORMAT))
