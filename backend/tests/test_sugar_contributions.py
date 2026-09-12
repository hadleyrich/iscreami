"""Direct tests for the shared sugar_contributions_per_100g() helper.

The helper lives next to SUGAR_FIELDS in api/models.py and is consumed by both
PAC (services/pac.py) and POD (services/sweetness.py). Because the extraction
made it a single point of failure for every consumer, it ships with its own
tests pinning the breakdown-vs-fallback decision, per the repo standard
journaled in .patrol/atlas.md (shared helpers ship WITH tests).
"""

from __future__ import annotations

from api.models import sugar_contributions_per_100g
from tests.conftest import make_ingredient


class TestSugarContributionsPer100g:
    def test_breakdown_pairs_are_returned_in_field_order(self):
        ing = make_ingredient(sucrose_pct=5.0, glucose_pct=6.0)
        assert sugar_contributions_per_100g(ing) == [("sucrose", 5.0), ("glucose", 6.0)]

    def test_breakdown_ignores_zero_and_none_entries(self):
        # Zeroes are excluded when the breakdown is present, matching the
        # pct > 0 filter that PAC/POD relied on pre-extraction.
        ing = make_ingredient(sucrose_pct=5.0, glucose_pct=0.0, fructose_pct=None)
        assert sugar_contributions_per_100g(ing) == [("sucrose", 5.0)]

    def test_total_sugar_falls_back_to_pure_sucrose(self):
        # No breakdown fields set -> total_sugar_pct treated as sucrose.
        ing = make_ingredient(total_sugar_pct=70.0)
        assert sugar_contributions_per_100g(ing) == [("sucrose", 70.0)]

    def test_empty_when_no_sugar_data(self):
        ing = make_ingredient()
        assert sugar_contributions_per_100g(ing) == []

    def test_all_zero_breakdown_does_not_fall_back(self):
        # Subtle edge: presence of the breakdown (all-zero) wins over the
        # total_sugar fallback. A present-but-zero breakdown yields an empty
        # list -- total_sugar_pct is NOT applied as sucrose.
        ing = make_ingredient(
            sucrose_pct=0.0,
            glucose_pct=0.0,
            fructose_pct=0.0,
            lactose_pct=0.0,
            maltose_pct=0.0,
            galactose_pct=0.0,
            total_sugar_pct=70.0,
        )
        assert sugar_contributions_per_100g(ing) == []
