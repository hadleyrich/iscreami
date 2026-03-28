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

export const IngredientCategorySchema = z.object({
    id: z.number(),
    name: z.string(),
    slug: z.string(),
});
export type IngredientCategory = z.infer<typeof IngredientCategorySchema>;

// ── Ingredient ────────────────────────────────────────────────────────────────

// Fields the user can create/edit — used for form validation and API payloads
export const IngredientInputSchema = z.object({
    name: z.string().min(1, "Name is required"),
    description: z.preprocess(
        (val) => (typeof val === "string" && val.trim() === "" ? null : val),
        z.string().nullable(),
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
        z.array(z.string()),
    ),
});
export type IngredientInput = z.infer<typeof IngredientInputSchema>;

// Full API response — extends IngredientInput with server-generated fields
export const IngredientSchema = IngredientInputSchema.extend({
    id: z.string(),
    source: z.string(),
    source_id: z.string().nullable(),
    pac: z.number(),
    pod: z.number(),
    total_solids_pct: z.number(),
    created_at: z.string(),
    updated_at: z.string(),
    category: IngredientCategorySchema.nullable(),
});
export type Ingredient = z.infer<typeof IngredientSchema>;

export const PaginatedIngredientsSchema = z.object({
    total: z.number(),
    items: z.array(IngredientSchema),
});
export type PaginatedIngredients = z.infer<typeof PaginatedIngredientsSchema>;

export const TargetProfileSchema = z.object({
    id: z.string(),
    name: z.string(),
    serving_temp_min: z.number().nullable(),
    serving_temp_max: z.number().nullable(),
    sweetness_min: z.number().nullable(),
    sweetness_max: z.number().nullable(),
    total_solids_min: z.number().nullable(),
    total_solids_max: z.number().nullable(),
    total_fat_min: z.number().nullable(),
    total_fat_max: z.number().nullable(),
    milk_fat_min: z.number().nullable(),
    milk_fat_max: z.number().nullable(),
    sugar_min: z.number().nullable(),
    sugar_max: z.number().nullable(),
    alcohol_min: z.number().nullable(),
    alcohol_max: z.number().nullable(),
    msnf_min: z.number().nullable(),
    msnf_max: z.number().nullable(),
    stabilizer_min: z.number().nullable(),
    stabilizer_max: z.number().nullable(),
    emulsifier_min: z.number().nullable(),
    emulsifier_max: z.number().nullable(),
});
export type TargetProfile = z.infer<typeof TargetProfileSchema>;

export const TargetProfileInputSchema = z.object({
    name: z.string().min(1, "Name is required"),
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

export interface RecipeIngredientInput {
    ingredient_id: string;
    weight_grams: number;
    sort_order: number;
}

export const RecipeIngredientOutSchema = z.object({
    id: z.number(),
    ingredient_id: z.string(),
    weight_grams: z.number(),
    sort_order: z.number(),
    ingredient: IngredientSchema,
});
export type RecipeIngredientOut = z.infer<typeof RecipeIngredientOutSchema>;

export const RecipeSchema = z.object({
    id: z.string(),
    name: z.string(),
    description: z.string().nullable(),
    recipe_type: z.string().nullable(),
    target_profile_id: z.string().nullable(),
    target_profile: TargetProfileSchema.nullable(),
    total_weight_grams: z.number(),
    created_at: z.string(),
    updated_at: z.string(),
    ingredients: z.array(RecipeIngredientOutSchema),
});
export type Recipe = z.infer<typeof RecipeSchema>;

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
