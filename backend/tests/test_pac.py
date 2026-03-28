"""Tests for PAC (Potere AntiCongelante) calculations."""

from __future__ import annotations

import pytest

from tests.conftest import make_ingredient


class TestIngredientPAC:
    def test_pure_sucrose(self):
        from api.services.pac import ingredient_pac

        ing = make_ingredient(sucrose_pct=99.8)
        assert abs(ingredient_pac(ing) - 99.8) < 0.01

    def test_pure_dextrose(self):
        from api.services.pac import ingredient_pac

        ing = make_ingredient(glucose_pct=91.0)
        # 91.0 * 190 / 100 = 172.9
        assert abs(ingredient_pac(ing) - 172.9) < 0.01

    def test_pure_fructose(self):
        from api.services.pac import ingredient_pac

        ing = make_ingredient(fructose_pct=50.0)
        # 50.0 * 190 / 100 = 95.0
        assert abs(ingredient_pac(ing) - 95.0) < 0.01

    def test_pure_lactose(self):
        from api.services.pac import ingredient_pac

        ing = make_ingredient(lactose_pct=100.0)
        # lactose factor = 100 (same as sucrose)
        assert abs(ingredient_pac(ing) - 100.0) < 0.01

    def test_pure_maltose(self):
        from api.services.pac import ingredient_pac

        ing = make_ingredient(maltose_pct=100.0)
        # maltose factor = 100
        assert abs(ingredient_pac(ing) - 100.0) < 0.01

    def test_pure_galactose(self):
        from api.services.pac import ingredient_pac

        ing = make_ingredient(galactose_pct=100.0)
        # galactose factor = 190
        assert abs(ingredient_pac(ing) - 190.0) < 0.01

    def test_whole_milk(self):
        from api.services.pac import ingredient_pac

        ing = make_ingredient(
            name="Whole Milk (3.25%)",
            lactose_pct=4.81,
            glucose_pct=0.07,
            sodium_mg=43.0,
        )
        pac = ingredient_pac(ing)
        # lactose=4.81*100/100=4.81, glucose=0.07*190/100=0.133,
        # sodium=0.043*2.58*585/100≈0.649 → total ≈5.59
        assert 5.0 < pac < 6.0, f"Whole milk PAC should be ~5.4, got {pac}"

    def test_pac_override_takes_precedence(self):
        from api.services.pac import ingredient_pac

        ing = make_ingredient(pac_override=42.0, sucrose_pct=99.0)
        assert ingredient_pac(ing) == pytest.approx(42.0)

    def test_pac_override_zero(self):
        from api.services.pac import ingredient_pac

        ing = make_ingredient(pac_override=0.0, sucrose_pct=50.0)
        assert ingredient_pac(ing) == pytest.approx(0.0)

    def test_simple_mode_fallback_total_sugar(self):
        """When no sugar breakdown present, total_sugar_pct is treated as sucrose."""
        from api.services.pac import ingredient_pac

        ing = make_ingredient(total_sugar_pct=50.0)
        assert abs(ingredient_pac(ing) - 50.0) < 0.01

    def test_no_sugars_returns_zero(self):
        from api.services.pac import ingredient_pac

        ing = make_ingredient()  # all None
        assert ingredient_pac(ing) == pytest.approx(0.0)

    def test_sodium_contribution(self):
        from api.services.pac import ingredient_pac

        # 100 mg/100g sodium → 0.1g * 2.58 * 585 / 100 = 1.5093
        ing = make_ingredient(sodium_mg=100.0)
        pac = ingredient_pac(ing)
        assert abs(pac - 1.5093) < 0.01

    def test_ethanol(self):
        from api.services.pac import ingredient_pac

        ing = make_ingredient(alcohol_pct=40.0)
        # 40 * 743 / 100 = 297.2
        assert abs(ingredient_pac(ing) - 297.2) < 0.01

    def test_combined_sugars_and_sodium(self):
        from api.services.pac import ingredient_pac

        ing = make_ingredient(sucrose_pct=50.0, fructose_pct=20.0, sodium_mg=50.0)
        # sucrose: 50*100/100=50, fructose: 20*190/100=38, sodium: 0.05*2.58*585/100≈0.754
        expected = 50.0 + 38.0 + (0.05 * 2.58 * 585 / 100)
        assert abs(ingredient_pac(ing) - expected) < 0.01

    def test_zero_sodium_ignored(self):
        from api.services.pac import ingredient_pac

        ing = make_ingredient(sucrose_pct=50.0, sodium_mg=0.0)
        assert abs(ingredient_pac(ing) - 50.0) < 0.01

    def test_zero_alcohol_ignored(self):
        from api.services.pac import ingredient_pac

        ing = make_ingredient(sucrose_pct=50.0, alcohol_pct=0.0)
        assert abs(ingredient_pac(ing) - 50.0) < 0.01

    def test_erythritol_via_override(self):
        from api.services.pac import ingredient_pac

        ing = make_ingredient(pac_override=280.0)
        assert abs(ingredient_pac(ing) - 280.0) < 0.01


class TestRecipePAC:
    def test_two_ingredient_recipe(self):
        from api.services.pac import recipe_pac

        sugar = make_ingredient(sucrose_pct=99.8, water_pct=0.03)
        water = make_ingredient(water_pct=100.0)
        items = [(sugar, 200.0), (water, 800.0)]
        pac_mix, pac_water = recipe_pac(items)  # type: ignore[arg-type]

        # Sugar contributes 200 * 99.8/100 = 199.6 PAC units
        # pac_mix = 199.6 / 1000 * 100 = 19.96
        assert abs(pac_mix - 19.96) < 0.1

        # free water = 0.03/100*200 + 100/100*800 = 800.06
        # pac_water = 199.6 / 800.06 * 100 ≈ 24.95
        assert pac_water is not None
        assert abs(pac_water - 24.95) < 0.1

    def test_pac_water_none_when_no_water_in_mix(self):
        from api.services.pac import recipe_pac

        fat = make_ingredient(total_fat_pct=100.0)
        _, pac_water = recipe_pac([(fat, 100.0)])  # type: ignore[arg-type]
        assert pac_water is None

    def test_empty_items_returns_zero(self):
        from api.services.pac import recipe_pac

        pac_mix, pac_water = recipe_pac([])
        assert pac_mix == pytest.approx(0.0)
        assert pac_water is None

    def test_single_pure_water_ingredient(self):
        from api.services.pac import recipe_pac

        water = make_ingredient(water_pct=100.0)
        pac_mix, pac_water = recipe_pac([(water, 500.0)])  # type: ignore[arg-type]
        assert pac_mix == pytest.approx(0.0)
        # water is present but pac_sum is 0 → pac_water = 0/500 * 100 = 0.0
        assert pac_water == pytest.approx(0.0)

    def test_pac_mix_scales_with_weight(self):
        """Doubling weights should not change pac_mix (it's a concentration)."""
        from api.services.pac import recipe_pac

        sugar = make_ingredient(sucrose_pct=100.0, water_pct=0.0)
        water = make_ingredient(water_pct=100.0)
        _, mix1 = recipe_pac([(sugar, 100.0), (water, 400.0)])  # type: ignore[arg-type]
        _, mix2 = recipe_pac([(sugar, 200.0), (water, 800.0)])  # type: ignore[arg-type]
        # pac_water should be identical
        assert mix1 is not None and mix2 is not None
        assert abs(mix1 - mix2) < 0.01
