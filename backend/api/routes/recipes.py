"""Recipe CRUD routes."""

from __future__ import annotations

import json
import uuid
from typing import TYPE_CHECKING, Annotated, cast

from fastapi import APIRouter, File, HTTPException, Query, UploadFile
from sqlalchemy import func, select
from sqlalchemy.orm import joinedload, selectinload

from api.db import NOT_FOUND_RESPONSE, DbSession
from api.models import Recipe, RecipeIngredient
from api.schemas import (
    PaginatedRecipes,
    RecipeCreate,
    RecipeExportOut,
    RecipeIngredientInput,
    RecipeOut,
    RecipeUpdate,
)
from api.services.export import (
    build_export_single,
    create_recipes_from_import,
    normalize_import_data,
    validate_import_data,
)

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

router = APIRouter(prefix="/recipes", tags=["recipes"])

_MAX_IMPORT_SIZE = 5 * 1024 * 1024  # 5 MB
_MAX_IMPORT_RECIPES = 200

# Eager-load the relationships every recipe endpoint needs. Shared so the
# query options can't drift between list/detail/export endpoints.
_RECIPE_LOAD_OPTIONS = (
    joinedload(Recipe.target_profile),
    selectinload(Recipe.ingredients).joinedload(RecipeIngredient.ingredient),
)


def _load_recipe(db, recipe_id: uuid.UUID) -> Recipe:
    stmt = select(Recipe).where(Recipe.id == recipe_id).options(*_RECIPE_LOAD_OPTIONS)
    recipe = db.scalars(stmt).unique().first()
    if not recipe:
        raise HTTPException(404, "Recipe not found")
    return recipe


def _sync_ingredients(
    db: Session,
    recipe: Recipe,
    ingredient_inputs: list[RecipeIngredientInput],
) -> None:
    """Replace recipe ingredients with the given list."""
    # Remove existing
    for ri in recipe.ingredients:
        db.delete(ri)
    db.flush()

    # Add new
    for inp in ingredient_inputs:
        db.add(
            RecipeIngredient(
                recipe_id=recipe.id,
                ingredient_id=inp.ingredient_id,
                weight_grams=inp.weight_grams,
                sort_order=inp.sort_order,
            )
        )


@router.get("", response_model=PaginatedRecipes)
def list_recipes(
    db: DbSession,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
):
    count = db.scalar(select(func.count()).select_from(Recipe)) or 0

    stmt = (
        select(Recipe)
        .options(*_RECIPE_LOAD_OPTIONS)
        .order_by(Recipe.updated_at.desc())
        .offset(offset)
        .limit(limit)
    )
    items = list(db.scalars(stmt).unique().all())
    return PaginatedRecipes(total=count, items=items)  # type: ignore[arg-type]


@router.get("/export-all", response_model=list[RecipeExportOut])
def export_all_recipes(db: DbSession):
    """Export all recipes as a JSON array with underscore keys."""
    stmt = select(Recipe).options(*_RECIPE_LOAD_OPTIONS)
    recipes = list(db.scalars(stmt).unique().all())
    return [build_export_single(recipe) for recipe in recipes]


@router.get("/{recipe_id}/export", response_model=RecipeExportOut)
def export_single_recipe(recipe_id: uuid.UUID, db: DbSession):
    """Export a single recipe as a plain JSON object with underscore keys."""
    recipe = _load_recipe(db, recipe_id)
    return build_export_single(recipe)


@router.get("/{recipe_id}", response_model=RecipeOut, responses=NOT_FOUND_RESPONSE)
def get_recipe(recipe_id: uuid.UUID, db: DbSession):
    return _load_recipe(db, recipe_id)


@router.post("", response_model=RecipeOut, status_code=201)
def create_recipe(data: RecipeCreate, db: DbSession):
    recipe = Recipe(
        name=data.name,
        description=data.description,
        recipe_type=data.recipe_type,
        target_profile_id=data.target_profile_id,
    )
    db.add(recipe)
    db.flush()

    _sync_ingredients(db, recipe, data.ingredients)

    db.commit()
    return _load_recipe(db, recipe.id)


@router.put("/{recipe_id}", response_model=RecipeOut, responses=NOT_FOUND_RESPONSE)
def update_recipe(recipe_id: uuid.UUID, data: RecipeUpdate, db: DbSession):
    recipe = _load_recipe(db, recipe_id)

    payload = data.model_dump(exclude_unset=True)
    if "ingredients" in payload:
        # model_dump includes explicitly-null ingredients, but only a real list is
        # valid here. cast() is a runtime no-op: a null value still fails inside
        # _sync_ingredients just as it did before.
        _sync_ingredients(
            db, recipe, cast(list[RecipeIngredientInput], data.ingredients)
        )
        del payload["ingredients"]
    for field, value in payload.items():
        setattr(recipe, field, value)

    db.commit()
    return _load_recipe(db, recipe.id)


@router.delete("/{recipe_id}", status_code=204, responses=NOT_FOUND_RESPONSE)
def delete_recipe(recipe_id: uuid.UUID, db: DbSession):
    recipe = db.get(Recipe, recipe_id)
    if not recipe:
        raise HTTPException(404, "Recipe not found")
    db.delete(recipe)
    db.commit()


@router.post(
    "/import",
    status_code=201,
    responses={
        400: {"description": "Invalid JSON or validation error"},
        413: {"description": "File too large"},
    },
)
async def import_recipes(
    file: Annotated[UploadFile, File(...)],
    db: DbSession,
) -> list[RecipeOut]:
    """Import recipes from a JSON file (object or array)."""
    if file.size is None:
        raise HTTPException(
            400, "File size could not be determined — send with Content-Length header"
        )
    if file.size > _MAX_IMPORT_SIZE:
        raise HTTPException(413, "File too large — maximum upload size is 5 MB")
    try:
        content = await file.read()
        raw_json = json.loads(content)
    except json.JSONDecodeError as e:
        raise HTTPException(400, f"Invalid JSON: {e!s}") from e

    # Normalize to array
    try:
        recipes_data = normalize_import_data(raw_json)
    except ValueError as e:
        raise HTTPException(400, str(e)) from e

    # Cap number of recipes to prevent resource exhaustion
    if len(recipes_data) > _MAX_IMPORT_RECIPES:
        raise HTTPException(413, f"Too many recipes — maximum is {_MAX_IMPORT_RECIPES}")

    # Validate
    errors = validate_import_data(recipes_data, db)
    if errors:
        raise HTTPException(400, "; ".join(errors)) from None

    # Create recipes
    try:
        created_recipes = create_recipes_from_import(recipes_data, db)
        db.commit()

        # Reload with full data
        result = []
        for recipe in created_recipes:
            loaded = _load_recipe(db, recipe.id)
            result.append(loaded)
        return result  # type: ignore[return-value]
    except Exception as e:
        db.rollback()
        raise HTTPException(400, f"Import failed: {e!s}") from e
