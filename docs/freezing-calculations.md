# Freezing Calculations

This document describes how iscreami calculates PAC, initial freezing point, freezing curve, and serving temperature.

## PAC (Potere AntiCongelante)

PAC quantifies the freezing-point depression power of a solute relative to sucrose. It is defined as:

$$PAC_{factor} = \frac{MW_{sucrose}}{MW_{solute}} \times 100$$

Sucrose (MW 342.3) is the reference with PAC = 100. Smaller molecules depress the freezing point more per gram.

### PAC factors used

| Solute    | MW    | PAC factor |
| --------- | ----- | ---------- |
| Sucrose   | 342.3 | 100        |
| Lactose   | 342.3 | 100        |
| Maltose   | 342.3 | 100        |
| Glucose   | 180.2 | 190        |
| Fructose  | 180.2 | 190        |
| Galactose | 180.2 | 190        |
| NaCl      | 58.4  | 585        |
| Ethanol   | 46.1  | 743        |

Sodium (as reported on nutrition labels in mg) is first converted to an NaCl mass equivalent using the NaCl/Na atomic weight ratio (≈ 2.58), then multiplied by the NaCl PAC factor.

### PAC per ingredient

For each ingredient the PAC (g sucrose-equivalent per 100 g ingredient) is summed across all active solutes:

$$PAC_{ingredient} = \sum_{s} \frac{pct_s \times PAC_s}{100}$$

where $pct_s$ is the mass percentage of solute $s$ in the ingredient and $PAC_s$ is its factor. If individual sugar fractions are not specified, total sugar is treated as sucrose (PAC = 100). A manual override field is available to bypass the calculation entirely.

### Recipe-level PAC

Two conventions are reported:

$$PAC_{mix} = \frac{\sum_i w_i \cdot PAC_i}{\sum_i w_i} \quad \text{(g per 100 g total mix)}$$

$$PAC_{water} = \frac{\sum_i w_i \cdot PAC_i}{\sum_i w_i \cdot water\_pct_i} \times 100 \quad \text{(g per 100 g free water)}$$

$PAC_{water}$ (also called the normalised PAC, or PACn) is the value used for all freezing calculations.

---

## Initial Freezing Point

The freezing point is calculated in two parts: sugar/solute depression and a separate MSNF salt correction, following Leighton (1927).

### Sugar/solute depression

The Pickering (1891) empirical curve gives the freezing point depression of sucrose solutions directly from the concentration in g per 100 g water. Leighton (1927) tabulated 60 anchor points from this curve at 3-unit intervals from 3 to 180 g/100 g water. iscreami stores these exact anchor values and linearly interpolates between them. Beyond 180 g/100 g water the slope is extrapolated at 0.08 °C per unit.

Because iscreami converts all solutes to sucrose-equivalents via PAC before looking up the curve, the single Pickering table handles sugars, alcohol, and NaCl in a unified way.

### MSNF salt correction

The mineral salts in milk solids-not-fat (MSNF) depress the freezing point independently of the sugar calculation. Leighton (1927) derived an apparent molecular weight for milk salts of 78.6 and expressed the correction as:

$$FPD_{salt} = \frac{MSNF \times 2.37}{W}$$

where $MSNF$ and $W$ are both in g per 100 g mix (i.e. percentages). The constant 2.37 consolidates the molecular weight formula constants for milk salt composition.

### Total initial freezing point

$$FPD_{total} = FPD_{sugar}(PAC_{water}) + FPD_{salt}$$

$$T_{freeze} = -FPD_{total} \quad (°C)$$

---

## Freezing Curve

As temperature falls below the initial freezing point, water progressively turns to ice. The remaining liquid becomes more concentrated, which further depresses its freezing point — a self-reinforcing process that is captured by the freezing curve.

At any point where a fraction $f$ (0–1) of the total water has frozen, the solutes that were dissolved in all of the water are now dissolved in only the unfrozen fraction $(1-f)$, so the effective normalised PAC rises:

$$PAC_{eff} = \frac{PAC_{water}}{1 - f}$$

The salt correction concentrates in the same way:

$$FPD_{salt,eff} = \frac{MSNF \times 2.37}{W \times (1 - f)}$$

The equilibrium temperature at frozen fraction $f$ is therefore:

$$T(f) = -\left[FPD_{sugar}(PAC_{eff}) + FPD_{salt,eff}\right]$$

To generate the curve, iscreami evaluates $T(f)$ for each 1 °C step from 0 °C down to −40 °C by numerically inverting the above: for a given temperature, binary search finds the frozen fraction $f$ that satisfies the equation to within ~0.0001% in 60 iterations.

---

## Serving Temperature

The serving temperature is defined as the temperature at which **75% of the water in the mix is frozen** — a widely used industry target that gives the right balance of scoopability and structure. It is read directly from the freezing curve at $f = 0.75$.

---

## References

- Pickering, S. U. (1891). The freezing point relationships of cane sugar. _Berichte der Deutschen Chemischen Gesellschaft_, 24, 3333.
- Leighton, A. (1927). On the calculation of the freezing point of ice-cream mixes and of the quantities of ice separated during the freezing process. _Journal of Dairy Science_, 10(4), 300–308. (`docs/ref/Leighton.pdf`)
- Goff, H. D., & Hartel, R. W. (2013). _Ice Cream_ (7th ed.). Springer. — Table 6.1 reproduces the Pickering anchor data used here. (`docs/ref/Ice Cream - Goff and Hartel.pdf`)
