import { useState } from "react";
import { useMutation, useQueryClient, useQuery } from "@tanstack/react-query";
import { X } from "lucide-react";
import { createIngredient, updateIngredient, fetchCategories } from "../api";
import { IngredientInputSchema, type Ingredient, type IngredientInput } from "../types";
import { useToast } from "../hooks/useToast";
import { fieldErrors, type FieldErrors } from "../lib/validation";
import { InfoIcon } from "./InfoIcon";
import { TOOLTIPS } from "../lib/tooltips";

interface Props {
  open: boolean;
  ingredient: Ingredient | null;
  onClose: () => void;
}

type FormFields = {
  name: string;
  description: string;
  category_id: string;
  energy_kj_per_100g: string;
  water_pct: string;
  protein_pct: string;
  total_fat_pct: string;
  saturated_fat_pct: string;
  trans_fat_pct: string;
  carbohydrate_pct: string;
  fiber_pct: string;
  total_sugar_pct: string;
  alcohol_pct: string;
  sodium_mg: string;
  sucrose_pct: string;
  glucose_pct: string;
  fructose_pct: string;
  lactose_pct: string;
  maltose_pct: string;
  galactose_pct: string;
  milk_fat_pct: string;
  msnf_pct: string;
  cocoa_butter_pct: string;
  cocoa_solids_pct: string;
  stabilizer_pct: string;
  emulsifier_pct: string;
  pac_override: string;
  pod_override: string;
  aliases: string;
};

const EMPTY: FormFields = {
  name: "",
  description: "",
  category_id: "",
  energy_kj_per_100g: "",
  water_pct: "",
  protein_pct: "",
  total_fat_pct: "",
  saturated_fat_pct: "",
  trans_fat_pct: "",
  carbohydrate_pct: "",
  fiber_pct: "",
  total_sugar_pct: "",
  alcohol_pct: "",
  sodium_mg: "",
  sucrose_pct: "",
  glucose_pct: "",
  fructose_pct: "",
  lactose_pct: "",
  maltose_pct: "",
  galactose_pct: "",
  milk_fat_pct: "",
  msnf_pct: "",
  cocoa_butter_pct: "",
  cocoa_solids_pct: "",
  stabilizer_pct: "",
  emulsifier_pct: "",
  pac_override: "",
  pod_override: "",
  aliases: "",
};

function toForm(ing: Ingredient): FormFields {
  const s = (v: number | null | undefined) => (v == null ? "" : String(v));
  return {
    name: ing.name,
    description: ing.description ?? "",
    category_id: ing.category?.id == null ? "" : String(ing.category.id),
    energy_kj_per_100g: s(ing.energy_kj_per_100g),
    water_pct: s(ing.water_pct),
    protein_pct: s(ing.protein_pct),
    total_fat_pct: s(ing.total_fat_pct),
    saturated_fat_pct: s(ing.saturated_fat_pct),
    trans_fat_pct: s(ing.trans_fat_pct),
    carbohydrate_pct: s(ing.carbohydrate_pct),
    fiber_pct: s(ing.fiber_pct),
    total_sugar_pct: s(ing.total_sugar_pct),
    alcohol_pct: s(ing.alcohol_pct),
    sodium_mg: s(ing.sodium_mg),
    sucrose_pct: s(ing.sucrose_pct),
    glucose_pct: s(ing.glucose_pct),
    fructose_pct: s(ing.fructose_pct),
    lactose_pct: s(ing.lactose_pct),
    maltose_pct: s(ing.maltose_pct),
    galactose_pct: s(ing.galactose_pct),
    milk_fat_pct: s(ing.milk_fat_pct),
    msnf_pct: s(ing.msnf_pct),
    cocoa_butter_pct: s(ing.cocoa_butter_pct),
    cocoa_solids_pct: s(ing.cocoa_solids_pct),
    stabilizer_pct: s(ing.stabilizer_pct),
    emulsifier_pct: s(ing.emulsifier_pct),
    pac_override: s(ing.pac_override),
    pod_override: s(ing.pod_override),
    aliases: ing.aliases.join(", "),
  };
}

