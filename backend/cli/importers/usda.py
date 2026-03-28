"""USDA FoodData Central importer.

Reads FoodData Central bulk JSON exports (Foundation, Survey, or Branded Foods).
Download from: https://fdc.nal.usda.gov/download-datasets

All three export types are supported and auto-detected from the file.
Uses streaming JSON parsing (ijson) so even the 3 GB Branded Foods file
is processed without loading everything into memory at once.
"""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path
from typing import TYPE_CHECKING, Any

import ijson  # type: ignore[import-untyped]
import typer

from api.db import SessionLocal
from api.schemas import IngredientCreate
from cli.importers.base import BaseImporter

if TYPE_CHECKING:
    from api.models import Ingredient

# Top-level JSON array keys for each FDC export type
DATASET_KEYS = {"FoundationFoods", "SurveyFoods", "BrandedFoods"}

# USDA nutrient IDs → iscreami fields
NUTRIENT_ID_MAP: dict[int, str] = {
    1051: "water_pct",  # Water
    1004: "total_fat_pct",  # Total lipid (fat)
    1258: "saturated_fat_pct",  # Fatty acids, total saturated
    1257: "trans_fat_pct",  # Fatty acids, total trans
    1003: "protein_pct",  # Protein
    1005: "carbohydrate_pct",  # Carbohydrate, by difference
    1079: "fiber_pct",  # Fiber, total dietary
    2000: "total_sugar_pct",  # Sugars, total including NLEA
    1008: "energy_kj_per_100g",  # Energy (kcal → converted to kJ in map())
    1018: "alcohol_pct",  # Alcohol, ethyl
    1093: "sodium_mg",  # Sodium, Na
    # Sugar breakdown
    1010: "sucrose_pct",  # Sucrose
    1011: "glucose_pct",  # Glucose
    1012: "fructose_pct",  # Fructose
    1013: "lactose_pct",  # Lactose
    1014: "maltose_pct",  # Maltose
    1075: "galactose_pct",  # Galactose
}

# Foundation Foods foodCategory.description → iscreami category slug
CATEGORY_MAP: dict[str, str] = {
    "dairy and egg products": "dairy",
    "sweets": "sweetener",
    "fruits and fruit juices": "fruit",
    "fats and oils": "fat_oil",
    "vegetables and vegetable products": "fruit",  # nearest available
    "nut and seed products": "other",
    "legumes and legume products": "other",
    "cereal grains and pasta": "other",
    "beverages": "other",
    "spices and herbs": "other",
    "baked products": "other",
    "soups, sauces, and gravies": "other",
    "beef products": "other",
    "pork products": "other",
    "poultry products": "other",
    "lamb, veal, and game products": "other",
    "finfish and shellfish products": "other",
    "sausages and luncheon meats": "other",
    "restaurant foods": "other",
}

# Food name keyword → category slug (fallback for survey/branded/unknown)
KEYWORD_CATEGORY: list[tuple[list[str], str]] = [
    (
        [
            "milk",
            "dairy",
            "cream",
            "cheese",
            "butter",
            "yoghurt",
            "yogurt",
            "ice cream",
        ],
        "dairy",
    ),
    (
        [
            "sugar",
            "honey",
            "syrup",
            "sweetener",
            "glucose",
            "fructose",
            "stevia",
            "erythritol",
        ],
        "sweetener",
    ),
    (["fruit", "berry", "berries", "juice"], "fruit"),
    (["oil", "margarine", "lard", "shortening"], "fat_oil"),
]


