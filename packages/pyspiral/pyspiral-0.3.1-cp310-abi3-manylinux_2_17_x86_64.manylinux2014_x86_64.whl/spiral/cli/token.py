from typing import Annotated

import rich
from typer import Argument, Option

from spiral.api.tokens import ListTokens, RevokeToken, Token
from spiral.cli import AsyncTyper, OptionalStr, printer, state
from spiral.cli.types import ProjectArg

app = AsyncTyper()


@app.command(help="List tokens.")
def ls(
    project: ProjectArg,
    on_behalf_of: Annotated[OptionalStr, Option(help="Filter by on behalf of.")] = None,
):
    tokens = list(state.settings.api.token.list(ListTokens.Request(project_id=project, on_behalf_of=on_behalf_of)))
    rich.print(printer.table_of_models(Token, tokens, fields=["id", "project_id", "on_behalf_of"]))


@app.command(help="Revoke a token.")
def revoke(token_id: Annotated[str, Argument(help="Token ID.")]):
    res = state.settings.api.token.revoke(RevokeToken.Request(token_id=token_id))
    rich.print(
        f"Revoked token {res.token.id} for project {res.token.project_id} acting on behalf of {res.token.on_behalf_of}"
    )
