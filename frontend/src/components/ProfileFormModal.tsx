import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { Trash2, X } from "lucide-react";
import { createProfile, updateProfile } from "../api";
import { TargetProfileInputSchema, type TargetProfile, type TargetProfileInput } from "../types";
import { useToast } from "../hooks/useToast";
import { fieldErrors, type FieldErrors } from "../lib/validation";

interface Props {
  open: boolean;
  profile: TargetProfile | null;
  onClose: () => void;
}

type FormFields = {
  name: string;
  serving_temp_min: string;
  serving_temp_max: string;
  sweetness_min: string;
  sweetness_max: string;
  total_solids_min: string;
  total_solids_max: string;
  total_fat_min: string;
  total_fat_max: string;
  milk_fat_min: string;
  milk_fat_max: string;
  sugar_min: string;
  sugar_max: string;
  alcohol_min: string;
  alcohol_max: string;
  msnf_min: string;
  msnf_max: string;
  stabilizer_min: string;
  stabilizer_max: string;
  emulsifier_min: string;
  emulsifier_max: string;
};

const EMPTY: FormFields = {
  name: "",
  serving_temp_min: "",
  serving_temp_max: "",
  sweetness_min: "",
  sweetness_max: "",
  total_solids_min: "",
  total_solids_max: "",
  total_fat_min: "",
  total_fat_max: "",
  milk_fat_min: "",
  milk_fat_max: "",
  sugar_min: "",
  sugar_max: "",
  alcohol_min: "",
  alcohol_max: "",
  msnf_min: "",
  msnf_max: "",
  stabilizer_min: "",
  stabilizer_max: "",
  emulsifier_min: "",
  emulsifier_max: "",
};

function toForm(p: TargetProfile): FormFields {
  const s = (v: number | null | undefined) => (v == null ? "" : String(v));
  return {
    name: p.name,
    serving_temp_min: s(p.serving_temp_min),
    serving_temp_max: s(p.serving_temp_max),
    sweetness_min: s(p.sweetness_min),
    sweetness_max: s(p.sweetness_max),
    total_solids_min: s(p.total_solids_min),
    total_solids_max: s(p.total_solids_max),
    total_fat_min: s(p.total_fat_min),
    total_fat_max: s(p.total_fat_max),
    milk_fat_min: s(p.milk_fat_min),
    milk_fat_max: s(p.milk_fat_max),
    sugar_min: s(p.sugar_min),
    sugar_max: s(p.sugar_max),
    alcohol_min: s(p.alcohol_min),
    alcohol_max: s(p.alcohol_max),
    msnf_min: s(p.msnf_min),
    msnf_max: s(p.msnf_max),
    stabilizer_min: s(p.stabilizer_min),
    stabilizer_max: s(p.stabilizer_max),
    emulsifier_min: s(p.emulsifier_min),
    emulsifier_max: s(p.emulsifier_max),
  };
}

interface TargetCardProps {
  readonly label: string;
  readonly unit: string;
  readonly minValue: string;
  readonly maxValue: string;
  readonly onMinChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  readonly onMaxChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  readonly onDelete: () => void;
  readonly minError?: string;
  readonly maxError?: string;
}

function TargetCard({
  label,
  unit,
  minValue,
  maxValue,
  onMinChange,
  onMaxChange,
  onDelete,
  minError,
  maxError,
}: Readonly<TargetCardProps>) {
  return (
    <div className="border border-base-200 rounded-lg p-4 bg-base-50 hover:bg-base-100 transition-colors space-y-3">
      <div className="flex items-center justify-between">
        <h4 className="font-medium text-sm text-base-content">{label}</h4>
        <button
          type="button"
          onClick={onDelete}
          className="btn btn-ghost btn-xs btn-circle text-base-content/60 hover:text-error"
          aria-label={`Delete ${label}`}
        >
          <Trash2 size={14} />
        </button>
      </div>

      <div className="flex items-center gap-2">
        {/* Min input */}
        <div className="flex-1">
          <div className="flex items-center gap-1">
            <input
              type="number"
              step="any"
              aria-label={`${label} min`}
              placeholder="0"
              className={`input input-sm input-bordered w-full${minError ? " input-error" : ""}`}
              value={minValue}
              onChange={onMinChange}
            />
            <span className="text-xs text-base-content/60 w-5">{unit}</span>
          </div>
        </div>

        {/* Dash separator */}
        <span className="text-base-content/40 text-xs shrink-0">–</span>

        {/* Max input */}
        <div className="flex-1">
          <div className="flex items-center gap-1">
            <input
              type="number"
              step="any"
              aria-label={`${label} max`}
              placeholder="0"
              className={`input input-sm input-bordered w-full${maxError ? " input-error" : ""}`}
              value={maxValue}
              onChange={onMaxChange}
            />
            <span className="text-xs text-base-content/60 w-5">{unit}</span>
          </div>
        </div>
      </div>

      {(minError || maxError) && (
        <p className="label-text-alt text-error text-xs">{minError ?? maxError}</p>
      )}
    </div>
  );
}

