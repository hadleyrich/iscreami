"""CLI entry point for iscreami admin commands."""

import typer

# Settings auto-loads from .env when imported
from api.settings import settings  # noqa: F401
from cli.importers import app as import_app
from cli.seed import app as seed_app

app = typer.Typer(help="iscreami admin CLI")
app.add_typer(seed_app, name="seed", help="Seed database with default data")
app.add_typer(
    import_app, name="import", help="Import ingredients from external sources"
)

if __name__ == "__main__":
    app()
