"""Database schema commands."""

from __future__ import annotations

from pathlib import Path

import typer
from alembic.command import upgrade as alembic_upgrade
from alembic.config import Config

app = typer.Typer()

# backend/ — holds alembic.ini and the alembic/ script directory. Resolved from
# this file so the command works regardless of the current working directory.
_BACKEND_DIR = Path(__file__).resolve().parent.parent


def alembic_config() -> Config:
    """Build an Alembic config for this checkout's migrations.

    The database URL is not set here: ``alembic/env.py`` reads it from
    ``api.settings`` (environment / .env), same as the app does.
    """
    config = Config(str(_BACKEND_DIR / "alembic.ini"))
    config.set_main_option("script_location", str(_BACKEND_DIR / "alembic"))
    return config


@app.command("upgrade")
def upgrade(
    revision: str = typer.Argument("head", help="Target revision (default: head)"),
) -> None:
    """Apply migrations up to REVISION."""
    alembic_upgrade(alembic_config(), revision)
    typer.echo(f"Database upgraded to {revision}.")
