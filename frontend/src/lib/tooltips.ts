/**
 * Comprehensive tooltip content library for the ice cream calculator.
 * Use these strings with Tooltip and InfoIcon components for consistent information.
 */

export const TOOLTIPS = {
    // === Calculator Page ===
    profile:
        "Choose a style target (e.g. gelato, sorbet, soft serve) to see how your recipe compares to typical ranges for that style. Leave blank to calculate without targets.",

    // === Metrics & Composition ===
    totalSolids:
        "Everything in the mix that isn't water — fat, sugars, proteins, and dry ingredients — expressed as a percentage. Aim for roughly 35–42% for most ice creams; too low and the result is icy, too high and it can taste dense or pasty.",
    totalFat:
        "Total fat as a percentage of the mix. Fat is the main source of creaminess and richness — cream, egg yolks, and butter all contribute. Classic ice cream typically sits around 8–16%.",
    milkFat:
        "Fat that comes specifically from dairy — milk, cream, or butter. It gives ice cream its characteristic rich, milky flavour and smooth mouthfeel.",
    msnf: "Milk Solids Not Fat (MSNF) — the proteins and lactose in dairy that aren't fat or water. They improve body, add a subtle milky flavour, and help prevent large ice crystals from forming. Too much can make the texture feel sandy.",
    sugars:
        "Total sugars and sweeteners as a percentage of the mix. Sugars do double duty: they add sweetness and lower the freezing point, keeping ice cream scoopable. Too little and it freezes rock-hard; too much and it stays too soft.",
    protein:
        "Protein (mainly from dairy) as a percentage of the mix. Proteins help stabilise the mix during freezing, improve texture, and contribute to a smoother, creamier result.",
    stabilizer:
        "Hydrocolloids like guar gum, locust bean gum, or carrageenan that bind water and slow ice crystal growth. A small amount (typically 0.1–0.5%) helps ice cream stay smooth in the freezer and resist melting quickly.",
    emulsifier:
        "Ingredients like lecithin or mono-diglycerides that help fat and water mix together evenly. Good emulsification creates a smoother, more uniform texture. Egg yolks are a natural source.",
    sweetness:
        "Sweetness Power (POD) — how sweet your whole mix is, expressed as a percentage equivalent to sucrose. A value of 16 means the mix tastes as sweet as a solution with 16g of sugar per 100g. Typical ice cream sits around 14–18. Use this to balance perceived sweetness when substituting sweeteners.",

    // === Freezing Point & PAC ===
    pac: "Anti-Freezing Power (PAC from the Italian 'Potere AntiCongelante'). A score that totals up how much all the dissolved ingredients lower the freezing point. Higher PAC = softer ice cream at a given temperature.",
    pacMix:
        "PAC calculated per 100g of total mix. This is the headline number for comparing recipes — higher means the mix resists freezing more strongly and will be softer at a given temperature.",
    freezingPoint:
        "The temperature at which your mix just starts to freeze. Below this point, water begins turning to ice crystals. The freezing curve below shows how much water is frozen at each temperature as it continues to drop.",
    servingTemp:
        "The calculated temperature at which 75% of your mix's water is frozen — the industry benchmark for scoopable consistency. In a typical dipping cabinet (around −12°C), a more negative value here means softer ice cream; less negative means harder and icier.",
    // === Ingredients ===
    ingredientPacOverride:
        "Manually set the PAC value for this ingredient instead of using the calculated one. Useful when you have lab data or a manufacturer spec that differs from the default.",
    ingredientPodOverride:
        "Manually set the sweetness score (POD) for this ingredient instead of using the calculated one. Useful for novel sweeteners or when matching a known sensory result.",

    // === Recipe Management ===
    saveRecipe: "Save your current recipe for future use",
    deleteRecipe: "Delete the currently open recipe",
};

