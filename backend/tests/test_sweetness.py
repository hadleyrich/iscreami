"""Tests for POD (Potere Dolcificante / sweetness) calculations."""

from __future__ import annotations

import pytest

from tests.conftest import make_ingredient


class TestIngredientPOD:
    def test_pure_sucrose(self):
        from api.services.sweetness import ingredient_pod

        ing = make_ingredient(sucrose_pct=99.8)
        # 99.8 * 1.0 = 99.8
        assert abs(ingredient_pod(ing) - 99.8) < 0.01

    def test_pure_fructose(self):
        from api.services.sweetness import ingredient_pod

        ing = make_ingredient(fructose_pct=50.0)
        # 50.0 * 1.7 = 85.0
        assert abs(ingredient_pod(ing) - 85.0) < 0.01

    def test_pure_glucose(self):
        from api.services.sweetness import ingredient_pod

        ing = make_ingredient(glucose_pct=100.0)
        # 100 * 0.75 = 75.0
        assert abs(ingredient_pod(ing) - 75.0) < 0.01

    def test_lactose_low_sweetness(self):
        from api.services.sweetness import ingredient_pod

        ing = make_ingredient(lactose_pct=4.81)
        # 4.81 * 0.16 = 0.7696
        assert abs(ingredient_pod(ing) - 0.77) < 0.01

    def test_pure_maltose(self):
        from api.services.sweetness import ingredient_pod

        ing = make_ingredient(maltose_pct=100.0)
        # 100 * 0.33 = 33.0
        assert abs(ingredient_pod(ing) - 33.0) < 0.01

    def test_pure_galactose(self):
        from api.services.sweetness import ingredient_pod

        ing = make_ingredient(galactose_pct=100.0)
        # 100 * 0.32 = 32.0
        assert abs(ingredient_pod(ing) - 32.0) < 0.01

    def test_pod_override_takes_precedence(self):
        from api.services.sweetness import ingredient_pod

        ing = make_ingredient(pod_override=25.0, sucrose_pct=99.0)
        assert ingredient_pod(ing) == pytest.approx(25.0)

    def test_pod_override_zero(self):
        from api.services.sweetness import ingredient_pod

        ing = make_ingredient(pod_override=0.0, sucrose_pct=99.0)
        assert ingredient_pod(ing) == pytest.approx(0.0)

    def test_simple_mode_fallback_total_sugar(self):
        """When no sugar breakdown, total_sugar_pct is treated as sucrose."""
        from api.services.sweetness import ingredient_pod

        ing = make_ingredient(total_sugar_pct=80.0)
        # 80.0 * 1.0 = 80.0
        assert abs(ingredient_pod(ing) - 80.0) < 0.01

    def test_no_sugars_returns_zero(self):
        from api.services.sweetness import ingredient_pod

        ing = make_ingredient()  # all None
        assert ingredient_pod(ing) == pytest.approx(0.0)

    def test_combined_sugars(self):
        from api.services.sweetness import ingredient_pod

        ing = make_ingredient(sucrose_pct=50.0, fructose_pct=20.0, glucose_pct=10.0)
        # 50*1.0 + 20*1.7 + 10*0.75 = 50 + 34 + 7.5 = 91.5
        assert abs(ingredient_pod(ing) - 91.5) < 0.01

    def test_zero_pct_sugar_not_counted(self):
        """Sugar fields with value 0 should not contribute to POD."""
        from api.services.sweetness import ingredient_pod

        ing = make_ingredient(sucrose_pct=50.0, fructose_pct=0.0)
        assert abs(ingredient_pod(ing) - 50.0) < 0.01


class TestRecipePOD:
    def test_single_ingredient(self):
        from api.services.sweetness import recipe_pod

        ing = make_ingredient(sucrose_pct=100.0)
        # 100g of 100% sucrose → pod = 100.0
        assert recipe_pod([(ing, 100.0)]) == pytest.approx(100.0)  # type: ignore[arg-type]

    def test_two_ingredients_weighted(self):
        from api.services.sweetness import recipe_pod

        a = make_ingredient(sucrose_pct=100.0)
        b = make_ingredient(fructose_pct=100.0)
        # 500g * 100*1.0/100 + 500g * 100*1.7/100 = 500 + 850 = 1350 pod_sum
        # / 1000 * 100 = 135.0 → actually recipe_pod: pod_sum / total * 100
        # a: 500 * 100/100 = 500 pod units; b: 500 * 170/100 = 850 pod units
        # pod_sum = 500 + 850 = 1350; total = 1000
        # recipe_pod = 1350 / 1000 * 100 = 135.0
        result = recipe_pod([(a, 500.0), (b, 500.0)])  # type: ignore[arg-type]
        assert result == pytest.approx(135.0)

    def test_empty_items_returns_zero(self):
        from api.services.sweetness import recipe_pod

        assert recipe_pod([]) == pytest.approx(0.0)

    def test_non_sweet_ingredient_zero_contribution(self):
        from api.services.sweetness import recipe_pod

        cream = make_ingredient(name="Cream", total_fat_pct=35.0)
        assert recipe_pod([(cream, 100.0)]) == pytest.approx(0.0)  # type: ignore[arg-type]

    def test_dilution_effect(self):
        """Adding water lowers POD per 100g of mix."""
        from api.services.sweetness import recipe_pod

        sugar = make_ingredient(sucrose_pct=100.0)
        water = make_ingredient(water_pct=100.0)
        pod_pure = recipe_pod([(sugar, 100.0)])  # type: ignore[arg-type]
        pod_diluted = recipe_pod([(sugar, 100.0), (water, 400.0)])  # type: ignore[arg-type]
        assert pod_diluted < pod_pure
        assert pod_diluted == pytest.approx(20.0)
