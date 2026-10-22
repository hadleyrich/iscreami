"""Tests for the `db` CLI commands."""

from __future__ import annotations

from pathlib import Path

from alembic.script import ScriptDirectory
from typer.testing import CliRunner

from cli.db import alembic_config
from cli.main import app


def test_alembic_config_points_at_this_checkout() -> None:
    config = alembic_config()

    script_location = config.get_main_option("script_location")
    assert script_location is not None
    assert Path(script_location).name == "alembic"
    assert (Path(script_location) / "env.py").is_file()

    # The migration chain must resolve to exactly one head, otherwise
    # `db upgrade` would need an explicit revision.
    assert len(ScriptDirectory.from_config(config).get_heads()) == 1


def test_upgrade_applies_requested_revision(monkeypatch) -> None:
    revisions: list[str] = []
    monkeypatch.setattr(
        "cli.db.alembic_upgrade", lambda config, revision: revisions.append(revision)
    )

    result = CliRunner().invoke(app, ["db", "upgrade", "abc123"])

    assert result.exit_code == 0, result.output
    assert revisions == ["abc123"]
    assert "Database upgraded to abc123." in result.output


def test_upgrade_defaults_to_head(monkeypatch) -> None:
    revisions: list[str] = []
    monkeypatch.setattr(
        "cli.db.alembic_upgrade", lambda config, revision: revisions.append(revision)
    )

    result = CliRunner().invoke(app, ["db", "upgrade"])

    assert result.exit_code == 0, result.output
    assert revisions == ["head"]
