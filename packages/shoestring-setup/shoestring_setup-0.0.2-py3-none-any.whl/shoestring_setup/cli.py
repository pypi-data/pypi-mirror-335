"""Console script for shoestring_assembler."""

import shoestring_setup as shoestring_setup_top
from shoestring_setup import display, shoestring_setup


import typer
from typing_extensions import Annotated


app = typer.Typer(name="Shoestring Setup Utility", no_args_is_help=True)


@app.command()
def main(
    update: Annotated[
        bool, typer.Option("--update", help="Attempt to update all dependencies")
    ] = False,
    force: Annotated[
        bool, typer.Option("--force", help="Ignore existing versions and perform install")
    ] = False,
    version: Annotated[
        bool, typer.Option("--version", "-v", help="Setup Utility version")
    ] = False,
):
    if version:
        display.print_log(
            f"Shoestring Setup Utility version {shoestring_setup_top.__version__}"
        )
    else:
        display.print_top_header("Installing Dependencies")
        shoestring_setup.install(update, force)
        display.print_top_header("Finished")


if __name__ == "__main__":
    app()


"""
* shoestring
    * assemble
    * update
    * check-recipe
    * install_docker
    * check_docker
    * bootstrap (maybe for a separate developer focussed tool?)
"""
