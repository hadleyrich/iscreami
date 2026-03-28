"""NZFCDB (NZ Food Composition Database) importer.

Parses .FT (tilde-delimited) files from NZ FOODfiles.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import typer

from api.db import SessionLocal
from api.schemas import IngredientCreate
from cli.importers.base import BaseImporter

# Mapping from NZFCDB nutrient component codes → iscreami fields
NUTRIENT_MAP: dict[str, str] = {
    "WATER": "water_pct",
    "FAT": "total_fat_pct",
    "FASAT": "saturated_fat_pct",
    "FATRN": "trans_fat_pct",
    "PROT": "protein_pct",
    "CHOCDF": "carbohydrate_pct",  # Total carbohydrate by difference
    "FIBTG": "fiber_pct",
    "SUGAR": "total_sugar_pct",
    "ENERC": "energy_kj_per_100g",  # Energy in kJ (direct)
    "ALC": "alcohol_pct",
    "NA": "sodium_mg",
    # Sugar breakdown
    "SUCS": "sucrose_pct",
    "GLUS": "glucose_pct",
    "FRUS": "fructose_pct",
    "LACS": "lactose_pct",
    "MALS": "maltose_pct",
    "GALS": "galactose_pct",
}


# Map from NZFCDB food chapter letter (first char of FoodID) → category slug
# Based on Table 2 of the NZ FOODfiles 2024 Data Manual.
CHAPTER_CATEGORY: dict[str, str] = {
    "A": "other",  # Bakery products
    "B": "alcohol",  # Beverages, alcoholic
    "C": "other",  # Beverages, non-alcoholic (cocoa powder, plant-based milks, juices)
    "D": "other",  # Breakfast cereals
    "E": "other",  # Cereals and pseudo-cereals
    "F": "dairy",  # Dairy (butters, cheeses, creams, milks, ice creams, yoghurt)
    "G": "egg",  # Eggs
    "J": "fat_oil",  # Fats and oils
    "L": "fruit",  # Fruits
    "P": "other",  # Miscellaneous (spices, herbs, dairy-free alternatives)
    "Q": "nuts-seeds",  # Nuts and seeds
    "R": "other",  # Recipes (derived calculations, not raw ingredients)
    "S": "other",  # Sauces
    "U": "other",  # Snack foods
    "W": "other",  # Sugars, confectionaries and sweet spreads
}

# Per-food-ID category overrides — takes precedence over CHAPTER_CATEGORY.
# Use this when a food belongs to a different category than its chapter default.
FOOD_ID_CATEGORY: dict[str, str] = {
    # Chapter W — sweeteners (sugars, syrups, honeys, treacle, molasses)
    "W10": "sweetener",  # Glucose liquid, BP
    "W12": "sweetener",  # Honey, comb
    "W19": "sweetener",  # Sugar, brown
    "W20": "sweetener",  # Sugar, caster
    "W21": "sweetener",  # Sugar, coffee
    "W22": "sweetener",  # Sugar, demerara
    "W23": "sweetener",  # Sugar, raw
    "W24": "sweetener",  # Sugar, white
    "W25": "sweetener",  # Syrup, golden
    "W27": "sweetener",  # Treacle, black
    "W32": "sweetener",  # Sugar, icing
    "W69": "sweetener",  # Syrup, malt
    "W70": "sweetener",  # Molasses
    "W1018": "sweetener",  # Honey, mono-floral, manuka
    "W1019": "sweetener",  # Honey, multifloral
    # Chapter W — chocolate products
    "W3": "chocolate",  # Chocolate bar, milk
    "W4": "chocolate",  # Chocolate bar, plain
    "W5": "chocolate",  # Chocolate, milk chocolate with coconut centre, Bounty
    "W6": "chocolate",  # Chocolate bar, Mars
    "W7": "chocolate",  # Chocolate, fancy & filled
    "W16": "chocolate",  # Spread, hazelnut, Nutella
    "W46": "chocolate",  # Sauce, chocolate, composite
    "W47": "chocolate",  # Sauce, chocolate, Hershey's
    "W53": "chocolate",  # Nut, peanut, coated with milk chocolate
    "W54": "chocolate",  # Chocolate, caramel, chocolate coated
    "W58": "chocolate",  # Chocolate, white chocolate, Milky Bar
    "W60": "chocolate",  # Chocolate, milk chocolate with caramel, Caramello
    "W61": "chocolate",  # Chocolate, milk chocolate with caramel, bite size
    "W68": "chocolate",  # Chocolate bar, milk chocolate with peanut, Moro
    "W1009": "chocolate",  # Chocolate, caramel & nougat whip, Moro
    "W1010": "chocolate",  # Chocolate, milk chocolate with sultanas & almond, Dairy Milk Fruit & Nut
    "W1011": "chocolate",  # Chocolate, block & slab, Whittaker's
    "W1012": "chocolate",  # Chocolate, rich chocolate, Energy, Cadbury
    "W1013": "chocolate",  # Chocolate, milk chocolate with golden honeycomb, Dairy Milk Crunchie
    "W1014": "chocolate",  # Chocolate bar, Gold Totally Nuts Bar, Moro
    "W1015": "chocolate",  # Chocolate, compound, composite
    "W1025": "chocolate",  # Dark chocolate, cocoa solids 45–69%
    "W1026": "chocolate",  # Dark chocolate, cocoa solids 70–84%
    "W1027": "chocolate",  # Dark chocolate, cocoa solids >85%
    "W1028": "chocolate",  # White chocolate, plain
    "W1029": "chocolate",  # Milk chocolate, plain
}

# Chapters excluded as not relevant to ice cream — meats, fish, grains, fast food, etc.
# Any chapter not in CHAPTER_CATEGORY is also implicitly excluded.
EXCLUDED_CHAPTERS: frozenset[str] = frozenset(
    {
        "H",  # Fast foods and ready-to-eat meals
        "K",  # Fin fishes
        "M",  # Meats
        "N",  # Meat products
        "T",  # Shellfishes
        "V",  # Soups
        "X",  # Vegetables and pulses
    }
)


def _parse_ft_file(path: Path) -> tuple[list[str], list[list[str]]]:
    """Parse a tilde-delimited .FT file.

    Line 1: copyright (skip)
    Line 2: headers
    Line 3+: data rows
    """
    lines = path.read_text(encoding="utf-8").strip().splitlines()
    if len(lines) < 2:
        return [], []

    headers = [h.strip() for h in lines[1].split("~")]
    rows = []
    for line in lines[2:]:
        if line.strip():
            rows.append([c.strip() for c in line.split("~")])
    return headers, rows


class NZFCDBImporter(BaseImporter):
    source_name = "nzfcdb"

    def __init__(self, db, data_dir: Path) -> None:
        super().__init__(db)
        self.data_dir = data_dir
        self._foods: dict[str, dict[str, str]] = {}
        self._nutrients: dict[str, dict[str, float]] = {}
        self._loaded = False

    def _load_foods(self) -> None:
        food_file = self.data_dir / "Supporting files" / "ASCII Text Files" / "NAME.FT"
        if not food_file.exists():
            return
        headers, rows = _parse_ft_file(food_file)
        for row in rows:
            rec = dict(zip(headers, row))
            food_id = rec.get("FoodID", "").strip()
            if food_id:
                self._foods[food_id] = rec

    def _load_nutrients(self) -> None:
        nutrient_file = (
            self.data_dir
            / "Principal files"
            / "ASCII Text Files"
            / "Standard"
            / "Standard DATA.FT"
        )
        if not nutrient_file.exists():
            return
        headers, rows = _parse_ft_file(nutrient_file)
        for row in rows:
            rec = dict(zip(headers, row))
            food_id = rec.get("FoodID", "").strip()
            component = rec.get("Component Identifier", "").strip()
            value_str = rec.get("Value", "").strip()
            if food_id and component and value_str:
                try:
                    value = float(value_str)
                except ValueError:
                    continue
                if food_id not in self._nutrients:
                    self._nutrients[food_id] = {}
                self._nutrients[food_id][component] = value

    def _load(self) -> None:
        if self._loaded:
            return
        self._load_foods()
        self._load_nutrients()
        self._loaded = True

    def fetch(self, source_id: str) -> dict[str, Any]:
        self._load()
        food = self._foods.get(source_id, {})
        nutrients = self._nutrients.get(source_id, {})
        return {"food": food, "nutrients": nutrients, "source_id": source_id}

    def map(self, raw: dict[str, Any]) -> IngredientCreate:
        food = raw["food"]
        nutrients = raw["nutrients"]

        name = food.get("Food Name", f"NZFCDB {raw['source_id']}")

        data: dict[str, Any] = {"name": name}

        for nz_code, field in NUTRIENT_MAP.items():
            if nz_code in nutrients:
                data[field] = nutrients[nz_code]

        # Parse alternative names into aliases — separator is " , " (space-comma-space)
        alt_raw = food.get("AlternativeNames", "").strip()
        if alt_raw:
            data["aliases"] = [a.strip() for a in alt_raw.split(" , ") if a.strip()]

        # Guess category from food name (no FoodGroup field in FOODfiles 2024)
        data["category_id"] = self._guess_category(food)

        return IngredientCreate(**data)

    def _guess_category(self, food: dict[str, str]) -> int | None:
        food_id = food.get("FoodID", "")
        if food_id in FOOD_ID_CATEGORY:
            return self._resolve_category(FOOD_ID_CATEGORY[food_id])
        chapter = food_id[0].upper() if food_id else ""
        slug = CHAPTER_CATEGORY.get(chapter, "other")
        return self._resolve_category(slug)

    def list_foods(self) -> list[tuple[str, str]]:
        """List food IDs and names relevant to ice cream (excluded chapters filtered out)."""
        self._load()
        return [
            (fid, f.get("Food Name", "?"))
            for fid, f in sorted(self._foods.items())
            if fid and fid[0].upper() not in EXCLUDED_CHAPTERS
        ]


def nzfcdb_command(
    data_dir: Path = typer.Option(..., help="Path to NZ FOODfiles directory"),
    food_id: str | None = typer.Option(None, help="Specific food ID to import"),
    all_foods: bool = typer.Option(False, "--all", help="Import all foods"),
    list_only: bool = typer.Option(
        False, "--list", help="List available foods without importing"
    ),
) -> None:
    """Import ingredients from NZ Food Composition Database .FT files."""
    db = SessionLocal()
    try:
        importer = NZFCDBImporter(db, data_dir)

        if list_only:
            for fid, name in importer.list_foods():
                typer.echo(f"{fid}: {name}")
        elif food_id:
            result = importer.import_one(food_id)
            if result:
                typer.echo(f"Imported: {result.name}")
            else:
                typer.echo(f"Skipped (already exists): {food_id}")
            db.commit()
        elif all_foods:
            count = 0
            for fid, name in importer.list_foods():
                result = importer.import_one(fid)
                if result:
                    typer.echo(f"  + {name}")
                    count += 1
            typer.echo(f"Imported {count} ingredients.")
            db.commit()
        else:
            typer.echo("Specify --food-id, --all, or --list")
            raise typer.Exit(1)
    finally:
        db.close()
