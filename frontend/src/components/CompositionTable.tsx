import type { CompositionResult, SweetnessResult } from "../types";
import { InfoIcon } from "./InfoIcon";
import { TOOLTIPS } from "../lib/tooltips";

interface CompositionTableProps {
  readonly composition: CompositionResult;
  readonly sweetness?: SweetnessResult;
}

const ROWS: { label: string; key: keyof CompositionResult; tooltip?: string }[] = [
  { label: "Total Weight", key: "total_weight_g" },
  { label: "Water", key: "water_pct" },
  { label: "Total Solids", key: "total_solids_pct", tooltip: TOOLTIPS.totalSolids },
  { label: "Total Fat", key: "total_fat_pct", tooltip: TOOLTIPS.totalFat },
  { label: "Saturated Fat", key: "saturated_fat_pct" },
  { label: "Trans Fat", key: "trans_fat_pct" },
  { label: "Milk Fat", key: "milk_fat_pct", tooltip: TOOLTIPS.milkFat },
  { label: "MSNF", key: "msnf_pct", tooltip: TOOLTIPS.msnf },
  { label: "Sugars", key: "total_sugar_pct", tooltip: TOOLTIPS.sugars },
  { label: "Protein", key: "protein_pct", tooltip: TOOLTIPS.protein },
  { label: "Carbohydrate", key: "carbohydrate_pct" },
  { label: "Fiber", key: "fiber_pct" },
  { label: "Alcohol", key: "alcohol_pct" },
  { label: "Stabilizer", key: "stabilizer_pct", tooltip: TOOLTIPS.stabilizer },
  { label: "Emulsifier", key: "emulsifier_pct", tooltip: TOOLTIPS.emulsifier },
];

export function CompositionTable({ composition, sweetness }: CompositionTableProps) {
  return (
    <div className="space-y-5">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-base-200">
            <th className="text-left py-1 font-medium text-base-content/60">Metric</th>
            <th className="text-right py-1 font-medium text-base-content/60">Value</th>
          </tr>
        </thead>
        <tbody>
          {ROWS.map(({ label, key, tooltip }) => {
            const val = composition[key];
            const unit = key === "total_weight_g" ? " g" : "%";
            return (
              <tr
                key={key}
                className="border-b border-base-200"
              >
                <td className="py-1">
                  <div className="flex items-center gap-1">
                    <span>{label}</span>
                    {tooltip && <InfoIcon label={tooltip} position="right" />}
                  </div>
                </td>
                <td className="py-1 text-right font-mono">
                  {val.toFixed(key === "total_weight_g" ? 0 : 2)}
                  {unit}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>

      {sweetness && sweetness.sweetener_breakdown.length > 0 && (
        <div>
          <div className="mb-2">
            <h3 className="text-sm font-semibold text-base-content/75">Sweetener Sources</h3>
            <p className="mt-1 text-xs text-base-content/45">
              Where the recipe's sweetness is coming from, by ingredient.
            </p>
          </div>
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-base-200">
                <th className="text-left py-1 font-medium text-base-content/60">Source</th>
                <th className="text-right py-1 font-medium text-base-content/60">g</th>
                <th className="text-right py-1 font-medium text-base-content/60">%</th>
              </tr>
            </thead>
            <tbody>
              {sweetness.sweetener_breakdown.map((item) => (
                <tr
                  key={item.ingredient_name}
                  className="border-b border-base-200"
                >
                  <td className="py-1">{item.ingredient_name}</td>
                  <td className="py-1 text-right font-mono">{item.weight_g.toFixed(1)}</td>
                  <td className="py-1 text-right font-mono">{item.pct_of_sweeteners.toFixed(1)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
