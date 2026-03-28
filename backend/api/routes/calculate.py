"""Stateless calculator endpoint."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from api.db import NOT_FOUND_RESPONSE, DbSession
from api.models import Ingredient, TargetProfile
from api.schemas import CalculateRequest, CalculateResponse
from api.services.calculator import calculate

router = APIRouter(tags=["calculator"])


@router.post(
    "/calculate", response_model=CalculateResponse, responses=NOT_FOUND_RESPONSE
)
def calculate_recipe(data: CalculateRequest, db: DbSession):
    """Calculate all metrics for a set of ingredients and weights."""
    # Load ingredients from DB
    ingredient_ids = [i.ingredient_id for i in data.ingredients]

    rows = db.scalars(select(Ingredient).where(Ingredient.id.in_(ingredient_ids))).all()
    ingredients_by_id = {ing.id: ing for ing in rows}

    for ing_id in ingredient_ids:
        if ing_id not in ingredients_by_id:
            raise HTTPException(404, f"Ingredient {ing_id} not found")

    items = [
        (ingredients_by_id[i.ingredient_id], i.weight_grams) for i in data.ingredients
    ]

    target_profile = None
    if data.target_profile_id is not None:
        target_profile = db.get(TargetProfile, data.target_profile_id)
        if not target_profile:
            raise HTTPException(
                404, f"Target profile {data.target_profile_id} not found"
            )

    return calculate(
        items=items,
        target_profile=target_profile,
        serving_size_g=data.serving_size_g,
    )
