"""Recipe calculator — orchestrates all sub-calculators.

Takes a list of (Ingredient, weight_grams) pairs and produces the full
calculation result: composition, PAC, freezing, sweetness, nutrition,
and optional target profile comparison.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from api.schemas import (
    CalculateResponse,
    CompositionResult,
    FreezingCurvePoint,
    FreezingResult,
    MetricComparison,
    MetricStatus,
    NutritionResult,
    PACResult,
    SweetenerBreakdownItem,
    SweetnessResult,
)
from api.services.freezing import (
    fpd_at_frozen_pct,
    freezing_curve,
    freezing_point,
)
from api.services.pac import recipe_pac
from api.services.sweetness import recipe_pod

if TYPE_CHECKING:
    from api.models import Ingredient, TargetProfile


def _weighted_pct(
    items: list[tuple[Ingredient, float]],
    attr: str,
    total_weight: float,
) -> float:
    """Compute weighted percentage for a given ingredient attribute."""
    total = 0.0
    for ingredient, weight_g in items:
        val = getattr(ingredient, attr, None)
        if val is not None:
            total += float(val) * weight_g / 100.0
    return total / total_weight * 100.0 if total_weight > 0 else 0.0


def calculate_composition(
    items: list[tuple[Ingredient, float]],
) -> CompositionResult:
    total_weight = sum(w for _, w in items)

    water = _weighted_pct(items, "water_pct", total_weight)
    total_fat = _weighted_pct(items, "total_fat_pct", total_weight)
    sat_fat = _weighted_pct(items, "saturated_fat_pct", total_weight)
    trans_fat = _weighted_pct(items, "trans_fat_pct", total_weight)
    milk_fat = _weighted_pct(items, "milk_fat_pct", total_weight)
    msnf = _weighted_pct(items, "msnf_pct", total_weight)
    total_sugar = _weighted_pct(items, "total_sugar_pct", total_weight)
    protein = _weighted_pct(items, "protein_pct", total_weight)
    carbohydrate = _weighted_pct(items, "carbohydrate_pct", total_weight)
    fiber = _weighted_pct(items, "fiber_pct", total_weight)
    alcohol = _weighted_pct(items, "alcohol_pct", total_weight)
    stabilizer = _weighted_pct(items, "stabilizer_pct", total_weight)
    emulsifier = _weighted_pct(items, "emulsifier_pct", total_weight)

    return CompositionResult(
        total_weight_g=round(total_weight, 2),
        water_pct=round(water, 2),
        total_solids_pct=round(100.0 - water - alcohol, 2),
        total_fat_pct=round(total_fat, 2),
        saturated_fat_pct=round(sat_fat, 2),
        trans_fat_pct=round(trans_fat, 2),
        milk_fat_pct=round(milk_fat, 2),
        msnf_pct=round(msnf, 2),
        total_sugar_pct=round(total_sugar, 2),
        protein_pct=round(protein, 2),
        carbohydrate_pct=round(carbohydrate, 2),
        fiber_pct=round(fiber, 2),
        alcohol_pct=round(alcohol, 2),
        stabilizer_pct=round(stabilizer, 2),
        emulsifier_pct=round(emulsifier, 2),
    )


def calculate_pac(items: list[tuple[Ingredient, float]]) -> PACResult:
    pac_mix, pac_water = recipe_pac(items)
    return PACResult(
        pac_mix=round(pac_mix, 2),
        pac_water=round(pac_water, 2) if pac_water is not None else None,
    )


def calculate_freezing(
    pac_result: PACResult, composition: CompositionResult
) -> FreezingResult:
    pac_water = pac_result.pac_water
    msnf_pct = composition.msnf_pct
    water_pct = composition.water_pct

    fp = freezing_point(pac_water, msnf_pct, water_pct)
    curve = freezing_curve(pac_water, msnf_pct, water_pct)

    # Serving temperature at 75% frozen water (industry standard)
    serving_temp: float | None = None
    if pac_water is not None and pac_water > 0 and water_pct > 0:
        fpd = fpd_at_frozen_pct(75.0, pac_water, msnf_pct, water_pct)
        serving_temp = -round(fpd, 2)

    return FreezingResult(
        freezing_point_c=round(fp, 2),
        serving_temperature_c=serving_temp,
        curve=[
            FreezingCurvePoint(temperature_c=t, frozen_water_pct=f) for t, f in curve
        ],
    )


def calculate_sweetness(
    items: list[tuple[Ingredient, float]],
) -> SweetnessResult:
    pod = recipe_pod(items)

    # Build sweetener breakdown
    breakdown: list[SweetenerBreakdownItem] = []
    total_sweetener_g = 0.0

    for ingredient, weight_g in items:
        sweet_g = 0.0
        # Check for any sugars
        for field in (
            "sucrose_pct",
            "glucose_pct",
            "fructose_pct",
            "lactose_pct",
            "maltose_pct",
            "galactose_pct",
        ):
            val = getattr(ingredient, field, None)
            if val is not None and val > 0:
                sweet_g += float(val) * weight_g / 100.0

        if sweet_g <= 0 and ingredient.total_sugar_pct:
            sweet_g = float(ingredient.total_sugar_pct) * weight_g / 100.0

        if sweet_g > 0:
            breakdown.append(
                SweetenerBreakdownItem(
                    ingredient_name=ingredient.name,
                    weight_g=round(sweet_g, 2),
                    pct_of_sweeteners=0.0,  # filled below
                )
            )
            total_sweetener_g += sweet_g

    # Compute percentages
    for item in breakdown:
        if total_sweetener_g > 0:
            item.pct_of_sweeteners = round(item.weight_g / total_sweetener_g * 100.0, 1)

    return SweetnessResult(
        pod=round(pod, 2),
        sweetener_breakdown=breakdown,
    )


def calculate_nutrition(
    items: list[tuple[Ingredient, float]],
    serving_size_g: float = 66.0,
) -> NutritionResult:
    total_weight = sum(w for _, w in items)

    nutrient_fields = {
        "energy_kj": "energy_kj_per_100g",
        "total_fat_g": "total_fat_pct",
        "saturated_fat_g": "saturated_fat_pct",
        "trans_fat_g": "trans_fat_pct",
        "carbohydrate_g": "carbohydrate_pct",
        "sugars_g": "total_sugar_pct",
        "fiber_g": "fiber_pct",
        "protein_g": "protein_pct",
    }

    per_100g: dict[str, float] = {}
    for label, attr in nutrient_fields.items():
        total = 0.0
        for ingredient, weight_g in items:
            val = getattr(ingredient, attr, None)
            if val is not None:
                total += float(val) * weight_g / 100.0
        # Normalize to per 100g of mix
        if total_weight > 0:
            per_100g[label] = round(total / total_weight * 100.0, 2)
        else:
            per_100g[label] = 0.0

    # Per serving
    per_serving: dict[str, float] = {}
    for label, val in per_100g.items():
        per_serving[label] = round(val * serving_size_g / 100.0, 2)

    return NutritionResult(
        per_100g=per_100g,
        per_serving=per_serving,
        serving_size_g=serving_size_g,
    )


def compare_to_target(
    composition: CompositionResult,
    sweetness: SweetnessResult,
    freezing: FreezingResult,
    profile: TargetProfile,
) -> list[MetricComparison]:
    """Compare calculated metrics against target profile ranges."""
    checks: list[tuple[str, float, float | None, float | None]] = [
        (
            "total_solids",
            composition.total_solids_pct,
            _f(profile.total_solids_min),
            _f(profile.total_solids_max),
        ),
        (
            "total_fat",
            composition.total_fat_pct,
            _f(profile.total_fat_min),
            _f(profile.total_fat_max),
        ),
        ("milk_fat", composition.milk_fat_pct, None, _f(profile.milk_fat_max)),
        (
            "sugar",
            composition.total_sugar_pct,
            _f(profile.sugar_min),
            _f(profile.sugar_max),
        ),
        ("msnf", composition.msnf_pct, None, _f(profile.msnf_max)),
        (
            "stabilizer",
            composition.stabilizer_pct,
            _f(profile.stabilizer_min),
            _f(profile.stabilizer_max),
        ),
        (
            "emulsifier",
            composition.emulsifier_pct,
            _f(profile.emulsifier_min),
            _f(profile.emulsifier_max),
        ),
        (
            "sweetness",
            sweetness.pod,
            _f(profile.sweetness_min),
            _f(profile.sweetness_max),
        ),
        (
            "serving_temp",
            freezing.serving_temperature_c
            if freezing.serving_temperature_c is not None
            else 0.0,
            _f(profile.serving_temp_min),
            _f(profile.serving_temp_max),
        ),
    ]

    results: list[MetricComparison] = []
    for metric, value, tmin, tmax in checks:
        status = MetricStatus.in_range
        if tmin is not None and value < tmin:
            status = MetricStatus.below
        elif tmax is not None and value > tmax:
            status = MetricStatus.above
        results.append(
            MetricComparison(
                metric=metric,
                value=round(value, 2),
                target_min=tmin,
                target_max=tmax,
                status=status,
            )
        )
    return results


def _f(val: float | None) -> float | None:
    """Convert Numeric/Decimal to float safely."""
    return float(val) if val is not None else None


def calculate(
    items: list[tuple[Ingredient, float]],
    target_profile: TargetProfile | None = None,
    serving_size_g: float = 66.0,
) -> CalculateResponse:
    """Run the full calculation pipeline."""
    composition = calculate_composition(items)
    pac = calculate_pac(items)
    freezing_result = calculate_freezing(pac, composition)
    sweetness = calculate_sweetness(items)
    nutrition = calculate_nutrition(items, serving_size_g)

    target_comparison = None
    if target_profile is not None:
        target_comparison = compare_to_target(
            composition, sweetness, freezing_result, target_profile
        )

    return CalculateResponse(
        composition=composition,
        pac=pac,
        freezing=freezing_result,
        sweetness=sweetness,
        nutrition=nutrition,
        target_comparison=target_comparison,
    )
