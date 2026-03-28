"""Importer CLI sub-commands."""

from pathlib import Path

import typer

app = typer.Typer()


def nzfcdb_command(
    data_dir: Path = typer.Option(..., help="Path to NZ FOODfiles directory"),
    food_id: str | None = typer.Option(None, help="Specific food ID to import"),
    all_foods: bool = typer.Option(False, "--all", help="Import all foods"),
    list_only: bool = typer.Option(
        False, "--list", help="List available foods without importing"
    ),
) -> None:
    from cli.importers.nzfcdb import nzfcdb_command as _nzfcdb_command

    _nzfcdb_command(data_dir, food_id, all_foods, list_only)


def usda_command(
    json_file: Path = typer.Option(..., help="Path to FoodData Central bulk JSON file"),
    fdc_id: str | None = typer.Option(None, help="Specific FDC ID to import"),
    all_foods: bool = typer.Option(False, "--all", help="Import all foods"),
    list_only: bool = typer.Option(
        False, "--list", help="List available foods without importing"
    ),
) -> None:
    from cli.importers.usda import usda_command as _usda_command

    _usda_command(json_file, fdc_id, all_foods, list_only)


app.command("nzfcdb", help="Import from NZ Food Composition Database")(nzfcdb_command)
app.command("usda", help="Import from USDA FoodData Central")(usda_command)
