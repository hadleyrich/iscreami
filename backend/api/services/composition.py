"""Composition-level calculations for individual ingredients."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from api.models import Ingredient


def ingredient_total_solids_pct(ingredient: Ingredient) -> float:
    """Calculate total solids as percentage of 100g ingredient.

    Total solids = 100% - water% - alcohol%
    Alcohol is not a solid and is tracked separately.
    """
    water = ingredient.water_pct or 0.0
    alcohol = ingredient.alcohol_pct or 0.0
    return max(0.0, 100.0 - water - alcohol)
