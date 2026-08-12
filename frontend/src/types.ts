/* API types matching the backend Pydantic schemas. */

import { z } from "zod";

// ── Shared field preprocessors ────────────────────────────────────────────────

// Accepts string (form input) or number/null (API response) → number | null
const numericNullable = z.preprocess(
    (val) => {
        if (val === null || val === undefined || val === "") return null;
        if (typeof val === "string") { const n = Number(val); return Number.isFinite(n) ? n : null; }
        if (typeof val === "number") return Number.isFinite(val) ? val : null;
        return null;
    },
    z.number().nullable(),
);

// ── IngredientCategory ────────────────────────────────────────────────────────

export interface IngredientCategory {
    id: number;
    name: string;
    slug: string;
}

// ── Ingredient ────────────────────────────────────────────────────────────────

// Fields the user can create/edit — used for form validation and API payloads
export const IngredientInputSchema = z.object({
    name: z.string().min(1, "Name is required").max(255, "Name too long"),
    description: z.preprocess(
        (val) => (typeof val === "string" && val.trim() === "" ? null : val),
        z.string().max(2000, "Description too long").nullable(),
    ),
    category_id: z.preprocess(
        (val) => {
            if (val === "" || val === null || val === undefined) return null;
            return typeof val === "string" ? Number(val) : val;
        },
        z.number().int().nullable(),
    ),
    energy_kj_per_100g: numericNullable,
    water_pct: numericNullable,
    protein_pct: numericNullable,
    total_fat_pct: numericNullable,
    saturated_fat_pct: numericNullable,
    trans_fat_pct: numericNullable,
    carbohydrate_pct: numericNullable,
    fiber_pct: numericNullable,
    total_sugar_pct: numericNullable,
    alcohol_pct: numericNullable,
    sodium_mg: numericNullable,
    sucrose_pct: numericNullable,
    glucose_pct: numericNullable,
    fructose_pct: numericNullable,
    lactose_pct: numericNullable,
    maltose_pct: numericNullable,
    galactose_pct: numericNullable,
    milk_fat_pct: numericNullable,
    msnf_pct: numericNullable,
    cocoa_butter_pct: numericNullable,
    cocoa_solids_pct: numericNullable,
    stabilizer_pct: numericNullable,
    emulsifier_pct: numericNullable,
    pac_override: numericNullable,
    pod_override: numericNullable,
    aliases: z.preprocess(
        (val) => {
            if (Array.isArray(val)) return val;
            if (typeof val === "string")
                return val.split(",").map((s) => s.trim()).filter(Boolean);
            return [];
        },
        z.array(z.string().max(200, "Alias must be at most 200 characters")).max(50, "At most 50 aliases allowed"),
    ),
});
export type IngredientInput = z.infer<typeof IngredientInputSchema>;

// Full API response — extends IngredientInput with server-generated fields
export interface Ingredient {
    id: string;
    name: string;
    description: string | null;
    category_id: number | null;
    source: string;
    source_id: string | null;
    energy_kj_per_100g: number | null;
    water_pct: number | null;
    protein_pct: number | null;
    total_fat_pct: number | null;
    saturated_fat_pct: number | null;
    trans_fat_pct: number | null;
    carbohydrate_pct: number | null;
    fiber_pct: number | null;
    total_sugar_pct: number | null;
    alcohol_pct: number | null;
    sodium_mg: number | null;
    sucrose_pct: number | null;
    glucose_pct: number | null;
    fructose_pct: number | null;
    lactose_pct: number | null;
    maltose_pct: number | null;
    galactose_pct: number | null;
    milk_fat_pct: number | null;
    msnf_pct: number | null;
    cocoa_butter_pct: number | null;
    cocoa_solids_pct: number | null;
    stabilizer_pct: number | null;
    emulsifier_pct: number | null;
    pac_override: number | null;
    pod_override: number | null;
    aliases: string[];
    pac: number;
    pod: number;
    total_solids_pct: number;
    created_at: string;
    updated_at: string;
    category: IngredientCategory | null;
}

export interface PaginatedIngredients {
    total: number;
    items: Ingredient[];
}

