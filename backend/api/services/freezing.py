"""Freezing point depression and freezing curve calculations.

Algorithm from Leighton (1927):

- Lookup table: g sucrose-equivalent per 100g free water (normalized PAC) → FPD °C
- MSNF salt correction added on top: msnf_pct * 2.37 / water_pct
- As ice forms, solutes concentrate in remaining liquid:
    effective_pac = pac_water / (1 - frozen_fraction)

Key inputs:
    pac_water  — g sucrose-equiv per 100g free water (normalized / PACn)
    msnf_pct   — g MSNF per 100g mix  (for salt correction)
    water_pct  — g water per 100g mix
"""

from __future__ import annotations

import bisect

# Anchor points from Pickering (1891) as tabulated by Leighton (1927) and
# reproduced in Table 6.1 of Goff & Hartel, "Ice Cream" (8th ed.).
# g sucrose per 100 g water → FPD °C.
# Values between anchors are linearly interpolated; beyond 180 g/100g water
# the slope is extrapolated at 0.08 °C per unit (consistent with the curve
# flattening seen at high concentrations).
_PICKERING_ANCHORS: list[tuple[float, float]] = [
    (3, 0.18),
    (6, 0.35),
    (9, 0.53),
    (12, 0.72),
    (15, 0.90),
    (18, 1.10),
    (21, 1.29),
    (24, 1.47),
    (27, 1.67),
    (30, 1.86),
    (33, 2.03),
    (36, 2.21),
    (39, 2.40),
    (42, 2.60),
    (45, 2.78),
    (48, 2.99),
    (51, 3.20),
    (54, 3.42),
    (57, 3.63),
    (60, 3.85),
    (63, 4.10),
    (66, 4.33),
    (69, 4.54),
    (72, 4.77),
    (75, 5.00),
    (78, 5.26),
    (81, 5.53),
    (84, 5.77),
    (87, 5.99),
    (90, 6.23),
    (93, 6.50),
    (96, 6.80),
    (99, 7.04),
    (102, 7.32),
    (105, 7.56),
    (108, 7.80),
    (111, 8.04),
    (114, 8.33),
    (117, 8.62),
    (120, 8.92),
    (123, 9.19),
    (126, 9.45),
    (129, 9.71),
    (132, 9.96),
    (135, 10.22),
    (138, 10.47),
    (141, 10.72),
    (144, 10.97),
    (147, 11.19),
    (150, 11.41),
    (153, 11.63),
    (156, 11.88),
    (159, 12.14),
    (162, 12.40),
    (165, 12.67),
    (168, 12.88),
    (171, 13.08),
    (174, 13.28),
    (177, 13.48),
    (180, 13.68),
]
_ANCHOR_X = [p[0] for p in _PICKERING_ANCHORS]
_ANCHOR_Y = [p[1] for p in _PICKERING_ANCHORS]
_ANCHOR_MAX_X = _ANCHOR_X[-1]  # 180
_ANCHOR_MAX_Y = _ANCHOR_Y[-1]  # 13.68
_EXTRAPOLATION_SLOPE = 0.08  # °C per unit beyond last anchor


def _lookup_fpd(pac_water: float) -> float:
    """Return FPD °C for g sucrose-equivalent per 100g water.

    Linearly interpolates between Pickering (1891) anchor points up to
    180 g/100g water; extrapolates beyond at 0.08 °C per unit.
    """
    if pac_water <= 0:
        return 0.0
    if pac_water >= _ANCHOR_MAX_X:
        return _ANCHOR_MAX_Y + (pac_water - _ANCHOR_MAX_X) * _EXTRAPOLATION_SLOPE
    if pac_water <= _ANCHOR_X[0]:
        # Below first anchor: linear from origin through first point (≈0.06/unit)
        return _ANCHOR_Y[0] * pac_water / _ANCHOR_X[0]
    i = bisect.bisect_right(_ANCHOR_X, pac_water) - 1
    x0, x1 = _ANCHOR_X[i], _ANCHOR_X[i + 1]
    y0, y1 = _ANCHOR_Y[i], _ANCHOR_Y[i + 1]
    return y0 + (y1 - y0) * (pac_water - x0) / (x1 - x0)


def fpd_at_frozen_pct(
    frozen_pct: float,
    pac_water: float,
    msnf_pct: float,
    water_pct: float,
) -> float:
    """Total FPD (°C, positive) when frozen_pct % of water has frozen.

    As ice forms, solutes concentrate in the remaining liquid water, raising
    the effective normalized PAC and depressing the freezing point further.
    """
    unfrozen_pct = max(100.0 - frozen_pct, 0.001)
    effective_pac = pac_water / (unfrozen_pct / 100.0)
    salt_correction = msnf_pct * 2.37 / (water_pct / 100.0 * unfrozen_pct)
    return _lookup_fpd(effective_pac) + salt_correction


def freezing_point(
    pac_water: float | None,
    msnf_pct: float = 0.0,
    water_pct: float = 100.0,
) -> float:
    """Return freezing point in °C (negative).

    pac_water: normalized PAC, g sucrose-equiv per 100g free water
    msnf_pct:  g MSNF per 100g mix
    water_pct: g water per 100g mix
    """
    if pac_water is None or pac_water <= 0:
        return 0.0
    fpd = fpd_at_frozen_pct(0.0, pac_water, msnf_pct, water_pct)
    return -round(fpd, 2)


def frozen_water_fraction(
    temperature_c: float,
    pac_water: float | None,
    msnf_pct: float = 0.0,
    water_pct: float = 100.0,
) -> float:
    """Fraction of water (0–1) that is frozen at temperature_c.

    Uses binary search to invert the freezing curve T(frozen_pct).
    """
    if pac_water is None or pac_water <= 0 or temperature_c >= 0:
        return 0.0
    fp = freezing_point(pac_water, msnf_pct, water_pct)
    if temperature_c >= fp:
        return 0.0

    # T(frozen_pct) is monotonically decreasing: higher frozen_pct → colder T.
    lo, hi = 0.0, 99.9
    for _ in range(60):
        mid = (lo + hi) / 2.0
        t_mid = -fpd_at_frozen_pct(mid, pac_water, msnf_pct, water_pct)
        if t_mid > temperature_c:  # warmer than target → need more frozen
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2.0 / 100.0


def freezing_curve(
    pac_water: float | None,
    msnf_pct: float = 0.0,
    water_pct: float = 100.0,
    min_temp: float = -40.0,
    step: float = 1.0,
) -> list[tuple[float, float]]:
    """Freezing curve as (temperature_°C, frozen_water_%) from 0 °C to min_temp."""
    points: list[tuple[float, float]] = []
    temp = 0.0
    while temp >= min_temp:
        fraction = frozen_water_fraction(temp, pac_water, msnf_pct, water_pct)
        points.append((round(temp, 1), round(fraction * 100.0, 2)))
        temp = round(temp - step, 10)
    return points
