/* API client for communicating with the iscreami backend. */

import type {
    CalculateRequest,
    CalculateResponse,
    Ingredient,
    IngredientCategory,
    IngredientInput,
    PaginatedIngredients,
    Recipe,
    TargetProfile,
    TargetProfileInput,
} from "./types";

const BASE = "/api/v1";

function parseErrorMessage(status: number, body: string): string {
    let message = `HTTP ${status}`;
    try {
        message = (JSON.parse(body) as { detail?: string })?.detail ?? message;
    } catch {
        /* use status fallback */
    }
    return message;
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
    const headers: Record<string, string> = {
        ...(init?.headers as Record<string, string> | undefined),
    };
    if (init?.body) headers["Content-Type"] = "application/json";
    const res = await fetch(`${BASE}${path}`, {
        ...init,
        headers,
    });
    if (!res.ok) {
        const body = await res.text();
        throw new Error(parseErrorMessage(res.status, body));
    }
    if (res.status === 204) return undefined as unknown as T;
    return res.json();
}

// --- Ingredients ---

export function fetchIngredients(
    params?: {
        q?: string;
        category_id?: number;
        source?: string;
        offset?: number;
        limit?: number;
    },
    signal?: AbortSignal,
): Promise<PaginatedIngredients> {
    const sp = new URLSearchParams();
    if (params?.q) sp.set("q", params.q);
    if (params?.category_id) sp.set("category_id", String(params.category_id));
    if (params?.source) sp.set("source", params.source);
    if (params?.offset) sp.set("offset", String(params.offset));
    if (params?.limit) sp.set("limit", String(params.limit));
    const qs = sp.toString();
    const path = qs ? `/ingredients?${qs}` : "/ingredients";
    return request(path, signal ? { signal } : undefined);
}

export function fetchIngredient(id: string): Promise<Ingredient> {
    return request(`/ingredients/${id}`);
}

export function createIngredient(data: IngredientInput): Promise<Ingredient> {
    return request("/ingredients", { method: "POST", body: JSON.stringify(data) });
}

export function updateIngredient(id: string, data: IngredientInput): Promise<Ingredient> {
    return request(`/ingredients/${id}`, { method: "PUT", body: JSON.stringify(data) });
}

export function deleteIngredient(id: string): Promise<void> {
    return request(`/ingredients/${id}`, { method: "DELETE" });
}

// --- Categories ---

export function fetchCategories(): Promise<IngredientCategory[]> {
    return request("/ingredient-categories");
}

// --- Recipes ---

export function fetchRecipes(): Promise<{ total: number; items: Recipe[] }> {
    return request("/recipes");
}

export function fetchRecipe(id: string): Promise<Recipe> {
    return request(`/recipes/${id}`);
}

export function createRecipe(data: {
    name: string;
    target_profile_id?: string | null;
    ingredients: { ingredient_id: string; weight_grams: number; sort_order: number }[];
}): Promise<Recipe> {
    return request("/recipes", { method: "POST", body: JSON.stringify(data) });
}

export function updateRecipe(
    id: string,
    data: {
        name?: string;
        target_profile_id?: string | null;
        ingredients?: { ingredient_id: string; weight_grams: number; sort_order: number }[];
    }
): Promise<Recipe> {
    return request(`/recipes/${id}`, { method: "PUT", body: JSON.stringify(data) });
}

export function deleteRecipe(id: string): Promise<void> {
    return request(`/recipes/${id}`, { method: "DELETE" });
}

// --- Target Profiles ---

export function fetchProfiles(): Promise<TargetProfile[]> {
    return request("/target-profiles");
}

export function createProfile(data: TargetProfileInput): Promise<TargetProfile> {
    return request("/target-profiles", { method: "POST", body: JSON.stringify(data) });
}

export function updateProfile(id: string, data: TargetProfileInput): Promise<TargetProfile> {
    return request(`/target-profiles/${id}`, { method: "PUT", body: JSON.stringify(data) });
}

export function deleteProfile(id: string): Promise<void> {
    return request(`/target-profiles/${id}`, { method: "DELETE" });
}

// --- Calculator ---

export function calculate(data: CalculateRequest): Promise<CalculateResponse> {
    return request("/calculate", { method: "POST", body: JSON.stringify(data) });
}

// --- Export/Import ---

export async function exportRecipe(id: string): Promise<unknown> {
    return request(`/recipes/${id}/export`);
}

export async function exportAllRecipes(): Promise<unknown[]> {
    return request(`/recipes/export-all`);
}

export async function importRecipes(file: File): Promise<Recipe[]> {
    const formData = new FormData();
    formData.append("file", file);
    const res = await fetch(`${BASE}/recipes/import`, {
        method: "POST",
        body: formData,
    });
    if (!res.ok) {
        const body = await res.text();
        throw new Error(parseErrorMessage(res.status, body));
    }
    return res.json();
}
