from typing import Annotated

import questionary
import rich
from typer import Option

from spiral.api.filesystems import BuiltinFileSystem, GetFileSystem, UpdateFileSystem
from spiral.cli import AsyncTyper, state
from spiral.cli.types import ProjectArg

app = AsyncTyper()


@app.command(help="Show the file system configured for project.")
def show(project: ProjectArg):
    res = state.settings.api.file_system.get_file_system(GetFileSystem.Request(project_id=project))
    match res.file_system:
        case BuiltinFileSystem(provider=provider):
            rich.print(f"provider: {provider}")
        case _:
            rich.print(res.file_system)


def _provider_default():
    res = state.settings.api.file_system.list_providers()
    return questionary.select("Select a file system provider", choices=res.providers).ask()


ProviderOpt = Annotated[
    str,
    Option(help="Built-in provider to use for the file system.", show_default=False, default_factory=_provider_default),
]


@app.command(help="Update a project's file system.")
def update(project: ProjectArg, provider: ProviderOpt):
    res = state.settings.api.file_system.update_file_system(
        UpdateFileSystem.Request(project_id=project, file_system=BuiltinFileSystem(provider=provider))
    )
    rich.print(res.file_system)


@app.command(help="Lists the available built-in file system providers.")
def list_providers():
    res = state.settings.api.file_system.list_providers()
    for provider in res.providers:
        rich.print(provider)
