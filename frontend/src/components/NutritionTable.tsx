import type { NutritionResult } from "../types";
import { InfoIcon } from "./InfoIcon";
import { TOOLTIPS } from "../lib/tooltips";

interface NutritionTableProps {
  readonly nutrition: NutritionResult;
}

const PRIMARY_NUTRIENTS = ["energy_kj", "total_fat_g", "sugars_g", "protein_g"] as const;

const PRIMARY_CARD_STYLES: Record<(typeof PRIMARY_NUTRIENTS)[number], string> = {
  energy_kj: "bg-pink-50 text-pink-800 dark:bg-pink-900/20 dark:text-pink-300",
  total_fat_g: "bg-amber-50 text-amber-800 dark:bg-amber-900/20 dark:text-amber-300",
  sugars_g: "bg-sky-50 text-sky-800 dark:bg-sky-900/20 dark:text-sky-300",
  protein_g: "bg-green-50 text-green-800 dark:bg-green-900/20 dark:text-green-300",
};

const NUTRIENT_LABELS: Record<string, string> = {
  energy_kj: "Energy",
  total_fat_g: "Total Fat",
  saturated_fat_g: "Saturated Fat",
  trans_fat_g: "Trans Fat",
  carbohydrate_g: "Carbohydrate",
  sugars_g: "Sugars",
  fiber_g: "Fiber",
  protein_g: "Protein",
};

const NUTRIENT_UNITS: Record<string, string> = {
  energy_kj: "kJ",
  total_fat_g: "g",
  saturated_fat_g: "g",
  trans_fat_g: "g",
  carbohydrate_g: "g",
  sugars_g: "g",
  fiber_g: "g",
  protein_g: "g",
};

const NUTRIENT_TOOLTIPS: Record<string, string | undefined> = {
  energy_kj: undefined,
  total_fat_g: TOOLTIPS.totalFat,
  saturated_fat_g: undefined,
  trans_fat_g: undefined,
  carbohydrate_g: undefined,
  sugars_g: TOOLTIPS.sugars,
  fiber_g: undefined,
  protein_g: TOOLTIPS.protein,
};

export function NutritionTable({ nutrition }: NutritionTableProps) {
  const keys = Object.keys(NUTRIENT_LABELS);

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
        {PRIMARY_NUTRIENTS.map((key) => {
          const label = NUTRIENT_LABELS[key];
          const unit = NUTRIENT_UNITS[key];
          const decimals = key === "energy_kj" ? 0 : 1;
          const per100Raw = nutrition.per_100g[key];
          const per100Str = per100Raw == null ? "\u2014" : `${per100Raw.toFixed(decimals)} ${unit}`;

          return (
            <div key={key} className={`rounded-lg p-3 ${PRIMARY_CARD_STYLES[key]}`}>
              <div className="text-xs font-medium uppercase tracking-wider opacity-80">{label}</div>
              <div className="mt-1 text-xl font-bold tabular-nums">{per100Str}</div>
              <div className="mt-1 text-xs opacity-75">Per 100g</div>
            </div>
          );
        })}
      </div>

      <div className="rounded-lg border border-base-200 bg-base-100 px-3 py-3">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-base-200">
              <th className="text-left py-1 font-medium text-base-content/60">Nutrient</th>
              <th className="text-right py-1 font-medium text-base-content/60">Per 100g</th>
              <th className="text-right py-1 font-medium text-base-content/60">
                Per {nutrition.serving_size_g}g
              </th>
            </tr>
          </thead>
          <tbody>
            {keys.map((key) => {
              const label = NUTRIENT_LABELS[key];
              const unit = NUTRIENT_UNITS[key];
              const tooltip = NUTRIENT_TOOLTIPS[key];
              const decimals = key === "energy_kj" ? 0 : 1;
              const per100Raw = nutrition.per_100g[key];
              const perServingRaw = nutrition.per_serving[key];
              const per100Str = per100Raw == null ? "\u2014" : `${per100Raw.toFixed(decimals)} ${unit}`;
              const perServingStr = perServingRaw == null ? "\u2014" : `${perServingRaw.toFixed(decimals)} ${unit}`;
              const isPrimary = PRIMARY_NUTRIENTS.includes(key as (typeof PRIMARY_NUTRIENTS)[number]);

              return (
                <tr key={key} className={`border-b border-base-200 ${isPrimary ? "bg-base-200/30" : ""}`}>
                  <td className="py-1.5">
                    <div className="flex items-center gap-1">
                      <span className={isPrimary ? "font-medium" : ""}>{label}</span>
                      {tooltip && <InfoIcon label={tooltip} position="right" />}
                    </div>
                  </td>
                  <td className="py-1.5 text-right font-mono">{per100Str}</td>
                  <td className="py-1.5 text-right font-mono">{perServingStr}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
