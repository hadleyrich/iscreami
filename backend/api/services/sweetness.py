"""Sweetness / POD (Potere Dolcificante) calculator.

POD expresses relative sweetness compared to sucrose (= 1.0).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from api.models import Ingredient

# POD factors (relative to sucrose = 1.0)
POD_FACTORS: dict[str, float] = {
    "sucrose": 1.0,
    "glucose": 0.75,
    "fructose": 1.7,
    "lactose": 0.16,
    "maltose": 0.33,
    "galactose": 0.32,
}


def ingredient_pod(ingredient: Ingredient) -> float:
    """Calculate POD per 100 g of ingredient.

    If override is set, use that.
    If sugar breakdown available, use individual POD factors.
    Otherwise treat total_sugar_pct as sucrose.
    """
    if ingredient.pod_override is not None:
        return float(ingredient.pod_override)

    pod = 0.0

    sugar_fields = {
        "sucrose": ingredient.sucrose_pct,
        "glucose": ingredient.glucose_pct,
        "fructose": ingredient.fructose_pct,
        "lactose": ingredient.lactose_pct,
        "maltose": ingredient.maltose_pct,
        "galactose": ingredient.galactose_pct,
    }

    has_breakdown = any(v is not None for v in sugar_fields.values())

    if has_breakdown:
        for sugar_name, pct in sugar_fields.items():
            if pct is not None and pct > 0:
                pod += float(pct) * POD_FACTORS[sugar_name]
    elif ingredient.total_sugar_pct is not None:
        pod = float(ingredient.total_sugar_pct) * POD_FACTORS["sucrose"]

    return pod


def recipe_pod(
    items: list[tuple[Ingredient, float]],
) -> float:
    """Calculate recipe-level POD (% relative sweetness).

    Weighted by ingredient weight, normalized to total mix weight.
    """
    total_weight = sum(w for _, w in items)
    if total_weight == 0:
        return 0.0

    pod_sum = 0.0
    for ingredient, weight_g in items:
        pod_per_100 = ingredient_pod(ingredient)
        pod_sum += weight_g * pod_per_100 / 100.0

    return pod_sum / total_weight * 100.0
