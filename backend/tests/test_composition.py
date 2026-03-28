"""Tests for composition-level calculations."""

from __future__ import annotations

import pytest

from tests.conftest import make_ingredient


class TestIngredientTotalSolidsPct:
    """Tests for the ingredient-level composition helper."""

    def test_all_water_is_zero_solids(self):
        from api.services.composition import ingredient_total_solids_pct

        ing = make_ingredient(water_pct=100.0)
        assert ingredient_total_solids_pct(ing) == pytest.approx(0.0)

    def test_no_water_is_all_solids(self):
        from api.services.composition import ingredient_total_solids_pct

        ing = make_ingredient(water_pct=0.0)
        assert ingredient_total_solids_pct(ing) == pytest.approx(100.0)

    def test_typical_dry_ingredient(self):
        from api.services.composition import ingredient_total_solids_pct

        ing = make_ingredient(water_pct=3.0)
        assert ingredient_total_solids_pct(ing) == pytest.approx(97.0)

    def test_none_water_treated_as_zero(self):
        from api.services.composition import ingredient_total_solids_pct

        ing = make_ingredient()
        assert ingredient_total_solids_pct(ing) == pytest.approx(100.0)

    def test_alcohol_reduces_solids(self):
        """Alcohol is not a solid — total_solids = 100 - water - alcohol."""
        from api.services.composition import ingredient_total_solids_pct

        ing = make_ingredient(water_pct=60.0, alcohol_pct=10.0)
        assert ingredient_total_solids_pct(ing) == pytest.approx(30.0)

    def test_cannot_go_negative(self):
        """If water+alcohol > 100 for some reason, clamp to 0."""
        from api.services.composition import ingredient_total_solids_pct

        ing = make_ingredient(water_pct=80.0, alcohol_pct=30.0)
        assert ingredient_total_solids_pct(ing) == pytest.approx(0.0)


class TestCalculateComposition:
    def test_weighted_averages(self):
        from api.services.calculator import calculate_composition

        fat = make_ingredient(total_fat_pct=100.0, water_pct=0.0)
        water = make_ingredient(water_pct=100.0, total_fat_pct=0.0)
        result = calculate_composition([(fat, 50.0), (water, 50.0)])  # type: ignore[arg-type]

        assert result.total_weight_g == pytest.approx(100.0)
        assert result.total_fat_pct == pytest.approx(50.0)
        assert result.water_pct == pytest.approx(50.0)

    def test_total_solids_complement_of_water(self):
        from api.services.calculator import calculate_composition

        ing = make_ingredient(water_pct=35.0)
        result = calculate_composition([(ing, 100.0)])  # type: ignore[arg-type]
        assert result.total_solids_pct == pytest.approx(65.0)

    def test_stabilizer_pct_contributes_weighted_amount(self):
        from api.services.calculator import calculate_composition

        stab = make_ingredient(stabilizer_pct=25.0)
        other = make_ingredient(stabilizer_pct=0.0)
        result = calculate_composition([(stab, 5.0), (other, 95.0)])  # type: ignore[arg-type]
        # 5g * 25% = 1.25g stabilizer in 100g mix -> 1.25%
        assert result.stabilizer_pct == pytest.approx(1.25)
        assert result.emulsifier_pct == pytest.approx(0.0)

    def test_emulsifier_pct_contributes_weighted_amount(self):
        from api.services.calculator import calculate_composition

        emul = make_ingredient(emulsifier_pct=40.0)
        other = make_ingredient(emulsifier_pct=0.0)
        result = calculate_composition([(emul, 10.0), (other, 90.0)])  # type: ignore[arg-type]
        # 10g * 40% = 4g emulsifier in 100g mix -> 4%
        assert result.emulsifier_pct == pytest.approx(4.0)
        assert result.stabilizer_pct == pytest.approx(0.0)

    def test_none_attributes_treated_as_absent(self):
        from api.services.calculator import calculate_composition

        ing = make_ingredient()  # all None
        result = calculate_composition([(ing, 100.0)])  # type: ignore[arg-type]
        assert result.total_fat_pct == pytest.approx(0.0)
        assert result.protein_pct == pytest.approx(0.0)

    def test_alcohol_excluded_from_total_solids(self):
        from api.services.calculator import calculate_composition

        ing = make_ingredient(water_pct=60.0, alcohol_pct=10.0)
        result = calculate_composition([(ing, 100.0)])  # type: ignore[arg-type]
        assert result.total_solids_pct == pytest.approx(30.0)
        assert result.alcohol_pct == pytest.approx(10.0)

    def test_msnf_included_in_result(self):
        from api.services.calculator import calculate_composition

        ing = make_ingredient(msnf_pct=8.5, water_pct=87.0)
        result = calculate_composition([(ing, 1000.0)])  # type: ignore[arg-type]
        assert result.msnf_pct == pytest.approx(8.5)

    def test_multi_ingredient_protein_weighted(self):
        from api.services.calculator import calculate_composition

        a = make_ingredient(protein_pct=10.0, water_pct=80.0)
        b = make_ingredient(protein_pct=0.0, water_pct=0.0)
        result = calculate_composition([(a, 200.0), (b, 800.0)])  # type: ignore[arg-type]
        # 200 * 10/100 = 20g protein in 1000g → 2%
        assert result.protein_pct == pytest.approx(2.0)
