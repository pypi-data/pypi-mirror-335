import typer

import igs_toolbox


def version_callback(value: bool) -> None:  # noqa: FBT001
    """Print toolbox version."""
    if value:
        print(f"IGS Toolbox Version: {igs_toolbox.__version__}")  # noqa: T201
        raise typer.Exit
