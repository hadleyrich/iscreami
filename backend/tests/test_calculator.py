"""Tests for the calculator orchestration layer and sub-calculator functions."""

from __future__ import annotations

import pytest

from tests.conftest import make_ingredient, make_profile


def _make_composition(**kwargs):
    from api.schemas import CompositionResult

    defaults = {
        "total_weight_g": 1000.0,
        "water_pct": 60.0,
        "total_solids_pct": 40.0,
        "total_fat_pct": 10.0,
        "saturated_fat_pct": 6.0,
        "trans_fat_pct": 0.0,
        "milk_fat_pct": 10.0,
        "msnf_pct": 9.0,
        "total_sugar_pct": 15.0,
        "protein_pct": 3.0,
        "carbohydrate_pct": 20.0,
        "fiber_pct": 0.0,
        "alcohol_pct": 0.0,
        "stabilizer_pct": 0.3,
        "emulsifier_pct": 0.2,
    }
    defaults.update(kwargs)
    return CompositionResult(**defaults)


def _make_sweetness(pod=18.0):
    from api.schemas import SweetnessResult

    return SweetnessResult(pod=pod, sweetener_breakdown=[])


def _make_freezing(serving_temp: float | None = -12.0):
    from api.schemas import FreezingResult

    return FreezingResult(
        freezing_point_c=-2.5,
        serving_temperature_c=serving_temp,
        curve=[],
    )


class TestCalculatePAC:
    def test_returns_pac_result_schema(self):
        from api.schemas import PACResult
        from api.services.calculator import calculate_pac

        sugar = make_ingredient(sucrose_pct=100.0, water_pct=0.0)
        result = calculate_pac([(sugar, 100.0)])  # type: ignore[arg-type]
        assert isinstance(result, PACResult)
        assert result.pac_mix > 0

    def test_no_water_pac_water_is_none(self):
        from api.services.calculator import calculate_pac

        fat = make_ingredient(total_fat_pct=100.0)
        result = calculate_pac([(fat, 100.0)])  # type: ignore[arg-type]
        assert result.pac_water is None

    def test_values_are_rounded(self):
        from api.services.calculator import calculate_pac

        sugar = make_ingredient(sucrose_pct=99.8, water_pct=0.03)
        water = make_ingredient(water_pct=100.0)
        result = calculate_pac([(sugar, 200.0), (water, 800.0)])  # type: ignore[arg-type]
        # Values should be rounded to 2 decimal places
        assert result.pac_mix == round(result.pac_mix, 2)


class TestCalculateFreezing:
    def test_zero_pac_gives_zero_freezing_point(self):
        from api.schemas import PACResult
        from api.services.calculator import calculate_freezing

        comp = _make_composition(water_pct=60.0, total_solids_pct=40.0)
        result = calculate_freezing(PACResult(pac_mix=0.0, pac_water=0.0), comp)
        assert result.freezing_point_c == pytest.approx(0.0)
        assert result.serving_temperature_c is None

    def test_none_pac_water_gives_zero_freezing_point(self):
        from api.schemas import PACResult
        from api.services.calculator import calculate_freezing

        comp = _make_composition()
        result = calculate_freezing(PACResult(pac_mix=5.0, pac_water=None), comp)
        assert result.freezing_point_c == pytest.approx(0.0)
        assert result.serving_temperature_c is None

    def test_positive_pac_gives_negative_freezing_point(self):
        from api.schemas import PACResult
        from api.services.calculator import calculate_freezing

        comp = _make_composition(water_pct=80.0)
        result = calculate_freezing(PACResult(pac_mix=15.0, pac_water=25.0), comp)
        assert result.freezing_point_c < 0.0
        assert result.serving_temperature_c is not None
        assert result.serving_temperature_c < result.freezing_point_c

    def test_curve_is_populated(self):
        from api.schemas import PACResult
        from api.services.calculator import calculate_freezing

        comp = _make_composition(water_pct=80.0)
        result = calculate_freezing(PACResult(pac_mix=15.0, pac_water=25.0), comp)
        assert len(result.curve) > 0


