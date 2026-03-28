import { Save, Trash2 } from "lucide-react";
import type { CalculateResponse, TargetProfile } from "../types";
import { Tooltip } from "./Tooltip";
import { TOOLTIPS } from "../lib/tooltips";
import { InfoIcon } from "./InfoIcon";

interface StatusPill {
  label: string;
  value: string;
  tone: string;
}

function getBalancePill(result: CalculateResponse | null): StatusPill {
  const comparisons = result?.target_comparison;
  if (!comparisons || comparisons.length === 0) {
    return {
      label: "Balance",
      value: "No target",
      tone: "bg-base-200 text-base-content/70",
    };
  }

  const issueCount = comparisons.filter((comparison) => comparison.status !== "in_range").length;
  if (issueCount === 0) {
    return {
      label: "Balance",
      value: "On target",
      tone: "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300",
    };
  }

  if (issueCount <= 2) {
    return {
      label: "Balance",
      value: `${issueCount} issue${issueCount === 1 ? "" : "s"}`,
      tone: "bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-300",
    };
  }

  return {
    label: "Balance",
    value: `${issueCount} issues`,
    tone: "bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300",
  };
}

function getFreezePill(result: CalculateResponse | null, targetProfile: TargetProfile | null): StatusPill {
  const servingTemp = result?.freezing.serving_temperature_c;
  if (servingTemp == null) {
    return {
      label: "Scoopability",
      value: "No data",
      tone: "bg-base-200 text-base-content/70",
    };
  }

  if (
    targetProfile?.serving_temp_min != null &&
    targetProfile.serving_temp_max != null
  ) {
    if (servingTemp < targetProfile.serving_temp_min) {
      return {
        label: "Scoopability",
        value: "Softer than target",
        tone: "bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-300",
      };
    }
    if (servingTemp > targetProfile.serving_temp_max) {
      return {
        label: "Scoopability",
        value: "Harder than target",
        tone: "bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300",
      };
    }
    return {
      label: "Scoopability",
      value: "In serving range",
      tone: "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300",
    };
  }

  if (servingTemp >= -8) {
    return {
      label: "Scoopability",
      value: "Very firm",
      tone: "bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300",
    };
  }
  if (servingTemp >= -11) {
    return {
      label: "Scoopability",
      value: "Firm",
      tone: "bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-300",
    };
  }
  if (servingTemp >= -14) {
    return {
      label: "Scoopability",
      value: "Balanced",
      tone: "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300",
    };
  }
  if (servingTemp >= -17) {
    return {
      label: "Scoopability",
      value: "Soft",
      tone: "bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-300",
    };
  }
  return {
    label: "Scoopability",
    value: "Very soft",
    tone: "bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300",
  };
}

function getSweetnessPill(result: CalculateResponse | null, targetProfile: TargetProfile | null): StatusPill {
  const pod = result?.sweetness.pod;
  if (pod == null) {
    return {
      label: "Sweetness",
      value: "No data",
      tone: "bg-base-200 text-base-content/70",
    };
  }

  if (targetProfile?.sweetness_min != null && targetProfile.sweetness_max != null) {
    if (pod < targetProfile.sweetness_min) {
      return {
        label: "Sweetness",
        value: "Below target",
        tone: "bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-300",
      };
    }
    if (pod > targetProfile.sweetness_max) {
      return {
        label: "Sweetness",
        value: "Above target",
        tone: "bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300",
      };
    }
    return {
      label: "Sweetness",
      value: "On target",
      tone: "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300",
    };
  }

  if (pod < 14) {
    return {
      label: "Sweetness",
      value: "Restrained",
      tone: "bg-sky-100 text-sky-800 dark:bg-sky-900/30 dark:text-sky-300",
    };
  }
  if (pod <= 18) {
    return {
      label: "Sweetness",
      value: "Balanced",
      tone: "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300",
    };
  }
  return {
    label: "Sweetness",
    value: "Sweet-forward",
    tone: "bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-300",
  };
}

interface RecipeHeaderProps {
  readonly recipeName: string | null;
  readonly targetProfile: TargetProfile | null;
  readonly profiles?: TargetProfile[];
  readonly result: CalculateResponse | null;
  readonly isSaving: boolean;
  readonly hasIngredients: boolean;
  readonly hasUnsavedChanges: boolean;
  readonly onSaveRecipe: () => void;
  readonly onDeleteRecipe: () => void;
  readonly onChangeProfile: (profile: TargetProfile | null) => void;
}