interface NumFieldProps {
  readonly label: string;
  readonly unit: string;
  readonly value: string;
  readonly onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  readonly error?: string;
  readonly tooltip?: string;
}

function NumField({ label, unit, value, onChange, error, tooltip }: Readonly<NumFieldProps>) {
  return (
    <label className="form-control">
      <div className="label py-1">
        <div className="flex items-center gap-1">
          <span className="label-text text-xs text-base-content/60">{label}</span>
          {tooltip && <InfoIcon label={tooltip} position="right" />}
        </div>
      </div>
      {unit ? (
        <div className="join">
          <input
            type="number"
            step="any"
            aria-label={label}
            className={`input input-sm input-bordered join-item w-full${error ? " input-error" : ""}`}
            value={value}
            onChange={onChange}
          />
          <span className="join-item px-2 flex items-center bg-base-200 border border-l-0 border-base-300 text-xs rounded-r-btn">
            {unit}
          </span>
        </div>
      ) : (
        <input
          type="number"
          step="any"
          aria-label={label}
          className={`input input-sm input-bordered w-full${error ? " input-error" : ""}`}
          value={value}
          onChange={onChange}
        />
      )}
      {error && <p className="label-text-alt text-error mt-0.5">{error}</p>}
    </label>
  );
}

export function IngredientFormModal({ open, ingredient, onClose }: Readonly<Props>) {
  const [form, setForm] = useState<FormFields>(() =>
    ingredient ? toForm(ingredient) : EMPTY
  );
  const [errors, setErrors] = useState<FieldErrors>({});
  const qc = useQueryClient();
  const { addToast } = useToast();
  const isEdit = ingredient != null;

  const { data: categories } = useQuery({
    queryKey: ["categories"],
    queryFn: fetchCategories,
  });

  function textChange(key: keyof FormFields) {
    return (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
      setErrors((prev) => { const next = { ...prev }; delete next[key]; return next; });
      setForm((prev) => ({ ...prev, [key]: e.target.value }));
    };
  }

  function numChange(key: keyof FormFields) {
    return (e: React.ChangeEvent<HTMLInputElement>) => {
      setErrors((prev) => { const next = { ...prev }; delete next[key]; return next; });
      setForm((prev) => ({ ...prev, [key]: e.target.value }));
    };
  }

  const mutation = useMutation({
    mutationFn: (payload: IngredientInput) =>
      isEdit
        ? updateIngredient(ingredient.id, payload)
        : createIngredient(payload),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["ingredients"] });
      addToast(isEdit ? "Ingredient updated." : "Ingredient created.", "success");
      onClose();
    },
    onError: (err: Error) => {
      addToast(err.message, "error");
    },
  });

  function handleSubmit(e: React.SyntheticEvent) {
    e.preventDefault();
    const result = IngredientInputSchema.safeParse(form);
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
          <h3 className="font-bold text-lg">
            {isEdit ? "Edit Ingredient" : "Add Ingredient"}
          </h3>
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
          id="ingredient-form"
          onSubmit={handleSubmit}
          className="overflow-y-auto overflow-x-hidden flex-1 px-6 py-4 space-y-5"
        >
          {/* Basics */}
          <section className="space-y-3">
            <h4 className="text-xs font-semibold text-base-content/50 uppercase tracking-wider">
              Basics
            </h4>
            <label className="form-control">
              <div className="label pb-0.5">
                <span className="label-text text-xs">
                  Name <span className="text-error">*</span>
                </span>
              </div>
              <input
                type="text"
                required
                aria-label="Name"
                className={`input input-sm input-bordered w-full${errors.name ? " input-error" : ""}`}
                value={form.name}
                onChange={textChange("name")}
                placeholder="e.g. Heavy cream"
              />
              {errors.name && (
                <p className="label-text-alt text-error mt-0.5">{errors.name}</p>
              )}
            </label>
            <label className="form-control">
              <div className="label pb-0.5">
                <span className="label-text text-xs">Description</span>
              </div>
              <input
                type="text"
                aria-label="Description"
                className="input input-sm input-bordered w-full"
                value={form.description}
                onChange={textChange("description")}
              />
            </label>
            <div className="grid grid-cols-2 gap-3">
              <label className="form-control">
                <div className="label py-1">
                  <span className="label-text text-xs">Category</span>
                </div>
                <select
                  className="select select-sm select-bordered w-full"
                  value={form.category_id}
                  onChange={textChange("category_id")}
                >
                  <option value="">— None —</option>
                  {categories?.map((c) => (
                    <option key={c.id} value={c.id}>
                      {c.name}
                    </option>
                  ))}
                </select>
              </label>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <NumField
                label="Stabilizer"
                unit="g"
                value={form.stabilizer_pct}
                onChange={numChange("stabilizer_pct")}
                error={errors.stabilizer_pct}
                tooltip={TOOLTIPS.stabilizer}
              />
              <NumField
                label="Emulsifier"
                unit="g"
                value={form.emulsifier_pct}
                onChange={numChange("emulsifier_pct")}
                error={errors.emulsifier_pct}
                tooltip={TOOLTIPS.emulsifier}
              />
            </div>
            <label className="form-control">
              <div className="label pb-0.5">
                <span className="label-text text-xs">
                  Aliases{" "}
                  <span className="text-base-content/40">(comma-separated)</span>
                </span>
              </div>
              <input
                type="text"
                aria-label="Aliases"
                className="input input-sm input-bordered w-full"
                value={form.aliases}
                onChange={textChange("aliases")}
                placeholder="e.g. Whipping cream, Thickened cream"
              />
            </label>
          </section>

          <div className="divider my-0" />

          {/* Composition */}
          <section className="space-y-3">
            <h4 className="text-xs font-semibold text-base-content/50 uppercase tracking-wider">
              Composition per 100g
            </h4>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
              <NumField
                label="Energy"
                unit="kJ"
                value={form.energy_kj_per_100g}
                onChange={numChange("energy_kj_per_100g")}
                error={errors.energy_kj_per_100g}
              />
              <NumField
                label="Water"
                unit="g"
                value={form.water_pct}
                onChange={numChange("water_pct")}
                error={errors.water_pct}
              />
              <NumField
                label="Protein"
                unit="g"
                value={form.protein_pct}
                onChange={numChange("protein_pct")}
                error={errors.protein_pct}
              />
              <NumField
                label="Total Fat"
                unit="g"
                value={form.total_fat_pct}
                onChange={numChange("total_fat_pct")}
                error={errors.total_fat_pct}
              />
              <NumField
                label="Saturated Fat"
                unit="g"
                value={form.saturated_fat_pct}
                onChange={numChange("saturated_fat_pct")}
                error={errors.saturated_fat_pct}
              />
              <NumField
                label="Trans Fat"
                unit="g"
                value={form.trans_fat_pct}
                onChange={numChange("trans_fat_pct")}
                error={errors.trans_fat_pct}
              />
              <NumField
                label="Carbohydrates"
                unit="g"
                value={form.carbohydrate_pct}
                onChange={numChange("carbohydrate_pct")}
                error={errors.carbohydrate_pct}
              />
              <NumField
                label="Fiber"
                unit="g"
                value={form.fiber_pct}
                onChange={numChange("fiber_pct")}
                error={errors.fiber_pct}
              />
              <NumField
                label="Total Sugar"
                unit="g"
                value={form.total_sugar_pct}
                onChange={numChange("total_sugar_pct")}
                error={errors.total_sugar_pct}
              />
              <NumField
                label="Alcohol"
                unit="g"
                value={form.alcohol_pct}
                onChange={numChange("alcohol_pct")}
                error={errors.alcohol_pct}
              />
              <NumField
                label="Sodium"
                unit="mg"
                value={form.sodium_mg}
                onChange={numChange("sodium_mg")}
                error={errors.sodium_mg}
              />
            </div>
          </section>

          <div className="divider my-0" />

          {/* Sugar breakdown */}
          <section className="space-y-3">
            <h4 className="text-xs font-semibold text-base-content/50 uppercase tracking-wider">
              Sugar Breakdown
            </h4>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
              <NumField
                label="Sucrose"
                unit="g"
                value={form.sucrose_pct}
                onChange={numChange("sucrose_pct")}
                error={errors.sucrose_pct}
              />
              <NumField
                label="Glucose"
                unit="g"
                value={form.glucose_pct}
                onChange={numChange("glucose_pct")}
                error={errors.glucose_pct}
              />
              <NumField
                label="Fructose"
                unit="g"
                value={form.fructose_pct}
                onChange={numChange("fructose_pct")}
                error={errors.fructose_pct}
              />
              <NumField
                label="Lactose"
                unit="g"
                value={form.lactose_pct}
                onChange={numChange("lactose_pct")}
                error={errors.lactose_pct}
              />
              <NumField
                label="Maltose"
                unit="g"
                value={form.maltose_pct}
                onChange={numChange("maltose_pct")}
                error={errors.maltose_pct}
              />
              <NumField
                label="Galactose"
                unit="g"
                value={form.galactose_pct}
                onChange={numChange("galactose_pct")}
                error={errors.galactose_pct}
              />
            </div>
          </section>

          <div className="divider my-0" />

          {/* Dairy / Chocolate */}
          <section className="space-y-3">
            <h4 className="text-xs font-semibold text-base-content/50 uppercase tracking-wider">
              Dairy / Chocolate
            </h4>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              <NumField
                label="Milk Fat"
                unit="g"
                value={form.milk_fat_pct}
                onChange={numChange("milk_fat_pct")}
                error={errors.milk_fat_pct}
              />
              <NumField
                label="MSNF"
                unit="g"
                value={form.msnf_pct}
                onChange={numChange("msnf_pct")}
                error={errors.msnf_pct}
              />
              <NumField
                label="Cocoa Butter"
                unit="g"
                value={form.cocoa_butter_pct}
                onChange={numChange("cocoa_butter_pct")}
                error={errors.cocoa_butter_pct}
              />
              <NumField
                label="Cocoa Solids"
                unit="g"
                value={form.cocoa_solids_pct}
                onChange={numChange("cocoa_solids_pct")}
                error={errors.cocoa_solids_pct}
              />
            </div>
          </section>

          <div className="divider my-0" />

          {/* Overrides */}
          <section className="space-y-3">
            <h4 className="text-xs font-semibold text-base-content/50 uppercase tracking-wider">
              Overrides
            </h4>
            <p className="text-xs text-base-content/40">
              Leave blank to use calculated values.
            </p>
            <div className="grid grid-cols-2 gap-3">
              <NumField
                label="PAC override"
                unit=""
                value={form.pac_override}
                onChange={numChange("pac_override")}
                error={errors.pac_override}
                tooltip={TOOLTIPS.ingredientPacOverride}
              />
              <NumField
                label="POD override"
                unit=""
                value={form.pod_override}
                onChange={numChange("pod_override")}
                error={errors.pod_override}
                tooltip={TOOLTIPS.ingredientPodOverride}
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
            form="ingredient-form"
            className="btn btn-primary btn-sm"
            disabled={mutation.isPending}
          >
            {mutation.isPending && (
              <span className="loading loading-spinner loading-xs" />
            )}
            {isEdit ? "Save changes" : "Add ingredient"}
          </button>
        </div>
      </div>
      <form method="dialog" className="modal-backdrop">
        <button onClick={onClose}>close</button>
      </form>
    </dialog>
  );
}
