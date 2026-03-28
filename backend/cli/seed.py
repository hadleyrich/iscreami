"""Seed database with default categories, target profiles, and common ingredients."""

from __future__ import annotations

import json
import uuid
from pathlib import Path

import typer
from sqlalchemy import select

from api.db import SessionLocal
from api.models import Ingredient, IngredientCategory, TargetProfile

app = typer.Typer()

_INGREDIENTS_FILE = Path(__file__).parent / "seed-ingredients.json"
_PROFILE_NAMESPACE = uuid.UUID("6f2790bd-e765-4066-b9cf-38510df50c53")
_INGREDIENT_NAMESPACE = uuid.UUID("899fcfe0-50c6-48f3-9e55-b98b19a28f2b")

CATEGORIES = [
    ("dairy", "Dairy"),
    ("egg", "Egg"),
    ("sweetener", "Sweetener"),
    ("stabilizer", "Stabilizer"),
    ("emulsifier", "Emulsifier"),
    ("alcohol", "Alcohol"),
    ("fat_oil", "Fat & Oil"),
    ("fruit", "Fruit"),
    ("chocolate", "Chocolate"),
    ("flavoring", "Flavoring"),
    ("nuts-seeds", "Nuts & Seeds"),
    ("other", "Other"),
]

TARGET_PROFILES = [
    {
        "id": uuid.uuid5(_PROFILE_NAMESPACE, "Ice Cream"),
        "name": "Ice Cream",
        "serving_temp_min": -14.0,
        "serving_temp_max": -12.0,
        "sweetness_min": 16.0,
        "sweetness_max": 22.0,
        "total_solids_min": 36.0,
        "total_solids_max": 42.0,
        "total_fat_min": 10.0,
        "total_fat_max": 16.0,
        "milk_fat_max": 16.0,
        "sugar_min": 14.0,
        "sugar_max": 18.0,
        "msnf_max": 12.0,
        "stabilizer_min": 0.2,
        "stabilizer_max": 0.5,
        "emulsifier_min": 0.1,
        "emulsifier_max": 0.3,
    },
    {
        "id": uuid.uuid5(_PROFILE_NAMESPACE, "Gelato"),
        "name": "Gelato",
        "serving_temp_min": -12.0,
        "serving_temp_max": -10.0,
        "sweetness_min": 16.0,
        "sweetness_max": 22.0,
        "total_solids_min": 32.0,
        "total_solids_max": 40.0,
        "total_fat_min": 4.0,
        "total_fat_max": 9.0,
        "milk_fat_max": 9.0,
        "sugar_min": 16.0,
        "sugar_max": 22.0,
        "msnf_max": 12.0,
        "stabilizer_min": 0.2,
        "stabilizer_max": 0.5,
        "emulsifier_min": 0.0,
        "emulsifier_max": 0.2,
    },
    {
        "id": uuid.uuid5(_PROFILE_NAMESPACE, "Sorbet"),
        "name": "Sorbet",
        "serving_temp_min": -13.0,
        "serving_temp_max": -11.0,
        "sweetness_min": 20.0,
        "sweetness_max": 30.0,
        "total_solids_min": 28.0,
        "total_solids_max": 35.0,
        "total_fat_min": 0.0,
        "total_fat_max": 3.0,
        "milk_fat_max": 0.0,
        "sugar_min": 25.0,
        "sugar_max": 35.0,
        "msnf_max": 0.0,
        "stabilizer_min": 0.3,
        "stabilizer_max": 0.7,
        "emulsifier_min": 0.0,
        "emulsifier_max": 0.0,
    },
    {
        "id": uuid.uuid5(_PROFILE_NAMESPACE, "Sherbet"),
        "name": "Sherbet",
        "serving_temp_min": -14.0,
        "serving_temp_max": -12.0,
        "sweetness_min": 20.0,
        "sweetness_max": 28.0,
        "total_solids_min": 30.0,
        "total_solids_max": 38.0,
        "total_fat_min": 1.0,
        "total_fat_max": 4.0,
        "milk_fat_max": 4.0,
        "sugar_min": 22.0,
        "sugar_max": 30.0,
        "msnf_max": 5.0,
        "stabilizer_min": 0.2,
        "stabilizer_max": 0.5,
        "emulsifier_min": 0.0,
        "emulsifier_max": 0.2,
    },
    {
        "id": uuid.uuid5(_PROFILE_NAMESPACE, "Ice Cream - Low Fat Low Sugar"),
        "name": "Ice Cream - Low Fat Low Sugar",
        "serving_temp_min": -14.0,
        "serving_temp_max": -12.0,
        "sweetness_min": 12.0,
        "sweetness_max": 18.0,
        "total_solids_min": 20.0,
        "total_solids_max": 28.0,
        "total_fat_min": 1.0,
        "total_fat_max": 3.0,
        "milk_fat_max": 3.0,
        "sugar_min": 2.0,
        "sugar_max": 4.0,
        "msnf_max": 8.0,
        "stabilizer_min": 0.2,
        "stabilizer_max": 0.5,
        "emulsifier_min": 0.1,
        "emulsifier_max": 0.3,
    },
    {
        "id": uuid.uuid5(_PROFILE_NAMESPACE, "Ice Cream - Low Fat High Sugar"),
        "name": "Ice Cream - Low Fat High Sugar",
        "serving_temp_min": -14.0,
        "serving_temp_max": -12.0,
        "sweetness_min": 16.0,
        "sweetness_max": 24.0,
        "total_solids_min": 22.0,
        "total_solids_max": 30.0,
        "total_fat_min": 1.0,
        "total_fat_max": 3.0,
        "milk_fat_max": 3.0,
        "sugar_min": 6.0,
        "sugar_max": 8.0,
        "msnf_max": 8.0,
        "stabilizer_min": 0.2,
        "stabilizer_max": 0.5,
        "emulsifier_min": 0.1,
        "emulsifier_max": 0.3,
    },
    {
        "id": uuid.uuid5(_PROFILE_NAMESPACE, "Ice Cream - Medium Fat Low Sugar"),
        "name": "Ice Cream - Medium Fat Low Sugar",
        "serving_temp_min": -14.0,
        "serving_temp_max": -12.0,
        "sweetness_min": 12.0,
        "sweetness_max": 18.0,
        "total_solids_min": 24.0,
        "total_solids_max": 32.0,
        "total_fat_min": 4.0,
        "total_fat_max": 6.0,
        "milk_fat_max": 6.0,
        "sugar_min": 2.0,
        "sugar_max": 4.0,
        "msnf_max": 10.0,
        "stabilizer_min": 0.2,
        "stabilizer_max": 0.5,
        "emulsifier_min": 0.1,
        "emulsifier_max": 0.3,
    },
    {
        "id": uuid.uuid5(_PROFILE_NAMESPACE, "Ice Cream - Medium Fat High Sugar"),
        "name": "Ice Cream - Medium Fat High Sugar",
        "serving_temp_min": -14.0,
        "serving_temp_max": -12.0,
        "sweetness_min": 16.0,
        "sweetness_max": 24.0,
        "total_solids_min": 26.0,
        "total_solids_max": 34.0,
        "total_fat_min": 4.0,
        "total_fat_max": 6.0,
        "milk_fat_max": 6.0,
        "sugar_min": 6.0,
        "sugar_max": 8.0,
        "msnf_max": 10.0,
        "stabilizer_min": 0.2,
        "stabilizer_max": 0.5,
        "emulsifier_min": 0.1,
        "emulsifier_max": 0.3,
    },
    {
        "id": uuid.uuid5(_PROFILE_NAMESPACE, "Ice Cream - High Fat Low Sugar"),
        "name": "Ice Cream - High Fat Low Sugar",
        "serving_temp_min": -14.0,
        "serving_temp_max": -12.0,
        "sweetness_min": 12.0,
        "sweetness_max": 18.0,
        "total_solids_min": 28.0,
        "total_solids_max": 36.0,
        "total_fat_min": 6.0,
        "total_fat_max": 8.0,
        "milk_fat_max": 8.0,
        "sugar_min": 2.0,
        "sugar_max": 4.0,
        "msnf_max": 10.0,
        "stabilizer_min": 0.2,
        "stabilizer_max": 0.5,
        "emulsifier_min": 0.1,
        "emulsifier_max": 0.3,
    },
    {
        "id": uuid.uuid5(_PROFILE_NAMESPACE, "Ice Cream - High Fat High Sugar"),
        "name": "Ice Cream - High Fat High Sugar",
        "serving_temp_min": -14.0,
        "serving_temp_max": -12.0,
        "sweetness_min": 16.0,
        "sweetness_max": 24.0,
        "total_solids_min": 30.0,
        "total_solids_max": 38.0,
        "total_fat_min": 6.0,
        "total_fat_max": 8.0,
        "milk_fat_max": 8.0,
        "sugar_min": 6.0,
        "sugar_max": 8.0,
        "msnf_max": 10.0,
        "stabilizer_min": 0.2,
        "stabilizer_max": 0.5,
        "emulsifier_min": 0.1,
        "emulsifier_max": 0.3,
    },
]


