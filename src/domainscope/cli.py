
from importlib.metadata import version

import typer

app = typer.Typer(no_args_is_help=True)


def _version_callback(value: bool):
    if value:
        print(f"Domain Scope {version('domainscope')}")
        raise typer.Exit()


@app.callback()
def main(
    show_version: bool = typer.Option(
        False, "--version", "-V", callback=_version_callback, is_eager=True,
        help="Show the version and exit.")):
    """Domain Scoping Tool, offering a variety of utilities helping the system administrator or hosting engineer/technician"""