class TestCalculateSweetness:
    def test_breakdown_percentages_sum_to_100(self):
        from api.services.calculator import calculate_sweetness

        a = make_ingredient(name="A", sucrose_pct=50.0)
        b = make_ingredient(name="B", sucrose_pct=50.0)
        result = calculate_sweetness([(a, 100.0), (b, 100.0)])  # type: ignore[arg-type]

        total_pct = sum(item.pct_of_sweeteners for item in result.sweetener_breakdown)
        assert total_pct == pytest.approx(100.0)

    def test_simple_mode_fallback_in_breakdown(self):
        from api.services.calculator import calculate_sweetness

        ing = make_ingredient(name="Syrup", total_sugar_pct=80.0)
        result = calculate_sweetness([(ing, 100.0)])  # type: ignore[arg-type]

        assert len(result.sweetener_breakdown) == 1
        assert result.sweetener_breakdown[0].ingredient_name == "Syrup"
        assert result.sweetener_breakdown[0].weight_g == pytest.approx(80.0)

    def test_no_sweetener_gives_empty_breakdown(self):
        from api.services.calculator import calculate_sweetness

        ing = make_ingredient(name="Cream", total_fat_pct=35.0)
        result = calculate_sweetness([(ing, 100.0)])  # type: ignore[arg-type]

        assert result.sweetener_breakdown == []
        assert result.pod == pytest.approx(0.0)

    def test_pod_value(self):
        from api.services.calculator import calculate_sweetness

        ing = make_ingredient(name="Sugar", sucrose_pct=100.0)
        result = calculate_sweetness([(ing, 100.0)])  # type: ignore[arg-type]
        assert result.pod == pytest.approx(100.0)


class TestCalculateNutrition:
    def test_per_serving_scales_from_per_100g(self):
        from api.services.calculator import calculate_nutrition

        ing = make_ingredient(energy_kj_per_100g=400.0)
        result = calculate_nutrition([(ing, 100.0)], serving_size_g=50.0)  # type: ignore[arg-type]

        assert result.per_100g["energy_kj"] == pytest.approx(400.0)
        assert result.per_serving["energy_kj"] == pytest.approx(200.0)
        assert result.serving_size_g == pytest.approx(50.0)

    def test_two_ingredients_weighted_correctly(self):
        from api.services.calculator import calculate_nutrition

        a = make_ingredient(energy_kj_per_100g=100.0)
        b = make_ingredient(energy_kj_per_100g=0.0)
        result = calculate_nutrition([(a, 200.0), (b, 800.0)])  # type: ignore[arg-type]

        assert result.per_100g["energy_kj"] == pytest.approx(20.0)

    def test_none_nutrients_excluded_from_sum(self):
        from api.services.calculator import calculate_nutrition

        a = make_ingredient(protein_pct=10.0)
        b = make_ingredient()
        result = calculate_nutrition([(a, 100.0), (b, 100.0)])  # type: ignore[arg-type]

        # 10g protein from 200g mix = 5g/100g
        assert result.per_100g["protein_g"] == pytest.approx(5.0)

    def test_all_nutrient_keys_present(self):
        from api.services.calculator import calculate_nutrition

        ing = make_ingredient()
        result = calculate_nutrition([(ing, 100.0)])  # type: ignore[arg-type]

        expected_keys = {
            "energy_kj",
            "total_fat_g",
            "saturated_fat_g",
            "trans_fat_g",
            "carbohydrate_g",
            "sugars_g",
            "fiber_g",
            "protein_g",
        }
        assert expected_keys == set(result.per_100g.keys())
        assert expected_keys == set(result.per_serving.keys())

    def test_default_serving_size_is_66g(self):
        from api.services.calculator import calculate_nutrition

        ing = make_ingredient(energy_kj_per_100g=200.0)
        result = calculate_nutrition([(ing, 100.0)])  # type: ignore[arg-type]
        assert result.serving_size_g == pytest.approx(66.0)
        assert result.per_serving["energy_kj"] == pytest.approx(132.0)


