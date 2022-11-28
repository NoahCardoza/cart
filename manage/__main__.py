import os
import sys

import stripe
import typer

CLI_DIR = os.path.dirname(os.path.abspath(__file__))
APP_DIR = os.path.dirname(CLI_DIR)

sys.path.append(APP_DIR)

from app.environ import STRIPE_PRIVATE_KEY  # noqa
from manage.database import db_app  # noqa
from manage.stripe_utils import stripe_app  # noqa

stripe.api_key = STRIPE_PRIVATE_KEY

app = typer.Typer(help="A colletion of commands to help with development.")

app.add_typer(db_app, name="db")
app.add_typer(stripe_app, name="stripe")

if __name__ == "__main__":
    app()