class USDAImporter(BaseImporter):
    source_name = "usda"

    def __init__(self, db, json_file: Path) -> None:
        super().__init__(db)
        self.json_file = json_file
        self._array_key: str | None = None

    def _get_array_key(self) -> str:
        """Auto-detect which FDC dataset type this file contains."""
        if self._array_key is not None:
            return self._array_key
        with open(self.json_file, "rb") as f:
            for _prefix, event, value in ijson.parse(f):
                if event == "map_key" and value in DATASET_KEYS:
                    self._array_key = value
                    return value
        raise ValueError(f"No recognised FDC dataset key found in {self.json_file}")

    def _stream_foods(self) -> Iterator[dict[str, Any]]:
        """Stream food records one at a time — works for files of any size."""
        array_key = self._get_array_key()
        with open(self.json_file, "rb") as f:
            yield from ijson.items(f, f"{array_key}.item")

    def fetch(self, source_id: str) -> dict[str, Any]:
        """Scan through the file to find a food by fdcId."""
        for food in self._stream_foods():
            if str(int(food.get("fdcId") or 0)) == source_id:
                return food
        return {}

    def map(self, raw: dict[str, Any]) -> IngredientCreate:
        name = raw.get("description", f"USDA {raw.get('fdcId', '?')}")
        data: dict[str, Any] = {"name": name}

        for fn in raw.get("foodNutrients", []):
            nutrient_id = int(fn.get("nutrient", {}).get("id") or 0)
            amount = float(fn.get("amount") or 0)
            if nutrient_id in NUTRIENT_ID_MAP:
                field = NUTRIENT_ID_MAP[nutrient_id]
                if field == "sodium_mg":
                    amount = max(0.0, min(amount, 99999.9999))
                elif field == "energy_kj_per_100g":
                    amount = round(amount * 4.184, 2)  # kcal → kJ
                else:
                    amount = max(0.0, min(amount, 100.0))
                data[field] = amount

        data["category_id"] = self._guess_category(raw)
        return IngredientCreate(**data)

    def _guess_category(self, food: dict[str, Any]) -> int | None:
        # Foundation Foods: foodCategory.description
        cat_desc = str(food.get("foodCategory", {}).get("description") or "")
        # Survey Foods: wweiaFoodCategory.wweiaFoodCategoryDescription
        if not cat_desc:
            cat_desc = str(
                food.get("wweiaFoodCategory", {}).get("wweiaFoodCategoryDescription")
                or ""
            )
        # Branded Foods: brandedFoodCategory (plain string)
        if not cat_desc:
            cat_desc = str(food.get("brandedFoodCategory") or "")

        slug = CATEGORY_MAP.get(cat_desc.lower())
        if slug:
            return self._resolve_category(slug)

        # Fall back to food name keyword matching
        name = str(food.get("description") or "").lower()
        for keywords, kw_slug in KEYWORD_CATEGORY:
            if any(w in name for w in keywords):
                return self._resolve_category(kw_slug)
        return self._resolve_category("other")

    def list_foods(self) -> list[tuple[str, str]]:
        """Stream the file to collect all (fdcId, description) pairs."""
        return [
            (str(int(f.get("fdcId") or 0)), str(f.get("description") or "?"))
            for f in self._stream_foods()
            if f.get("fdcId")
        ]

    def import_all(
        self, skip_existing: bool = True
    ) -> Iterator[tuple[str, Ingredient | None]]:
        """Stream the file once, yielding (name, ingredient) — never scans N times."""
        for food in self._stream_foods():
            fdc_id = food.get("fdcId")
            if not fdc_id:
                continue
            source_id = str(int(fdc_id))
            name = str(food.get("description") or source_id)
            if skip_existing and self._ingredient_exists(source_id):
                yield name, None
                continue
            schema = self.map(food)
            ingredient = self._build_ingredient(schema, source_id)
            self.db.add(ingredient)
            yield name, ingredient


def usda_command(
    json_file: Path = typer.Option(..., help="Path to FoodData Central bulk JSON file"),
    fdc_id: str | None = typer.Option(None, help="Specific FDC ID to import"),
    all_foods: bool = typer.Option(False, "--all", help="Import all foods"),
    list_only: bool = typer.Option(
        False, "--list", help="List available foods without importing"
    ),
) -> None:
    """Import ingredients from a USDA FoodData Central bulk JSON (Foundation, Survey, or Branded)."""
    db = SessionLocal()
    try:
        importer = USDAImporter(db, json_file)

        if list_only:
            for fid, name in importer.list_foods():
                typer.echo(f"{fid}: {name}")
        elif fdc_id:
            result = importer.import_one(fdc_id)
            if result:
                typer.echo(f"Imported: {result.name}")
            else:
                typer.echo(f"Skipped (already exists): {fdc_id}")
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
            typer.echo("Specify --fdc-id, --all, or --list")
            raise typer.Exit(1)
    finally:
        db.close()
