"""Tests for importer identity behavior."""

from __future__ import annotations

import uuid

from api.schemas import IngredientCreate
from cli.importers.base import BaseImporter


class DummyImporter(BaseImporter):
    source_name = "dummy"

    def fetch(self, source_id: str) -> dict[str, str]:
        return {"source_id": source_id, "name": f"Item {source_id}"}

    def map(self, raw: dict[str, str]) -> IngredientCreate:
        return IngredientCreate(name=raw["name"])


def test_import_one_uses_deterministic_uuid(test_db):
    importer = DummyImporter(test_db)

    item = importer.import_one("abc-123", skip_existing=False)

    assert item is not None
    expected = uuid.uuid5(importer.import_id_namespace, "dummy:abc-123")
    assert item.id == expected
    assert item.source == "dummy"
    assert item.source_id == "abc-123"


def test_import_one_skip_existing_detects_existing_source_row(test_db):
    importer = DummyImporter(test_db)

    first = importer.import_one("abc-123")
    assert first is not None
    test_db.flush()

    second = importer.import_one("abc-123")
    assert second is None