class TestCompareToTarget:
    def test_all_in_range(self):
        from api.schemas import MetricStatus
        from api.services.calculator import compare_to_target

        profile = make_profile(
            total_solids_min=35.0,
            total_solids_max=45.0,
            total_fat_min=8.0,
            total_fat_max=12.0,
        )
        results = compare_to_target(
            _make_composition(), _make_sweetness(), _make_freezing(), profile
        )  # type: ignore[arg-type]
        by_metric = {r.metric: r for r in results}
        assert by_metric["total_solids"].status == MetricStatus.in_range
        assert by_metric["total_fat"].status == MetricStatus.in_range

    def test_below_minimum(self):
        from api.schemas import MetricStatus
        from api.services.calculator import compare_to_target

        profile = make_profile(total_solids_min=50.0)
        results = compare_to_target(
            _make_composition(), _make_sweetness(), _make_freezing(), profile
        )  # type: ignore[arg-type]
        by_metric = {r.metric: r for r in results}
        assert by_metric["total_solids"].status == MetricStatus.below

    def test_above_maximum(self):
        from api.schemas import MetricStatus
        from api.services.calculator import compare_to_target

        profile = make_profile(total_fat_max=5.0)
        results = compare_to_target(
            _make_composition(), _make_sweetness(), _make_freezing(), profile
        )  # type: ignore[arg-type]
        by_metric = {r.metric: r for r in results}
        assert by_metric["total_fat"].status == MetricStatus.above

    def test_no_bounds_is_in_range(self):
        from api.schemas import MetricStatus
        from api.services.calculator import compare_to_target

        profile = make_profile()  # all None
        results = compare_to_target(
            _make_composition(), _make_sweetness(), _make_freezing(), profile
        )  # type: ignore[arg-type]
        for r in results:
            assert r.status == MetricStatus.in_range

    def test_all_nine_metrics_present(self):
        from api.services.calculator import compare_to_target

        profile = make_profile()
        results = compare_to_target(
            _make_composition(), _make_sweetness(), _make_freezing(), profile
        )  # type: ignore[arg-type]
        metrics = {r.metric for r in results}
        assert metrics == {
            "total_solids",
            "total_fat",
            "milk_fat",
            "sugar",
            "msnf",
            "stabilizer",
            "emulsifier",
            "sweetness",
            "serving_temp",
        }

    def test_serving_temp_none_treated_as_zero(self):
        from api.schemas import MetricStatus
        from api.services.calculator import compare_to_target

        profile = make_profile(serving_temp_min=-5.0, serving_temp_max=5.0)
        results = compare_to_target(
            _make_composition(),
            _make_sweetness(),
            _make_freezing(serving_temp=None),
            profile,  # type: ignore[arg-type]
        )
        by_metric = {r.metric: r for r in results}
        assert by_metric["serving_temp"].value == pytest.approx(0.0)
        assert by_metric["serving_temp"].status == MetricStatus.in_range

    def test_metric_comparison_includes_value_and_bounds(self):
        from api.services.calculator import compare_to_target

        profile = make_profile(total_fat_min=5.0, total_fat_max=15.0)
        results = compare_to_target(
            _make_composition(), _make_sweetness(), _make_freezing(), profile
        )  # type: ignore[arg-type]
        fat = next(r for r in results if r.metric == "total_fat")
        assert fat.target_min == pytest.approx(5.0)
        assert fat.target_max == pytest.approx(15.0)
        assert fat.value == pytest.approx(10.0)


class TestCalculate:
    def test_basic_calculation(self):
        from api.services.calculator import calculate

        sugar = make_ingredient(
            name="Sugar",
            sucrose_pct=99.8,
            water_pct=0.03,
            total_sugar_pct=99.8,
            carbohydrate_pct=99.98,
            energy_kj_per_100g=1619.2,
        )
        milk = make_ingredient(
            name="Whole Milk",
            water_pct=87.99,
            total_fat_pct=3.25,
            milk_fat_pct=3.25,
            msnf_pct=8.76,
            protein_pct=3.15,
            carbohydrate_pct=4.80,
            total_sugar_pct=5.05,
            lactose_pct=4.81,
            glucose_pct=0.07,
            sodium_mg=43.0,
            energy_kj_per_100g=255.2,
        )
        items = [(sugar, 150.0), (milk, 850.0)]
        result = calculate(items)  # type: ignore[arg-type]

        assert result.composition.total_weight_g == pytest.approx(1000.0)
        assert result.composition.total_solids_pct > 20
        assert result.pac.pac_mix > 10
        assert result.freezing.freezing_point_c < 0
        assert result.sweetness.pod > 10
        assert result.nutrition.per_100g["energy_kj"] > 0

    def test_with_target_profile(self):
        from api.services.calculator import calculate

        sugar = make_ingredient(
            name="Sugar", sucrose_pct=99.8, water_pct=0.03, total_sugar_pct=99.8
        )
        milk = make_ingredient(
            name="Milk",
            water_pct=87.99,
            lactose_pct=4.81,
            glucose_pct=0.07,
            sodium_mg=43.0,
        )
        profile = make_profile(total_solids_min=10.0, total_solids_max=50.0)

        result = calculate([(sugar, 150.0), (milk, 850.0)], target_profile=profile)  # type: ignore[arg-type]

        assert result.target_comparison is not None
        metrics = {c.metric for c in result.target_comparison}
        assert "total_solids" in metrics
        assert "sweetness" in metrics

    def test_no_target_profile_gives_none_comparison(self):
        from api.services.calculator import calculate

        ing = make_ingredient(name="Water", water_pct=100.0)
        result = calculate([(ing, 500.0)])  # type: ignore[arg-type]
        assert result.target_comparison is None

    def test_custom_serving_size(self):
        from api.services.calculator import calculate

        ing = make_ingredient(
            name="Sugar", sucrose_pct=100.0, energy_kj_per_100g=1600.0
        )
        result = calculate([(ing, 100.0)], serving_size_g=33.0)  # type: ignore[arg-type]
        assert result.nutrition.serving_size_g == pytest.approx(33.0)
        assert result.nutrition.per_serving["energy_kj"] == pytest.approx(528.0)
