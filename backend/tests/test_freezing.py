"""Tests for freezing point depression calculations."""

from __future__ import annotations

import itertools

import pytest

from api.services.freezing import (
    _lookup_fpd,
    fpd_at_frozen_pct,
    freezing_curve,
    freezing_point,
    frozen_water_fraction,
)


class TestLookupFPD:
    """Tests for the internal _lookup_fpd interpolation function."""

    def test_zero_returns_zero(self):

        assert _lookup_fpd(0) == pytest.approx(0.0)

    def test_negative_returns_zero(self):

        assert _lookup_fpd(-5) == pytest.approx(0.0)

    def test_below_first_anchor_interpolates_from_origin(self):

        # First anchor is (3, 0.18); at 1.5 should be ~0.09
        result = _lookup_fpd(1.5)
        assert 0.08 < result < 0.10

    def test_exact_first_anchor(self):

        assert _lookup_fpd(3) == pytest.approx(0.18)

    def test_known_table_value_at_25(self):
        """Between anchors 24 (1.47) and 27 (1.67) → 25 interpolates to ~1.53."""

        result = _lookup_fpd(25.0)
        assert abs(result - 1.533) < 0.01

    def test_exact_last_anchor(self):

        assert _lookup_fpd(180) == pytest.approx(13.68)

    def test_above_last_anchor_extrapolates(self):

        # Beyond 180: extrapolate at 0.08°C/unit
        result = _lookup_fpd(190)
        expected = 13.68 + (190 - 180) * 0.08
        assert abs(result - expected) < 0.01

    def test_monotonically_increasing(self):

        values = [_lookup_fpd(x) for x in range(0, 200, 5)]
        assert all(a <= b for a, b in itertools.pairwise(values))


class TestFreezingPoint:
    def test_zero_pac_returns_zero(self):

        assert freezing_point(0) == pytest.approx(0.0)
        assert freezing_point(None) == pytest.approx(0.0)

    def test_negative_pac_returns_zero(self):

        assert freezing_point(-5.0) == pytest.approx(0.0)

    def test_known_freezing_point_at_pac25(self):
        """PAC_water=25 → FPD ~1.53 → freezing_point ≈ -1.53°C."""

        fp = freezing_point(25.0)
        assert abs(fp - (-1.53)) < 0.02

    def test_returns_negative_value(self):

        assert freezing_point(30.0) < 0.0

    def test_msnf_increases_fpd(self):
        """Adding MSNF should lower (more negative) the freezing point."""

        fp_plain = freezing_point(25.0, msnf_pct=0.0, water_pct=80.0)
        fp_msnf = freezing_point(25.0, msnf_pct=10.0, water_pct=80.0)
        assert fp_msnf < fp_plain


class TestFrozenWaterFraction:
    def test_at_or_above_freezing_point_no_ice(self):

        assert frozen_water_fraction(0.0, 25.0) == pytest.approx(0.0)
        assert frozen_water_fraction(5.0, 25.0) == pytest.approx(0.0)

    def test_zero_pac_returns_zero(self):

        assert frozen_water_fraction(-10.0, 0.0) == pytest.approx(0.0)
        assert frozen_water_fraction(-10.0, None) == pytest.approx(0.0)

    def test_below_freezing_some_ice(self):

        frac = frozen_water_fraction(-10.0, 25.0)
        assert 0.0 < frac < 1.0

    def test_well_below_freezing_mostly_frozen(self):

        frac = frozen_water_fraction(-20.0, 25.0)
        assert frac > 0.5

    def test_fraction_increases_with_colder_temperature(self):

        f1 = frozen_water_fraction(-5.0, 25.0)
        f2 = frozen_water_fraction(-15.0, 25.0)
        assert f2 > f1

    def test_at_exact_freezing_point_returns_zero(self):

        fp = freezing_point(25.0)
        frac = frozen_water_fraction(fp, 25.0)
        assert frac == pytest.approx(0.0)


class TestFreezingCurve:
    def test_default_curve_starts_at_zero(self):

        curve = freezing_curve(25.0)
        assert curve[0][0] == pytest.approx(0.0)
        assert curve[0][1] == pytest.approx(0.0)

    def test_curve_length_matches_step(self):

        curve = freezing_curve(25.0, min_temp=-30.0, step=1.0)
        assert len(curve) == 31  # 0 to -30 inclusive

    def test_curve_temperatures_descend(self):

        curve = freezing_curve(25.0, min_temp=-10.0, step=1.0)
        temps = [p[0] for p in curve]
        assert all(a > b for a, b in itertools.pairwise(temps))

    def test_frozen_fraction_non_decreasing(self):

        curve = freezing_curve(25.0, min_temp=-20.0, step=1.0)
        fracs = [p[1] for p in curve]
        assert all(a <= b for a, b in itertools.pairwise(fracs))

    def test_zero_pac_all_zeros(self):

        curve = freezing_curve(0.0, min_temp=-10.0, step=1.0)
        assert all(f == 0.0 for _, f in curve)

    def test_none_pac_all_zeros(self):

        curve = freezing_curve(None, min_temp=-10.0, step=1.0)
        assert all(f == 0.0 for _, f in curve)


class TestFPDAtFrozenPct:
    def test_no_frozen_water_equals_freezing_point(self):
        """At 0% frozen, result should match freezing_point() FPD (positive)."""

        pac_water = 25.0
        fpd_zero_frozen = fpd_at_frozen_pct(0.0, pac_water, 0.0, 100.0)
        expected = _lookup_fpd(pac_water)
        assert abs(fpd_zero_frozen - expected) < 0.01

    def test_higher_frozen_fraction_raises_fpd(self):
        """More ice → solutes concentrate → higher FPD."""

        fpd_low = fpd_at_frozen_pct(10.0, 25.0, 0.0, 80.0)
        fpd_high = fpd_at_frozen_pct(50.0, 25.0, 0.0, 80.0)
        assert fpd_high > fpd_low

    def test_msnf_adds_to_fpd(self):

        fpd_plain = fpd_at_frozen_pct(0.0, 25.0, 0.0, 80.0)
        fpd_msnf = fpd_at_frozen_pct(0.0, 25.0, 10.0, 80.0)
        assert fpd_msnf > fpd_plain