export interface TargetProfile {
    id: string;
    name: string;
    serving_temp_min: number | null;
    serving_temp_max: number | null;
    sweetness_min: number | null;
    sweetness_max: number | null;
    total_solids_min: number | null;
    total_solids_max: number | null;
    total_fat_min: number | null;
    total_fat_max: number | null;
    milk_fat_min: number | null;
    milk_fat_max: number | null;
    sugar_min: number | null;
    sugar_max: number | null;
    alcohol_min: number | null;
    alcohol_max: number | null;
    msnf_min: number | null;
    msnf_max: number | null;
    stabilizer_min: number | null;
    stabilizer_max: number | null;
    emulsifier_min: number | null;
    emulsifier_max: number | null;
}

export const TargetProfileInputSchema = z.object({
    name: z.string().min(1, "Name is required").max(255, "Name too long"),
    serving_temp_min: numericNullable,
    serving_temp_max: numericNullable,
    sweetness_min: numericNullable,
    sweetness_max: numericNullable,
    total_solids_min: numericNullable,
    total_solids_max: numericNullable,
    total_fat_min: numericNullable,
    total_fat_max: numericNullable,
    milk_fat_min: numericNullable,
    milk_fat_max: numericNullable,
    sugar_min: numericNullable,
    sugar_max: numericNullable,
    alcohol_min: numericNullable,
    alcohol_max: numericNullable,
    msnf_min: numericNullable,
    msnf_max: numericNullable,
    stabilizer_min: numericNullable,
    stabilizer_max: numericNullable,
    emulsifier_min: numericNullable,
    emulsifier_max: numericNullable,
});
export type TargetProfileInput = z.infer<typeof TargetProfileInputSchema>;

export interface RecipeIngredientOut {
    id: number;
    ingredient_id: string;
    weight_grams: number;
    sort_order: number;
    ingredient: Ingredient;
}

export interface Recipe {
    id: string;
    name: string;
    description: string | null;
    recipe_type: string | null;
    target_profile_id: string | null;
    target_profile: TargetProfile | null;
    total_weight_grams: number;
    created_at: string;
    updated_at: string;
    ingredients: RecipeIngredientOut[];
}

export interface CalculateIngredientInput {
    ingredient_id: string;
    weight_grams: number;
}

export interface CalculateRequest {
    target_profile_id?: string | null;
    ingredients: CalculateIngredientInput[];
    serving_size_g?: number;
}

export interface CompositionResult {
    total_weight_g: number;
    water_pct: number;
    total_solids_pct: number;
    total_fat_pct: number;
    saturated_fat_pct: number;
    trans_fat_pct: number;
    milk_fat_pct: number;
    msnf_pct: number;
    total_sugar_pct: number;
    protein_pct: number;
    carbohydrate_pct: number;
    fiber_pct: number;
    alcohol_pct: number;
    stabilizer_pct: number;
    emulsifier_pct: number;
}

export interface PACResult {
    pac_mix: number;
    pac_water: number | null;
}

export interface FreezingCurvePoint {
    temperature_c: number;
    frozen_water_pct: number;
}

export interface FreezingResult {
    freezing_point_c: number;
    serving_temperature_c: number | null;
    curve: FreezingCurvePoint[];
}

export interface SweetenerBreakdownItem {
    ingredient_name: string;
    weight_g: number;
    pct_of_sweeteners: number;
}

export interface SweetnessResult {
    pod: number;
    sweetener_breakdown: SweetenerBreakdownItem[];
}

export interface NutritionResult {
    per_100g: Record<string, number>;
    per_serving: Record<string, number>;
    serving_size_g: number;
}

export type MetricStatus = "in_range" | "below" | "above";

export interface MetricComparison {
    metric: string;
    value: number;
    target_min: number | null;
    target_max: number | null;
    status: MetricStatus;
}

export interface CalculateResponse {
    composition: CompositionResult;
    pac: PACResult;
    freezing: FreezingResult;
    sweetness: SweetnessResult;
    nutrition: NutritionResult;
    target_comparison: MetricComparison[] | null;
}
