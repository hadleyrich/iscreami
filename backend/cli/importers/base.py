"""Abstract base class for ingredient importers."""

from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from api.models import Ingredient, IngredientAlias, IngredientCategory
from api.schemas import IngredientCreate


class BaseImporter(ABC):
    """Base class for all ingredient importers."""

    source_name: str = "unknown"
    import_id_namespace: uuid.UUID = uuid.UUID("14c45863-aa22-4d80-8ff0-decd5941e901")

    def __init__(self, db: Session) -> None:
        self.db = db
        self._category_cache: dict[str, int] = {}

    def _resolve_category(self, slug: str) -> int | None:
        """Look up category ID by slug, with caching."""
        if slug in self._category_cache:
            return self._category_cache[slug]
        cat = self.db.scalar(
            select(IngredientCategory).where(IngredientCategory.slug == slug)
        )
        if cat:
            self._category_cache[slug] = cat.id
            return cat.id
        return None

    def _ingredient_exists(self, source_id: str) -> bool:
        """Check if an ingredient from this source already exists."""
        return (
            self.db.scalar(
                select(Ingredient).where(
                    Ingredient.source == self.source_name,
                    Ingredient.source_id == source_id,
                )
            )
            is not None
        )

    def _deterministic_ingredient_id(self, source_id: str) -> uuid.UUID:
        """Build a stable UUID for imported ingredients from source + source_id."""
        return uuid.uuid5(self.import_id_namespace, f"{self.source_name}:{source_id}")

    def _build_ingredient(self, schema: IngredientCreate, source_id: str) -> Ingredient:
        """Convert schema into an Ingredient ORM instance with deterministic ID."""
        data = schema.model_dump()
        data["id"] = self._deterministic_ingredient_id(source_id)
        data["source"] = self.source_name
        data["source_id"] = source_id
        alias_names_raw: list[str] = data.pop("aliases", [])

        ingredient = Ingredient(**data)
        if alias_names_raw:
            ingredient.aliases = [IngredientAlias(alias=a) for a in alias_names_raw]
        return ingredient

    @abstractmethod
    def fetch(self, source_id: str) -> dict[str, Any]:
        """Fetch raw data for a single item from the source."""
        ...

    @abstractmethod
    def map(self, raw: dict[str, Any]) -> IngredientCreate:
        """Map raw source data to our IngredientCreate schema."""
        ...

    def import_one(
        self, source_id: str, skip_existing: bool = True
    ) -> Ingredient | None:
        """Import a single ingredient by source ID."""
        if skip_existing and self._ingredient_exists(source_id):
            return None

        raw = self.fetch(source_id)
        schema = self.map(raw)
        ingredient = self._build_ingredient(schema, source_id)
        self.db.add(ingredient)
        return ingredient
