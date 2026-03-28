# Freezing Point Depression of a Mix

To calculate the freezing point of a given mix, the first step is to determine the equivalent content of sucrose in the mix, based on all the mono- and disaccharides that are present. This is referred to as the sucrose equivalence (SE) in g/100 g of mix.

$$
SE = (MSNF \times 0.545) + (WS \times 0.765) + S
+ (10DE\ CSS \times 0.2) + (36DE\ CSS \times 0.6) + (42DE\ CSS \times 0.8) + (62DE\ CSS \times 1.2)
+ (HFCS \times 1.8) + (F \times 1.9)
$$

Where:

- **MSNF** = milk solids-not-fat; 0.545 is the percentage of lactose typical of MSNF.
- **WS** = whey solids (from dry or condensed whey); 0.765 is the percentage of lactose typically found in whey solids.
- **S** = sucrose or other disaccharides such as maltose or lactose (if added directly as a separate ingredient, otherwise accounted for in the MSNF or whey solids calculations) or disaccharide alcohols such as maltitol or lactitol.
- **DE** = dextrose equivalence of the CSS; the various factors convert the carbohydrates in the starch hydrolysate to sucrose equivalents.
- **HFCS** = high fructose corn syrup, which is mostly monosaccharide; factor of 1.8 converts it to equivalent sucrose content.
- **F** = pure fructose or other pure monosaccharides such as dextrose, or monosaccharide 6-carbon alcohols such as sorbitol; factor of 1.9 converts it to equivalent sucrose content based on molecular weight ratios. All in g/100 g mix (or %).

---

**Table 6.1** — Freezing point depression (°C) below 0°C of sucrose solutions (g/100 g water)

| g/100 g water | FPD (°C) | g/100 g water | FPD (°C) | g/100 g water | FPD (°C) |
|--------------:|---------:|--------------:|---------:|--------------:|---------:|
| 3             | 0.18     | 63            | 4.10     | 123           | 9.19     |
| 6             | 0.35     | 66            | 4.33     | 126           | 9.45     |
| 9             | 0.53     | 69            | 4.54     | 129           | 9.71     |
| 12            | 0.72     | 72            | 4.77     | 132           | 9.96     |
| 15            | 0.90     | 75            | 5.00     | 135           | 10.22    |
| 18            | 1.10     | 78            | 5.26     | 138           | 10.47    |
| 21            | 1.29     | 81            | 5.53     | 141           | 10.72    |
| 24            | 1.47     | 84            | 5.77     | 144           | 10.97    |
| 27            | 1.67     | 87            | 5.99     | 147           | 11.19    |
| 30            | 1.86     | 90            | 6.23     | 150           | 11.41    |
| 33            | 2.03     | 93            | 6.50     | 153           | 11.63    |
| 36            | 2.21     | 96            | 6.80     | 156           | 11.88    |
| 39            | 2.40     | 99            | 7.04     | 159           | 12.14    |
| 42            | 2.60     | 102           | 7.32     | 162           | 12.40    |
| 45            | 2.78     | 105           | 7.56     | 165           | 12.67    |
| 48            | 2.99     | 108           | 7.80     | 168           | 12.88    |
| 51            | 3.20     | 111           | 8.04     | 171           | 13.08    |
| 54            | 3.42     | 114           | 8.33     | 174           | 13.28    |
| 57            | 3.63     | 117           | 8.62     | 177           | 13.48    |
| 60            | 3.85     | 120           | 8.92     | 180           | 13.68    |

*Data were extrapolated from Leighton (1927), originally derived from Pickering (1891, as cited by Leighton).*

---

If blended protein, lactose, and mineral ingredients are used as a source of MSNF, the lactose and salts in those ingredients should be included directly in the calculation rather than using the factors for MSNF or WP. Simply ensure that all lactose and salts are accounted for and none are double-counted. If xylitol (5-carbon sugar alcohol, MW 152), erythritol (4-carbon sugar alcohol, MW 122), or other such low molecular weight sweeteners are included in the formulation, the molecular weight of sucrose (342) divided by their molecular weight could be used as the appropriate factor.

The equivalent concentration of sucrose in water (g/100 g water) is then determined by dividing the SE by the water content:

$$\frac{g\ sucrose}{100\ g\ water} = \frac{SE \times 100}{W}$$

where $W$ is the water content (100 − total solids, %).

To obtain the freezing point depression associated with this concentration of SE in water, $FPD_{SE}$, Table 6.1 is used.