export function ProfileFormModal({ open, profile, onClose }: Readonly<Props>) {
  const [form, setForm] = useState<FormFields>(() =>
    profile ? toForm(profile) : EMPTY
  );
  const [errors, setErrors] = useState<FieldErrors>({});
  const qc = useQueryClient();
  const { addToast } = useToast();
  const isEdit = profile != null;

  function numChange(key: keyof FormFields) {
    return (e: React.ChangeEvent<HTMLInputElement>) => {
      setErrors((prev) => {
        const next = { ...prev };
        delete next[key];
        return next;
      });
      setForm((prev) => ({ ...prev, [key]: e.target.value }));
    };
  }

  function handleClearTargets() {
    setForm((prev) => ({
      ...prev,
      serving_temp_min: "",
      serving_temp_max: "",
      sweetness_min: "",
      sweetness_max: "",
      total_solids_min: "",
      total_solids_max: "",
      total_fat_min: "",
      total_fat_max: "",
      milk_fat_min: "",
      milk_fat_max: "",
      sugar_min: "",
      sugar_max: "",
      alcohol_min: "",
      alcohol_max: "",
      msnf_min: "",
      msnf_max: "",
      stabilizer_min: "",
      stabilizer_max: "",
      emulsifier_min: "",
      emulsifier_max: "",
    }));
    setErrors({});
  }

  function handleResetTargets() {
    if (profile) {
      setForm(toForm(profile));
      setErrors({});
    }
  }

  const mutation = useMutation({
    mutationFn: (payload: TargetProfileInput) =>
      isEdit ? updateProfile(profile.id, payload) : createProfile(payload),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["profiles"] });
      addToast(isEdit ? "Profile updated." : "Profile created.", "success");
      onClose();
    },
    onError: (err: Error) => {
      addToast(err.message, "error");
    },
  });

  function handleSubmit(e: React.SyntheticEvent) {
    e.preventDefault();
    const result = TargetProfileInputSchema.safeParse(form);
    if (!result.success) {
      setErrors(fieldErrors(result.error));
      return;
    }
    setErrors({});
    mutation.mutate(result.data);
  }

  return (
    <dialog className="modal modal-bottom sm:modal-middle" open={open}>
      <div className="modal-box max-w-2xl max-h-[90vh] flex flex-col p-0 overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-base-200 shrink-0">
          <div>
            <h3 className="font-bold text-lg">
              Create a new target profile
            </h3>
            <p className="text-xs text-base-content/60 mt-1">
              Define a set of target values for your recipes.
            </p>
          </div>
          <button
            type="button"
            className="btn btn-ghost btn-sm btn-circle"
            onClick={onClose}
            aria-label="Close"
          >
            <X size={16} />
          </button>
        </div>

        {/* Scrollable form body */}
        <form
          id="profile-form"
          onSubmit={handleSubmit}
          className="overflow-y-auto overflow-x-hidden flex-1 px-6 py-4 space-y-5"
        >
          {/* Name */}
          <section className="space-y-2">
            <label htmlFor="profile-name" className="text-sm font-medium text-base-content">
              Name
            </label>
            <input
              id="profile-name"
              type="text"
              required
              aria-label="Profile name"
              className={`input input-sm input-bordered w-full${errors.name ? " input-error" : ""}`}
              value={form.name}
              onChange={(e) => {
                setErrors((prev) => {
                  const next = { ...prev };
                  delete next.name;
                  return next;
                });
                setForm((prev) => ({ ...prev, name: e.target.value }));
              }}
              placeholder="e.g. Sorbet (Copy)"
            />
            {errors.name && (
              <p className="text-xs text-error mt-1">{errors.name}</p>
            )}
          </section>

          {/* Targets section */}
          <section className="space-y-3">
            <div className="flex items-center justify-between">
              <h4 className="text-sm font-medium text-base-content">Targets</h4>
              <div className="flex gap-2">
                <button
                  type="button"
                  onClick={handleClearTargets}
                  className="btn btn-ghost btn-xs text-base-content/70 hover:text-base-content"
                >
                  Clear
                </button>
                <button
                  type="button"
                  onClick={handleResetTargets}
                  className="btn btn-ghost btn-xs text-base-content/70 hover:text-base-content"
                  disabled={!isEdit}
                >
                  Reset
                </button>
              </div>
            </div>

            {/* Targets grid - 2 columns */}
            <div className="grid grid-cols-2 gap-4">
              {/* Row 1 */}
              <TargetCard
                label="Sugars"
                unit="%"
                minValue={form.sugar_min}
                maxValue={form.sugar_max}
                onMinChange={numChange("sugar_min")}
                onMaxChange={numChange("sugar_max")}
                onDelete={() => {
                  setForm((prev) => ({
                    ...prev,
                    sugar_min: "",
                    sugar_max: "",
                  }));
                }}
                minError={errors.sugar_min}
                maxError={errors.sugar_max}
              />
              <TargetCard
                label="Relative sweetness"
                unit="%"
                minValue={form.sweetness_min}
                maxValue={form.sweetness_max}
                onMinChange={numChange("sweetness_min")}
                onMaxChange={numChange("sweetness_max")}
                onDelete={() => {
                  setForm((prev) => ({
                    ...prev,
                    sweetness_min: "",
                    sweetness_max: "",
                  }));
                }}
                minError={errors.sweetness_min}
                maxError={errors.sweetness_max}
              />

              {/* Row 2 */}
              <TargetCard
                label="Milk fat"
                unit="%"
                minValue={form.milk_fat_min}
                maxValue={form.milk_fat_max}
                onMinChange={numChange("milk_fat_min")}
                onMaxChange={numChange("milk_fat_max")}
                onDelete={() => {
                  setForm((prev) => ({
                    ...prev,
                    milk_fat_min: "",
                    milk_fat_max: "",
                  }));
                }}
                minError={errors.milk_fat_min}
                maxError={errors.milk_fat_max}
              />
              <TargetCard
                label="MSNF"
                unit="%"
                minValue={form.msnf_min}
                maxValue={form.msnf_max}
                onMinChange={numChange("msnf_min")}
                onMaxChange={numChange("msnf_max")}
                onDelete={() => {
                  setForm((prev) => ({
                    ...prev,
                    msnf_min: "",
                    msnf_max: "",
                  }));
                }}
                minError={errors.msnf_min}
                maxError={errors.msnf_max}
              />

              {/* Row 3 */}
              <TargetCard
                label="Stabilizers"
                unit="%"
                minValue={form.stabilizer_min}
                maxValue={form.stabilizer_max}
                onMinChange={numChange("stabilizer_min")}
                onMaxChange={numChange("stabilizer_max")}
                onDelete={() => {
                  setForm((prev) => ({
                    ...prev,
                    stabilizer_min: "",
                    stabilizer_max: "",
                  }));
                }}
                minError={errors.stabilizer_min}
                maxError={errors.stabilizer_max}
              />
              <TargetCard
                label="Emulsifiers"
                unit="%"
                minValue={form.emulsifier_min}
                maxValue={form.emulsifier_max}
                onMinChange={numChange("emulsifier_min")}
                onMaxChange={numChange("emulsifier_max")}
                onDelete={() => {
                  setForm((prev) => ({
                    ...prev,
                    emulsifier_min: "",
                    emulsifier_max: "",
                  }));
                }}
                minError={errors.emulsifier_min}
                maxError={errors.emulsifier_max}
              />

              {/* Row 4 */}
              <TargetCard
                label="Serving temperature"
                unit="°C"
                minValue={form.serving_temp_min}
                maxValue={form.serving_temp_max}
                onMinChange={numChange("serving_temp_min")}
                onMaxChange={numChange("serving_temp_max")}
                onDelete={() => {
                  setForm((prev) => ({
                    ...prev,
                    serving_temp_min: "",
                    serving_temp_max: "",
                  }));
                }}
                minError={errors.serving_temp_min}
                maxError={errors.serving_temp_max}
              />
              <TargetCard
                label="Total solids"
                unit="%"
                minValue={form.total_solids_min}
                maxValue={form.total_solids_max}
                onMinChange={numChange("total_solids_min")}
                onMaxChange={numChange("total_solids_max")}
                onDelete={() => {
                  setForm((prev) => ({
                    ...prev,
                    total_solids_min: "",
                    total_solids_max: "",
                  }));
                }}
                minError={errors.total_solids_min}
                maxError={errors.total_solids_max}
              />

              {/* Row 5 */}
              <TargetCard
                label="Total fat"
                unit="%"
                minValue={form.total_fat_min}
                maxValue={form.total_fat_max}
                onMinChange={numChange("total_fat_min")}
                onMaxChange={numChange("total_fat_max")}
                onDelete={() => {
                  setForm((prev) => ({
                    ...prev,
                    total_fat_min: "",
                    total_fat_max: "",
                  }));
                }}
                minError={errors.total_fat_min}
                maxError={errors.total_fat_max}
              />
              <TargetCard
                label="Alcohol"
                unit="%"
                minValue={form.alcohol_min}
                maxValue={form.alcohol_max}
                onMinChange={numChange("alcohol_min")}
                onMaxChange={numChange("alcohol_max")}
                onDelete={() => {
                  setForm((prev) => ({
                    ...prev,
                    alcohol_min: "",
                    alcohol_max: "",
                  }));
                }}
                minError={errors.alcohol_min}
                maxError={errors.alcohol_max}
              />
            </div>
          </section>
        </form>

        {/* Footer */}
        <div className="flex justify-end gap-2 px-6 py-4 border-t border-base-200 shrink-0">
          <button type="button" className="btn btn-ghost btn-sm" onClick={onClose}>
            Cancel
          </button>
          <button
            type="submit"
            form="profile-form"
            className="btn btn-primary btn-sm"
            disabled={mutation.isPending}
          >
            {mutation.isPending && (
              <span className="loading loading-spinner loading-xs" />
            )}
            Save
          </button>
        </div>
      </div>
      <form method="dialog" className="modal-backdrop">
        <button onClick={onClose}>close</button>
      </form>
    </dialog>
  );
}
