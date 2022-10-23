import os
import sys

import typer

CLI_DIR = os.path.dirname(os.path.abspath(__file__))
APP_DIR = os.path.dirname(CLI_DIR)

sys.path.append(APP_DIR)

from manage.database import db_app  # noqa

app = typer.Typer(help="A colletion of commands to help with development.")

app.add_typer(db_app, name="db")

if __name__ == "__main__":
    app()
