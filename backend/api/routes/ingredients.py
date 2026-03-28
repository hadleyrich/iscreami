"""Ingredient CRUD routes."""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import case, func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload, selectinload

from api.db import NOT_FOUND_RESPONSE, DbSession
from api.models import Ingredient, IngredientAlias, IngredientCategory
from api.schemas import (
    IngredientCategoryOut,
    IngredientCreate,
    IngredientOut,
    IngredientUpdate,
    PaginatedIngredients,
)

router = APIRouter(prefix="/ingredients", tags=["ingredients"])


@router.get("", response_model=PaginatedIngredients)
def list_ingredients(
    db: DbSession,
    q: Annotated[str | None, Query(max_length=200)] = None,
    category_id: int | None = None,
    source: str | None = None,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
):
    stmt = select(Ingredient).options(
        joinedload(Ingredient.category),
        selectinload(Ingredient.aliases),
    )

    if q:
        alias_subq = select(IngredientAlias.ingredient_id).where(
            IngredientAlias.alias.ilike(f"%{q}%")
        )
        stmt = stmt.where(
            or_(Ingredient.name.ilike(f"%{q}%"), Ingredient.id.in_(alias_subq))
        )
        # Relevance scoring: exact prefix > word boundary > substring match
        # Then sort by name length (shorter is better) and alphabetically
        relevance_score = case(
            (Ingredient.name.ilike(f"{q}%"), 3),  # Starts with query
            (Ingredient.name.ilike(f"% {q}%"), 2),  # Word boundary
            else_=1,  # Substring match
        )
        stmt = stmt.order_by(
            relevance_score.desc(),
            func.length(Ingredient.name).asc(),
            Ingredient.name,
        )
    else:
        stmt = stmt.order_by(Ingredient.name)

    if category_id is not None:
        stmt = stmt.where(Ingredient.category_id == category_id)
    if source is not None:
        stmt = stmt.where(Ingredient.source == source)

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = db.scalar(count_stmt) or 0

    stmt = stmt.offset(offset).limit(limit)
    items = list(db.scalars(stmt).unique().all())

    return PaginatedIngredients(total=total, items=items)  # type: ignore[arg-type]


@router.get(
    "/{ingredient_id}", response_model=IngredientOut, responses=NOT_FOUND_RESPONSE
)
def get_ingredient(ingredient_id: uuid.UUID, db: DbSession):
    ingredient = db.get(
        Ingredient,
        ingredient_id,
        options=[joinedload(Ingredient.category), selectinload(Ingredient.aliases)],
    )
    if not ingredient:
        raise HTTPException(404, "Ingredient not found")
    return ingredient


@router.post("", response_model=IngredientOut, status_code=201)
def create_ingredient(data: IngredientCreate, db: DbSession):
    payload = data.model_dump()
    alias_names: list[str] = payload.pop("aliases", [])
    ingredient = Ingredient(**payload)
    ingredient.aliases = [IngredientAlias(alias=a) for a in alias_names]
    db.add(ingredient)
    db.commit()
    db.refresh(ingredient, attribute_names=["category", "aliases"])
    return ingredient


@router.put(
    "/{ingredient_id}", response_model=IngredientOut, responses=NOT_FOUND_RESPONSE
)
def update_ingredient(ingredient_id: uuid.UUID, data: IngredientUpdate, db: DbSession):
    ingredient = db.get(
        Ingredient,
        ingredient_id,
        options=[joinedload(Ingredient.category), selectinload(Ingredient.aliases)],
    )
    if not ingredient:
        raise HTTPException(404, "Ingredient not found")

    payload = data.model_dump(exclude_unset=True)
    alias_names: list[str] | None = payload.pop("aliases", None)

    for key, value in payload.items():
        setattr(ingredient, key, value)

    if alias_names is not None:
        ingredient.aliases = [IngredientAlias(alias=a) for a in alias_names]

    db.commit()
    db.refresh(ingredient, attribute_names=["category", "aliases"])
    return ingredient


@router.delete("/{ingredient_id}", status_code=204, responses=NOT_FOUND_RESPONSE)
def delete_ingredient(ingredient_id: uuid.UUID, db: DbSession):
    ingredient = db.get(Ingredient, ingredient_id)
    if not ingredient:
        raise HTTPException(404, "Ingredient not found")
    db.delete(ingredient)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            409, "Ingredient is used in one or more recipes and cannot be deleted"
        ) from None


# --- Categories ---

cat_router = APIRouter(prefix="/ingredient-categories", tags=["ingredients"])


@cat_router.get("", response_model=list[IngredientCategoryOut])
def list_categories(db: DbSession):
    return db.scalars(
        select(IngredientCategory).order_by(IngredientCategory.name)
    ).all()
