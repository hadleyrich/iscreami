"""Export/import service for recipes."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import select

from api.models import Ingredient, Recipe, RecipeIngredient, TargetProfile
from api.schemas import RecipeExportMetrics, RecipeExportOut
from api.services.calculator import (
    calculate_composition,
    calculate_freezing,
    calculate_pac,
    calculate_sweetness,
)

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


def build_export_single(
    recipe: Recipe,
) -> RecipeExportOut:
    """Export a single recipe with calculated metrics.

    Returns a Pydantic model for validation and serialization.
    """
    # Prepare ingredient list for calculator
    items: list[tuple[Ingredient, float]] = [
        (ing.ingredient, float(ing.weight_grams))
        for ing in sorted(recipe.ingredients, key=lambda x: x.sort_order)
    ]

    # Calculate metrics
    composition = calculate_composition(items)
    pac = calculate_pac(items)
    freezing = calculate_freezing(pac, composition)
    sweetness = calculate_sweetness(items)

    # Build free water in grams
    total_weight_g = sum(w for _, w in items)
    free_water_g = (composition.water_pct * total_weight_g) / 100.0
    sugar_solids_g = (composition.total_sugar_pct * total_weight_g) / 100.0

    # Build calculated metrics model
    calculated_metrics = RecipeExportMetrics(
        pac_mix=pac.pac_mix,
        pac_water=pac.pac_water,
        pod=sweetness.pod,
        freezing_point_c=freezing.freezing_point_c,
        free_water_g=free_water_g,
        sugar_solids_g=sugar_solids_g,
    )

    # Build export model (model_validate uses from_attributes=True for ORM conversion)
    return RecipeExportOut.model_validate(
        {
            "id": str(recipe.id),
            "name": recipe.name,
            "description": recipe.description,
            "recipe_type": recipe.recipe_type,
            "created_at": recipe.created_at.isoformat(),
            "updated_at": recipe.updated_at.isoformat(),
            "total_weight_grams": float(total_weight_g),
            "target_profile": recipe.target_profile,
            "ingredients": sorted(recipe.ingredients, key=lambda x: x.sort_order),
            "calculated_metrics": calculated_metrics,
        }
    )


def build_export_batch(
    recipes: list[Recipe],
) -> list[RecipeExportOut]:
    """Export multiple recipes. Returns array of export models."""
    return [build_export_single(recipe) for recipe in recipes]


def normalize_import_data(raw_json: dict | list) -> list[dict]:
    """Normalize import data: if object, wrap in array; if array, return as-is."""
    if isinstance(raw_json, list):
        return raw_json
    elif isinstance(raw_json, dict):
        return [raw_json]
    else:
        raise ValueError("Import data must be object or array")


def _validate_recipe(recipe_data: dict, idx: int, db_session: Session) -> list[str]:
    """Validate a single recipe. Returns list of error messages."""
    errors: list[str] = []
    recipe_prefix = f"Recipe {idx + 1}"

    # Check required fields
    if "name" not in recipe_data or not recipe_data["name"]:
        errors.append(f"{recipe_prefix}: name is required")

    # Check ingredients
    ingredients = recipe_data.get("ingredients", [])
    if not isinstance(ingredients, list):
        errors.append(f"{recipe_prefix}: ingredients must be an array")
        return errors

    for ing_idx, ing in enumerate(ingredients):
        ing_errors = _validate_ingredient(ing, recipe_prefix, ing_idx, db_session)
        errors.extend(ing_errors)

    return errors


def _validate_ingredient(
    ing: dict,
    recipe_prefix: str,
    ing_idx: int,
    db_session: Session,
) -> list[str]:
    """Validate a single ingredient. Returns list of error messages."""
    errors: list[str] = []
    ing_prefix = f"{recipe_prefix} ingredient {ing_idx + 1}"

    if "ingredient_id" not in ing:
        errors.append(f"{ing_prefix}: ingredient_id is required")
        return errors

    ingredient_id_str = ing["ingredient_id"]
    ingredient_id: uuid.UUID | None = None
    try:
        ingredient_id = uuid.UUID(ingredient_id_str)
    except (ValueError, TypeError):
        ingredient_id = None

    ingredient = _resolve_import_ingredient(ing, db_session)
    if ingredient is None:
        if ingredient_id is None:
            errors.append(f"{ing_prefix}: invalid UUID format")
            return errors
        errors.append(f"{ing_prefix}: ingredient not found (UUID: {ingredient_id_str})")

    if "weight_grams" not in ing:
        errors.append(f"{ing_prefix}: weight_grams is required")
    elif not isinstance(ing["weight_grams"], (int, float)) or ing["weight_grams"] <= 0:
        errors.append(f"{ing_prefix}: weight_grams must be positive number")

    return errors


def _resolve_import_ingredient(
    ing: dict,
    db_session: Session,
) -> Ingredient | None:
    """Resolve imported ingredient by UUID, then by source/source_id, then by name."""
    ingredient_id_str = ing.get("ingredient_id")
    if isinstance(ingredient_id_str, str):
        try:
            ingredient_id = uuid.UUID(ingredient_id_str)
            by_id = db_session.scalars(
                select(Ingredient).where(Ingredient.id == ingredient_id)
            ).first()
            if by_id is not None:
                return by_id
        except (ValueError, TypeError):
            pass

    ingredient_data = ing.get("ingredient")
    if not isinstance(ingredient_data, dict):
        return None

    source = ingredient_data.get("source")
    source_id = ingredient_data.get("source_id")
    if source and source_id:
        by_source = db_session.scalars(
            select(Ingredient).where(
                Ingredient.source == source,
                Ingredient.source_id == source_id,
            )
        ).first()
        if by_source is not None:
            return by_source

    name = ingredient_data.get("name")
    if isinstance(name, str) and name.strip():
        by_name = db_session.scalars(
            select(Ingredient).where(Ingredient.name == name.strip())
        ).first()
        if by_name is not None:
            return by_name

    return None


def validate_import_data(
    recipes: list[dict],
    db_session: Session,
) -> list[str]:
    """Validate import data. Returns list of error messages (empty if valid)."""
    errors: list[str] = []

    if not recipes:
        errors.append("Import data must contain at least one recipe")
        return errors

    for idx, recipe_data in enumerate(recipes):
        recipe_errors = _validate_recipe(recipe_data, idx, db_session)
        errors.extend(recipe_errors)

    return errors


def resolve_or_create_target_profile(
    profile_data: dict | None,
    db_session: Session,
) -> TargetProfile | None:
    """Match or create target profile by name. Returns None if no profile provided."""
    if not profile_data:
        return None

    profile_name = profile_data.get("name")
    if not profile_name:
        return None

    # Try to find existing profile by name
    stmt = select(TargetProfile).where(TargetProfile.name == profile_name)
    existing = db_session.scalars(stmt).first()
    if existing:
        return existing

    # Create new profile from data
    profile = TargetProfile(
        name=profile_name,
        serving_temp_min=profile_data.get("serving_temp_min"),
        serving_temp_max=profile_data.get("serving_temp_max"),
        sweetness_min=profile_data.get("sweetness_min"),
        sweetness_max=profile_data.get("sweetness_max"),
        total_solids_min=profile_data.get("total_solids_min"),
        total_solids_max=profile_data.get("total_solids_max"),
        total_fat_min=profile_data.get("total_fat_min"),
        total_fat_max=profile_data.get("total_fat_max"),
        milk_fat_min=profile_data.get("milk_fat_min"),
        milk_fat_max=profile_data.get("milk_fat_max"),
        sugar_min=profile_data.get("sugar_min"),
        sugar_max=profile_data.get("sugar_max"),
        alcohol_min=profile_data.get("alcohol_min"),
        alcohol_max=profile_data.get("alcohol_max"),
        msnf_min=profile_data.get("msnf_min"),
        msnf_max=profile_data.get("msnf_max"),
        stabilizer_min=profile_data.get("stabilizer_min"),
        stabilizer_max=profile_data.get("stabilizer_max"),
        emulsifier_min=profile_data.get("emulsifier_min"),
        emulsifier_max=profile_data.get("emulsifier_max"),
    )
    db_session.add(profile)
    db_session.flush()
    return profile


def create_recipes_from_import(
    recipes_data: list[dict],
    db_session: Session,
) -> list[Recipe]:
    """Import recipes from normalized data. Resolves/creates profiles and ingredients."""
    created_recipes: list[Recipe] = []

    for recipe_data in recipes_data:
        # Resolve target profile
        target_profile = None
        profile_data = recipe_data.get("target_profile")
        if profile_data:
            target_profile = resolve_or_create_target_profile(profile_data, db_session)

        # Create recipe
        recipe = Recipe(
            name=recipe_data["name"],
            description=recipe_data.get("description"),
            recipe_type=recipe_data.get("recipe_type"),
            target_profile_id=target_profile.id if target_profile else None,
        )
        db_session.add(recipe)
        db_session.flush()

        # Add ingredients
        for ing_data in recipe_data.get("ingredients", []):
            ingredient = _resolve_import_ingredient(ing_data, db_session)
            if ingredient is None:
                ingredient_id_str = ing_data.get("ingredient_id")
                raise ValueError(
                    f"ingredient not found during import (UUID: {ingredient_id_str})"
                )

            weight_grams = float(ing_data["weight_grams"])
            sort_order = ing_data.get("sort_order", 0)

            ri = RecipeIngredient(
                recipe_id=recipe.id,
                ingredient_id=ingredient.id,
                weight_grams=weight_grams,
                sort_order=sort_order,
            )
            db_session.add(ri)

        db_session.flush()
        created_recipes.append(recipe)

    return created_recipes
