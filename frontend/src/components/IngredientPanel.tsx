import { Trash2 } from "lucide-react";
import type { RecipeRow } from "../hooks/useRecipeCalculator";

interface IngredientPanelProps {
  readonly rows: RecipeRow[];
  readonly onWeightChange: (ingredientId: string, weight: number) => void;
  readonly onRemove: (ingredientId: string) => void;
}

interface IngredientRowWithPct {
  row: RecipeRow;
  pct: number;
  originalIndex: number;
}

export function IngredientPanel({
  rows,
  onWeightChange,
  onRemove,
}: IngredientPanelProps) {
  const totalWeight = rows.reduce((sum, r) => sum + r.weight_grams, 0);
  const rowsWithPct: IngredientRowWithPct[] = rows.map((row, index) => ({
    row,
    pct: totalWeight > 0 ? (row.weight_grams / totalWeight) * 100 : 0,
    // Keep original insertion order as tie-breaker when percentages are equal.
    originalIndex: index,
  }));
  const sortedRows = [...rowsWithPct].sort((a, b) => {
    if (b.pct !== a.pct) return b.pct - a.pct;
    return a.originalIndex - b.originalIndex;
  });

  return (
    <div className="space-y-1">
      {/* Header */}
      <div className="grid grid-cols-[1fr_100px_60px_40px] gap-2 px-2 py-1.5 rounded-md bg-base-200/40 text-xs font-semibold text-base-content/50 uppercase tracking-wider items-center">
        <span>Ingredient</span>
        <span className="text-right">Grams</span>
        <span className="text-right">%</span>
        <span></span>
      </div>

      {rows.length === 0 && (
        <div className="rounded-md border border-dashed border-base-300 bg-base-200/20 px-3 py-4 text-sm text-base-content/45 italic">
          Search and add ingredients above
        </div>
      )}

      {rows.length > 0 && (
        <div className="space-y-1">
          <div className="px-2 pt-2 pb-1">
            <p className="text-xs text-base-content/45 leading-snug">
              Sorted by contribution (%) so the biggest ingredients are always at the top.
            </p>
          </div>

          {sortedRows.map(({ row, pct }) => (
            <div
              key={row.ingredient.id}
              className="grid grid-cols-[1fr_100px_60px_40px] gap-2 items-center px-2 py-1.5 rounded hover:bg-base-200/50"
            >
              <div className="min-w-0">
                <span className="text-sm font-medium truncate block">
                  {row.ingredient.name}
                </span>
                {row.ingredient.category && (
                  <span className="text-xs text-base-content/40">
                    {row.ingredient.category.name}
                  </span>
                )}
              </div>
              <input
                type="number"
                min={0}
                step={1}
                value={row.weight_grams}
                aria-label={`Weight for ${row.ingredient.name} in grams`}
                onChange={(e) =>
                  onWeightChange(
                    row.ingredient.id,
                    Math.max(0, Number.parseFloat(e.target.value) || 0)
                  )
                }
                className="input input-bordered input-xs w-full text-right"
              />
              <span className="text-right text-sm text-base-content/60">{pct.toFixed(1)}%</span>
              <button
                type="button"
                onClick={() => onRemove(row.ingredient.id)}
                className="btn btn-ghost btn-xs text-base-content/40 hover:text-error"
                aria-label={`Remove ${row.ingredient.name}`}
              >
                <Trash2 size={14} />
              </button>
            </div>
          ))}
        </div>
      )}

      {/* Total */}
      {rows.length > 0 && (
        <div className="grid grid-cols-[1fr_100px_60px_40px] gap-2 px-2 py-2 border-t border-base-200 mt-2 rounded-md bg-base-200/30">
          <span className="text-sm font-semibold">Total</span>
          <span className="text-right text-sm font-semibold">
            {totalWeight.toFixed(0)}
          </span>
          <span className="text-right text-sm font-semibold">100%</span>
          <span></span>
        </div>
      )}
    </div>
  );
}
