"""PAC (Potere AntiCongelante) calculator.

PAC measures the freezing point depression power of solutes relative to sucrose.
Factor = molecular_weight_of_sucrose / molecular_weight_of_solute × 100.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from api.models import Ingredient

# PAC factors (sucrose MW 342.3 / solute MW × 100)
PAC_FACTORS: dict[str, float] = {
    "sucrose": 100.0,
    "glucose": 190.0,
    "fructose": 190.0,
    "lactose": 100.0,
    "maltose": 100.0,
    "galactose": 190.0,
}

# Salt: NaCl MW 58.44 → factor 585
NACL_PAC_FACTOR = 585.0
# Sodium → NaCl conversion factor (NaCl MW / Na AW ≈ 58.44/22.99)
SODIUM_TO_NACL = 2.58
# mg → g conversion
MG_TO_G = 0.001

# Ethanol MW 46.07 → factor 743
ETHANOL_PAC_FACTOR = 743.0


def ingredient_pac(ingredient: Ingredient) -> float:
    """Calculate PAC per 100 g of ingredient.

    If the ingredient has a manual override, use that.
    If sugar breakdown fields are present, use advanced mode.
    Otherwise fall back to total_sugar_pct treated as sucrose.
    """
    if ingredient.pac_override is not None:
        return float(ingredient.pac_override)

    pac = 0.0

    # Check if we have any sugar breakdown data
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
        # Advanced mode: use individual sugar PAC factors
        for sugar_name, pct in sugar_fields.items():
            if pct is not None and pct > 0:
                pac += float(pct) * PAC_FACTORS[sugar_name] / 100.0
    elif ingredient.total_sugar_pct is not None:
        # Simple mode: treat all sugar as sucrose
        pac += float(ingredient.total_sugar_pct) * PAC_FACTORS["sucrose"] / 100.0

    # Sodium contribution (converted to NaCl equivalent)
    if ingredient.sodium_mg is not None and ingredient.sodium_mg > 0:
        sodium_g_per_100g = float(ingredient.sodium_mg) * MG_TO_G
        # sodium_g × NaCl/Na ratio × NaCl PAC factor / 100
        pac += sodium_g_per_100g * SODIUM_TO_NACL * NACL_PAC_FACTOR / 100.0

    # Alcohol contribution
    if ingredient.alcohol_pct is not None and ingredient.alcohol_pct > 0:
        pac += float(ingredient.alcohol_pct) * ETHANOL_PAC_FACTOR / 100.0

    return pac


def recipe_pac(
    items: list[tuple[Ingredient, float]],
) -> tuple[float, float | None]:
    """Calculate recipe-level PAC in both conventions.

    Args:
        items: List of (ingredient, weight_grams) pairs.

    Returns:
        (pac_mix, pac_water):
            pac_mix  — PAC per 100 g of total mix
            pac_water — PAC per 100 g of free water (None if no free water)
    """
    total_weight = sum(w for _, w in items)
    if total_weight == 0:
        return 0.0, None

    # Sum of absolute PAC contributions (grams of sucrose-equivalent FPD)
    pac_sum = 0.0
    free_water_g = 0.0

    for ingredient, weight_g in items:
        pac_per_100 = ingredient_pac(ingredient)
        pac_sum += weight_g * pac_per_100 / 100.0

        water_pct = float(ingredient.water_pct) if ingredient.water_pct else 0.0
        free_water_g += weight_g * water_pct / 100.0

    pac_mix = pac_sum / total_weight * 100.0
    pac_water = pac_sum / free_water_g * 100.0 if free_water_g > 0 else None

    return pac_mix, pac_water
