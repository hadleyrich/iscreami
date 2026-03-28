import type { MetricComparison, MetricStatus } from "../types";
import { InfoIcon } from "./InfoIcon";
import { TOOLTIPS } from "../lib/tooltips";

// ─── Labels & units ───────────────────────────────────────────────────────────

const METRIC_LABELS: Record<string, string> = {
  total_solids: "Total Solids",
  total_fat: "Total Fat",
  milk_fat: "Milk Fat",
  sugar: "Sugars",
  msnf: "MSNF",
  stabilizer: "Stabilizer",
  emulsifier: "Emulsifier",
  sweetness: "Sweetness (POD)",
  serving_temp: "Serving Temp",
};

const METRIC_UNITS: Record<string, string> = {
  serving_temp: "°C",
};

const METRIC_TOOLTIPS: Record<string, string> = {
  total_solids: TOOLTIPS.totalSolids,
  total_fat: TOOLTIPS.totalFat,
  milk_fat: TOOLTIPS.milkFat,
  sugar: TOOLTIPS.sugars,
  msnf: TOOLTIPS.msnf,
  stabilizer: TOOLTIPS.stabilizer,
  emulsifier: TOOLTIPS.emulsifier,
  sweetness: TOOLTIPS.sweetness,
  serving_temp: TOOLTIPS.servingTemp,
};

// ─── Beginner-friendly hints ──────────────────────────────────────────────────

const HINTS: Record<string, Partial<Record<MetricStatus, string>>> = {
  total_solids: {
    in_range: "Great body and texture for scooping",
    below: "Low solids — may freeze rock-hard or be icy",
    above: "High solids — risk of dense or pasty texture",
  },
  total_fat: {
    in_range: "Great creaminess and mouthfeel",
    below: "Low fat — may taste less creamy or feel icy",
    above: "High fat — risk of greasy or heavy texture",
  },
  milk_fat: {
    in_range: "Classic dairy richness",
    below: "Low milk fat — less milky flavour and creaminess",
    above: "Very high milk fat — may taste heavy",
  },
  sugar: {
    in_range: "Good balance of sweetness and freeze",
    below: "Low sugar — will freeze too hard at serving temp",
    above: "High sugar — ice cream may be too soft",
  },
  msnf: {
    in_range: "Good body and protein structure",
    below: "Low MSNF — less body, more likely to be icy",
    above: "High MSNF — risk of sandy or gritty texture",
  },
  stabilizer: {
    in_range: "Good stability — won't melt too fast",
    below: "Low stabilizer — may melt quickly or be unstable",
    above: "High stabilizer — could feel gummy",
  },
  emulsifier: {
    in_range: "Good fat distribution throughout the mix",
    below: "Low emulsifier — fat may not incorporate evenly",
    above: "High emulsifier — double-check your quantities",
  },
  sweetness: {
    in_range: "Well-balanced sweetness level for this style",
    below: "Lower sweetness than target — may taste flat or less satisfying",
    above: "Higher sweetness than target — may taste cloying",
  },
  serving_temp: {
    in_range: "Good freeze — roughly 75% water frozen at serving temp",
    below: "High PAC mix — may not freeze hard enough at a typical serving temp",
    above: "Low PAC mix — may freeze too hard and be difficult to scoop",
  },
};

// ─── Status config ────────────────────────────────────────────────────────────

interface StatusConfig {
  badge: string;
  zoneBg: string;
  zoneBorder: string;
  marker: string;
  label: string;
}

const STATUS_CONFIG: Record<MetricStatus, StatusConfig> = {
  in_range: {
    badge: "badge-success",
    zoneBg: "bg-green-500/20 dark:bg-green-500/15",
    zoneBorder: "border-green-500/50",
    marker: "bg-green-600 dark:bg-green-400",
    label: "In Range",
  },
  below: {
    badge: "badge-warning",
    zoneBg: "bg-amber-500/20 dark:bg-amber-500/15",
    zoneBorder: "border-amber-500/50",
    marker: "bg-amber-500 dark:bg-amber-400",
    label: "Too Low",
  },
  above: {
    badge: "badge-error",
    zoneBg: "bg-red-500/20 dark:bg-red-500/15",
    zoneBorder: "border-red-500/50",
    marker: "bg-red-600 dark:bg-red-400",
    label: "Too High",
  },
};

// ─── Gauge bar ────────────────────────────────────────────────────────────────

interface GaugeBarProps {
  readonly value: number;
  readonly targetMin: number | null;
  readonly targetMax: number | null;
  readonly status: MetricStatus;
}

