"""Python client for the Spiral warehouse."""

from spiral import _lib
from spiral.catalog import Spiral
from spiral.maintenance import Maintenance
from spiral.scan_ import Scan, scan
from spiral.table import Table
from spiral.txn import Transaction

# Eagerly import the Spiral library
assert _lib, "Spiral library"

__all__ = ["scan", "Scan", "Table", "Spiral", "Transaction", "Maintenance"]