export function RecipeHeader({
  recipeName,
  targetProfile,
  profiles,
  result,
  isSaving,
  hasIngredients,
  hasUnsavedChanges,
  onSaveRecipe,
  onDeleteRecipe,
  onChangeProfile,
}: RecipeHeaderProps) {
  const summaryPills = [
    getBalancePill(result),
    getFreezePill(result, targetProfile),
    getSweetnessPill(result, targetProfile),
  ];

  return (
    <div className="bg-linear-to-r from-pink-50 to-pink-50/50 dark:from-pink-900/20 dark:to-pink-900/10 rounded-xl border border-pink-200 dark:border-pink-800/30 p-4 mb-0">
      <div className="max-w-7xl mx-auto">
        {/* Title and action buttons in single row */}
        <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
          <div className="flex-1 min-w-0">
            <h1 className="text-2xl sm:text-3xl font-bold text-base-content mb-1">
              {recipeName ? (
                <span>{recipeName}</span>
              ) : (
                <span className="text-base-content/40 italic">Unsaved recipe</span>
              )}
            </h1>
            {/* Compact summary line */}
            <div className="flex items-center gap-3 text-sm text-base-content/60 flex-wrap">
              {targetProfile ? (
                <span>
                  Profile: <span className="font-semibold text-base-content/80">{targetProfile.name}</span>
                </span>
              ) : null}
              {result?.composition.total_weight_g ? (
                <span>
                  Weight: <span className="font-semibold text-base-content/80">{result.composition.total_weight_g.toFixed(0)}g</span>
                </span>
              ) : null}
              {result?.nutrition.per_100g.energy_kj ? (
                <span>
                  Energy: <span className="font-semibold text-base-content/80">{result.nutrition.per_100g.energy_kj.toFixed(0)}kJ</span>
                </span>
              ) : null}
            </div>

            <div className="mt-3 flex flex-wrap gap-2">
              {summaryPills.map((pill) => (
                <div
                  key={pill.label}
                  className={`rounded-full px-3 py-1.5 text-xs font-medium ${pill.tone}`}
                >
                  <span className="opacity-70">{pill.label}:</span>{" "}
                  <span>{pill.value}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Action buttons */}
          <div className="flex flex-col items-start gap-3 lg:items-end">
            <div className="flex items-center gap-2 self-start lg:self-end">
              <label htmlFor="profile-select" className="text-xs text-base-content/55 flex items-center gap-1">
                Profile
                <InfoIcon label={TOOLTIPS.profile} position="bottom" />
              </label>
              <select
                id="profile-select"
                value={targetProfile?.id ?? ""}
                onChange={(e) => {
                  const id = e.target.value;
                  const profile = profiles?.find((item) => item.id === id) ?? null;
                  onChangeProfile(profile);
                }}
                className="select select-sm min-w-48"
              >
                <option value="">None</option>
                {profiles?.map((profile) => (
                  <option key={profile.id} value={profile.id}>
                    {profile.name}
                  </option>
                ))}
              </select>
            </div>

            <div className="flex items-center gap-2 flex-wrap">
            <Tooltip content={TOOLTIPS.saveRecipe}>
              <button
                type="button"
                className="btn btn-sm btn-primary gap-1 disabled:bg-pink-100 disabled:border-pink-100 disabled:text-pink-300 dark:disabled:bg-pink-900/30 dark:disabled:border-pink-900/30 dark:disabled:text-pink-700"
                onClick={onSaveRecipe}
                disabled={isSaving || (!recipeName && !hasIngredients) || (!!recipeName && !hasUnsavedChanges)}
              >
                <Save size={16} />
                {recipeName ? "Update" : "Save"}
              </button>
            </Tooltip>
            {recipeName && (
              <Tooltip content={TOOLTIPS.deleteRecipe}>
                <button
                  type="button"
                  className="btn btn-sm btn-error btn-outline gap-1"
                  onClick={onDeleteRecipe}
                  disabled={isSaving}
                >
                  <Trash2 size={16} />
                  Delete
                </button>
              </Tooltip>
            )}
          </div>
        </div>
      </div>
    </div>
            </div>
  );
}
