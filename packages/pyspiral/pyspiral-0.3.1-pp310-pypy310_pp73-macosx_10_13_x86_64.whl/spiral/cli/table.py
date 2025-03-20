from typing import Annotated

import rich
from typer import Option

from spiral.api.tables import ListTables, Table
from spiral.cli import AsyncTyper, OptionalStr, printer, state
from spiral.cli.types import ProjectArg

app = AsyncTyper()


@app.command(help="List tables.")
def ls(
    project: ProjectArg,
    dataset: Annotated[OptionalStr, Option(help="Filter by dataset name.")] = None,
):
    """List tables."""
    tables = list(state.settings.api.table.list(ListTables.Request(project_id=project, dataset=dataset)))
    rich.print(printer.table_of_models(Table, tables, fields=["id", "project_id", "dataset", "table"]))
