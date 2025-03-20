import logging
import os
from logging.handlers import RotatingFileHandler

from spiral.cli import AsyncTyper, admin, console, fs, login, org, project, state, table, token, workload
from spiral.settings import LOG_DIR, Settings

app = AsyncTyper(name="spiral")


@app.callback()
def _callback(verbose: bool = False):
    if verbose:
        logging.getLogger().setLevel(level=logging.INFO)

    # Load the settings (we reload in the callback to support testing under different env vars)
    state.settings = Settings()


app.add_typer(fs.app, name="fs")
app.add_typer(org.app, name="org")
app.add_typer(project.app, name="project")
app.add_typer(table.app, name="table")
app.add_typer(workload.app, name="workload")
app.add_typer(token.app, name="token")
app.command("console")(console.command)
app.command("login")(login.command)

# Register unless we're building docs. Because Typer docs command does not skip hidden commands...
if not bool(os.environ.get("SPIRAL_DOCS", False)):
    app.add_typer(admin.app, name="admin", hidden=True)
    app.command("logout", hidden=True)(login.logout)


def main():
    # Setup rotating CLI logging.
    # NOTE(ngates): we should do the same for the Spiral client? Maybe move this logic elsewhere?
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.DEBUG,
        handlers=[RotatingFileHandler(LOG_DIR / "cli.log", maxBytes=2**20, backupCount=10)],
    )

    app()


if __name__ == "__main__":
    main()
