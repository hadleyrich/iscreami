"""Shared CLI driver for importer sub-commands (--list / --id / --all)."""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

import typer

from api.db import SessionLocal

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

    from cli.importers.base import BaseImporter


def run_import_command(
    make_importer: Callable[[Session], BaseImporter],
    target_id: str | None,
    all_foods: bool,
    list_only: bool,
    id_option: str,
) -> None:
    """Run an importer CLI command: --list, --id <ID>, or --all.

    Shared by all importers so the list/id/all dispatch and session
    handling stay consistent across sub-commands.
    """
    db = SessionLocal()
    try:
        importer = make_importer(db)

        if list_only:
            for fid, name in importer.list_foods():
                typer.echo(f"{fid}: {name}")
        elif target_id:
            result = importer.import_one(target_id)
            if result:
                typer.echo(f"Imported: {result.name}")
            else:
                typer.echo(f"Skipped (already exists): {target_id}")
            db.commit()
        elif all_foods:
            count = 0
            for name, result in importer.import_all():
                if result:
                    typer.echo(f"  + {name}")
                    count += 1
            typer.echo(f"Imported {count} ingredients.")
            db.commit()
        else:
            typer.echo(f"Specify --{id_option}, --all, or --list")
            raise typer.Exit(1)
    finally:
        db.close()