# Common ice cream ingredients with composition data
# Loaded from seed_ingredients.json — add new entries there, not here.
def _load_ingredients() -> list[dict]:
    return json.loads(_INGREDIENTS_FILE.read_text(encoding="utf-8"))


@app.command("all")
def seed_all() -> None:
    """Seed categories, target profiles, and common ingredients."""
    db = SessionLocal()
    try:
        _seed_categories(db)
        _seed_profiles(db)
        _seed_ingredients(db)
        db.commit()
        typer.echo("Seed complete.")
    finally:
        db.close()


@app.command("categories")
def seed_categories_cmd() -> None:
    """Seed ingredient categories only."""
    db = SessionLocal()
    try:
        _seed_categories(db)
        db.commit()
        typer.echo("Categories seeded.")
    finally:
        db.close()


def _seed_categories(db) -> None:
    for slug, name in CATEGORIES:
        exists = db.scalar(
            select(IngredientCategory).where(IngredientCategory.slug == slug)
        )
        if not exists:
            db.add(IngredientCategory(name=name, slug=slug))
            typer.echo(f"  + category: {name}")


def _seed_profiles(db) -> None:
    for profile_data in TARGET_PROFILES:
        exists = db.scalar(
            select(TargetProfile).where(TargetProfile.name == profile_data["name"])
        )
        if not exists:
            db.add(TargetProfile(**profile_data))
            typer.echo(f"  + profile: {profile_data['name']}")


def _seed_ingredients(db) -> None:
    # Build slug → id map
    categories = db.scalars(select(IngredientCategory)).all()
    slug_to_id = {c.slug: c.id for c in categories}

    for ing_data in _load_ingredients():
        source_id = ing_data["name"]
        exists = db.scalar(
            select(Ingredient).where(
                Ingredient.source == "seed",
                Ingredient.source_id == source_id,
            )
        )
        if exists:
            continue

        data = dict(ing_data)
        cat_slug = data.pop("category_slug", None)
        if cat_slug and cat_slug in slug_to_id:
            data["category_id"] = slug_to_id[cat_slug]
        data["source"] = "seed"
        data["source_id"] = source_id
        # Generate deterministic UUID based on source + source_id pattern
        data["id"] = uuid.uuid5(_INGREDIENT_NAMESPACE, f"seed:{source_id}")

        db.add(Ingredient(**data))
        typer.echo(f"  + ingredient: {data['name']}")