The contribution to freezing point depression from salts in MSNF and WS is found using the following equation:

$$FPD_{SA} = \frac{(MSNF + WS) \times 2.37}{W}$$

Here, $FPD_{SA}$ is the freezing point depression for salts (°C) contained in MSNF and WS, and the constant 2.37 is based on the average molecular weight and concentration of the salts present in milk. For computation in °F, the factor 4.26 is used.

To obtain the freezing point depression of the ice cream mix, $FPD_T$, the two contributions are summed:

$$FPD_T = FPD_{SE} + FPD_{SA}$$

---

### Example Problem 13

Calculate the initial freezing point of an ice cream mix containing 10% MSNF, 2% whey solids, 12% sucrose, 4% 42DE CSS, and 60% water (40% total solids).

First, calculate the sucrose equivalents:

$$SE = (10 \times 0.545) + (2 \times 0.765) + 12 + (4 \times 0.8) = 22.18$$

The equivalent concentration of sucrose in water is:

$$\frac{g\ sucrose}{100\ g\ water} = \frac{22.18 \times 100}{60} = 36.97$$

By interpolation, find the freezing point depression for this level of sucrose equivalent from Table 6.1:

$$FPD_{SE} = 2.27°C$$

For salts:

$$FPD_{SA} = \frac{(10 + 2) \times 2.37}{60} = 0.47°C$$

Total freezing point depression for the mix:

$$FPD_T = 2.27° + 0.47° = 2.74°C$$

Thus, the initial freezing point temperature for this ice cream mix is **−2.74°C**.

---

## Freezing Curves

The initial freezing point can then be used to compute a freezing curve, where the percent of water frozen in the mix (removed as ice) is plotted against freezing temperature. This is done by continually reducing the water content ($W$) in the mix and recalculating $FPD_T$ as above, since the remainder of the water is converted to ice and no longer acts as a solution.

**Table 6.2** — Freezing point depression values applicable to Example Problem 13, when 10–80% of the water in the ice cream is frozen

| % Water frozen | W  | g Sucrose/100 g water | FPD_SE | FPD_SA | FPD_T |
|---------------:|---:|----------------------:|-------:|-------:|------:|
| 10             | 54 | 41.07                 | 2.53   | 0.53   | 3.06  |
| 20             | 48 | 46.21                 | 2.86   | 0.59   | 3.45  |
| 30             | 42 | 52.81                 | 3.33   | 0.68   | 4.01  |
| 40             | 36 | 61.61                 | 3.97   | 0.79   | 4.76  |
| 50             | 30 | 73.93                 | 4.92   | 0.95   | 5.87  |
| 60             | 24 | 92.42                 | 6.45   | 1.18   | 7.63  |
| 70             | 18 | 123.22                | 9.21   | 1.58   | 10.79 |
| 75             | 15 | 147.87                | 11.26  | 1.90   | 13.16 |
| 80             | 12 | 184.83                | 14.27  | 2.37   | 16.61 |

*FPD_SE: freezing point depression of sucrose equivalents; FPD_SA: freezing point depression of salts; FPD_T: total freezing point depression.*

---

### Example Problem 14

Calculate the freezing curve for ice cream, based on a mix containing 10% MSNF, 2% whey solids, 12% sucrose, 4% 42DE CSS, and 60% water (40% total solids).

From above, the initial freezing point (0% water frozen) was −2.74°C. When 20% of the water is frozen, 80% is still liquid, so $W$ is now $(60\% \times 0.8) = 48\%$. The g sucrose/100 g water is now $22.18 \times 100 / 48 = 46.21$ g/100 g water. From Table 6.1, this ($FPD_{SE}$) corresponds to 2.86°C. For the milk salts:

$$FPD_{SA} = \frac{(10 + 2) \times 2.37}{48} = 0.59°C$$

Thus $FPD_T = 2.86° + 0.59° = 3.45°C$. At −3.45°C, 20% of the water in this mix will be frozen.

Similarly, a series of ice contents can be used, sufficient to plot a freezing curve. Such values are shown in Table 6.2 and plotted in Fig. 6.1. Table 6.3 shows an adaptation of the above freezing curve calculation that, when fed into an Excel spreadsheet, will give the predicted $FPD_{Total}$ (freezing point) and theoretical freezing curve, plotted as % water frozen in the mix (first column) graphed against $FPD_{Total}$ (last column).