function GaugeBar({ value, targetMin, targetMax, status }: GaugeBarProps) {
  if (targetMin == null && targetMax == null) return null;
  const cfg = STATUS_CONFIG[status];

  // Build a scale that comfortably contains both the target zone and the current value.
  // The padding ensures neither the zone nor the marker sits right at the track edge.
  const allValues = [value, targetMin ?? value, targetMax ?? value];
  const lo = Math.min(...allValues);
  const hi = Math.max(...allValues);
  const span = Math.max(hi - lo, 1);
  const pad = span * 0.38 + 0.5;
  const scaleMin = lo - pad;
  const scaleMax = hi + pad;
  const scaleRange = scaleMax - scaleMin;

  const toPos = (v: number) => ((v - scaleMin) / scaleRange) * 100;

  const valuePos = toPos(value);
  const zoneLeft = toPos(targetMin ?? scaleMin);
  const zoneRight = toPos(targetMax ?? scaleMax);

  return (
    <div className="relative h-1.5 rounded-full bg-base-200 mt-2.5" aria-hidden="true">
      {/* Target zone */}
      <div
        className={`absolute inset-y-0 rounded-full border ${cfg.zoneBg} ${cfg.zoneBorder}`}
        style={{ left: `${zoneLeft}%`, width: `${zoneRight - zoneLeft}%` }}
      />
      {/* Current-value marker */}
      <div
        className={`absolute top-1/2 -translate-y-1/2 -translate-x-1/2 w-3 h-3 rounded-full border-2 border-base-100 shadow-sm ${cfg.marker}`}
        style={{ left: `${Math.max(2, Math.min(98, valuePos))}%` }}
      />
    </div>
  );
}

// ─── MetricCards ──────────────────────────────────────────────────────────────

interface MetricCardsProps {
  readonly comparisons: MetricComparison[] | null;
}

export function MetricCards({ comparisons }: MetricCardsProps) {
  if (!comparisons || comparisons.length === 0) return null;

  const inRangeCount = comparisons.filter((c) => c.status === "in_range").length;
  const total = comparisons.length;
  const issueCount = total - inRangeCount;

  let summaryCfg = { bg: "bg-green-50 dark:bg-green-900/20", text: "text-green-800 dark:text-green-300", dot: "bg-green-500" };
  if (issueCount > 0 && issueCount <= Math.ceil(total / 2)) {
    summaryCfg = { bg: "bg-amber-50 dark:bg-amber-900/20", text: "text-amber-800 dark:text-amber-300", dot: "bg-amber-500" };
  } else if (issueCount > Math.ceil(total / 2)) {
    summaryCfg = { bg: "bg-red-50 dark:bg-red-900/20", text: "text-red-800 dark:text-red-300", dot: "bg-red-500" };
  }

  let summaryText = "All metrics in range";
  if (issueCount === 1) summaryText = "1 metric needs attention";
  else if (issueCount > 1) summaryText = `${issueCount} metrics may need attention`;

  return (
    <div>
      {/* Summary banner */}
      <div className={`flex items-center gap-2.5 rounded-lg px-3 py-2 mb-4 ${summaryCfg.bg}`}>
        <span className={`w-2 h-2 rounded-full shrink-0 ${summaryCfg.dot}`} aria-hidden="true" />
        <span className={`text-sm font-medium ${summaryCfg.text}`}>{summaryText}</span>
        <span className="text-xs text-base-content/30 ml-auto tabular-nums">{inRangeCount}/{total}</span>
      </div>

      {/* Metric rows */}
      <div className="divide-y divide-base-200">
        {comparisons.map((c) => {
          const label = METRIC_LABELS[c.metric] ?? c.metric;
          const unit = METRIC_UNITS[c.metric] ?? "%";
          const cfg = STATUS_CONFIG[c.status];
          const hint = HINTS[c.metric]?.[c.status];

          let rangeStr = "";
          if (c.target_min != null && c.target_max != null) {
            rangeStr = `${c.target_min}–${c.target_max}${unit}`;
          } else if (c.target_max != null) {
            rangeStr = `≤ ${c.target_max}${unit}`;
          } else if (c.target_min != null) {
            rangeStr = `≥ ${c.target_min}${unit}`;
          }

          return (
            <div key={c.metric} className="py-3 first:pt-0 last:pb-0">
              {/* Header: label · badge · value */}
              <div className="flex items-center justify-between gap-3">
                <div className="flex items-center gap-1.5 min-w-0">
                  <span className="text-sm font-medium text-base-content/80 truncate">{label}</span>
                  <InfoIcon label={METRIC_TOOLTIPS[c.metric] ?? label} position="bottom" />
                </div>
                <div className="flex items-center gap-2 shrink-0">
                  <span className={`badge badge-sm ${cfg.badge}`}>{cfg.label}</span>
                  <span className="text-base font-bold tabular-nums leading-none">
                    {c.value.toFixed(1)}
                    <span className="text-xs font-normal text-base-content/50 ml-0.5">{unit}</span>
                  </span>
                </div>
              </div>

              {/* Gauge */}
              <GaugeBar value={c.value} targetMin={c.target_min} targetMax={c.target_max} status={c.status} />

              {/* Hint + target range */}
              {(hint ?? rangeStr) && (
                <div className="flex items-start justify-between gap-4 mt-1.5">
                  {hint && <p className="text-xs text-base-content/50 leading-snug">{hint}</p>}
                  {rangeStr && <p className="text-xs text-base-content/50 shrink-0">target {rangeStr}</p>}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
