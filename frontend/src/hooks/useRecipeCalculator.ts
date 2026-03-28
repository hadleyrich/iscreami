import { useCallback, useEffect, useRef, useState, useMemo } from "react";
import { useQueryClient } from "@tanstack/react-query";
import type { CalculateResponse, Ingredient, Recipe, TargetProfile } from "../types";
import { calculate, createRecipe, updateRecipe as apiUpdateRecipe, deleteRecipe as apiDeleteRecipe } from "../api";
import { useToast } from "./useToast";

export interface RecipeRow {
    ingredient: Ingredient;
    weight_grams: number;
    sort_order: number;
}

export function useRecipeCalculator() {
    const [rows, setRows] = useState<RecipeRow[]>([]);
    const [result, setResult] = useState<CalculateResponse | null>(null);
    const [loading, setLoading] = useState(false);
    const [profile, setProfile] = useState<TargetProfile | null>(null);
    const [currentRecipe, setCurrentRecipe] = useState<Recipe | null>(null);
    const [isSaving, setIsSaving] = useState(false);
    const timerRef = useRef<ReturnType<typeof setTimeout> | undefined>(undefined);
    const lastErrorAtRef = useRef<number>(0);
    const { addToast } = useToast();
    const qc = useQueryClient();

    const triggerCalculate = useCallback(
        (nextRows: RecipeRow[], nextProfile: TargetProfile | null) => {
            if (timerRef.current) clearTimeout(timerRef.current);
            if (nextRows.length === 0) {
                setResult(null);
                return;
            }
            timerRef.current = setTimeout(async () => {
                setLoading(true);
                try {
                    const resp = await calculate({
                        target_profile_id: nextProfile?.id ?? null,
                        ingredients: nextRows.map((r) => ({
                            ingredient_id: r.ingredient.id,
                            weight_grams: r.weight_grams,
                        })),
                    });
                    setResult(resp);
                } catch {
                    // Only surface the error if it persists (> 5 s since last toast)
                    // to avoid flashing on transient debounced failures.
                    const now = Date.now();
                    if (now - lastErrorAtRef.current > 5000) {
                        lastErrorAtRef.current = now;
                        addToast("Could not reach the server. Please check your connection.");
                    }
                } finally {
                    setLoading(false);
                }
            }, 300);
        },
        [addToast]
    );

    const addIngredient = useCallback(
        (ingredient: Ingredient, weight_grams = 100) => {
            setRows((prev) => {
                if (prev.some((r) => r.ingredient.id === ingredient.id)) return prev;
                const next = [
                    ...prev,
                    { ingredient, weight_grams, sort_order: prev.length },
                ];
                triggerCalculate(next, profile);
                return next;
            });
        },
        [profile, triggerCalculate]
    );

    const updateWeight = useCallback(
        (ingredientId: string, weight_grams: number) => {
            setRows((prev) => {
                const next = prev.map((r) =>
                    r.ingredient.id === ingredientId ? { ...r, weight_grams } : r
                );
                triggerCalculate(next, profile);
                return next;
            });
        },
        [profile, triggerCalculate]
    );

    const removeIngredient = useCallback(
        (ingredientId: string) => {
            setRows((prev) => {
                const next = prev.filter((r) => r.ingredient.id !== ingredientId);
                triggerCalculate(next, profile);
                return next;
            });
        },
        [profile, triggerCalculate]
    );

    const changeProfile = useCallback(
        (p: TargetProfile | null) => {
            setProfile(p);
            triggerCalculate(rows, p);
        },
        [rows, triggerCalculate]
    );

    const loadRecipe = useCallback(
        (recipe: Recipe, targetProfile?: TargetProfile | null) => {
            const nextRows: RecipeRow[] = recipe.ingredients
                .slice()
                .sort((a, b) => a.sort_order - b.sort_order)
                .map((ri) => ({
                    ingredient: ri.ingredient,
                    weight_grams: ri.weight_grams,
                    sort_order: ri.sort_order,
                }));
            const p = targetProfile ?? null;
            setRows(nextRows);
            setCurrentRecipe(recipe);
            setProfile(p);
            triggerCalculate(nextRows, p);
        },
        [triggerCalculate]
    );

    const clearRecipe = useCallback(() => {
        setRows([]);
        setResult(null);
        setCurrentRecipe(null);
        setProfile(null);
    }, []);

    const saveAsNewRecipe = useCallback(
        async (name: string) => {
            setIsSaving(true);
            try {
                const saved = await createRecipe({
                    name,
                    target_profile_id: profile?.id ?? null,
                    ingredients: rows.map((r, idx) => ({
                        ingredient_id: r.ingredient.id,
                        weight_grams: r.weight_grams,
                        sort_order: idx,
                    })),
                });
                setCurrentRecipe(saved);
                qc.invalidateQueries({ queryKey: ["recipes"] });
                addToast(`Recipe "${name}" saved.`, "success");
            } catch (err) {
                addToast(err instanceof Error ? err.message : "Failed to save recipe.", "error");
            } finally {
                setIsSaving(false);
            }
        },
        [rows, profile, addToast, qc]
    );

    const saveCurrentRecipe = useCallback(async () => {
        if (!currentRecipe) return;
        setIsSaving(true);
        try {
            const saved = await apiUpdateRecipe(currentRecipe.id, {
                name: currentRecipe.name,
                target_profile_id: profile?.id ?? null,
                ingredients: rows.map((r, idx) => ({
                    ingredient_id: r.ingredient.id,
                    weight_grams: r.weight_grams,
                    sort_order: idx,
                })),
            });
            setCurrentRecipe(saved);
            qc.invalidateQueries({ queryKey: ["recipes"] });
            addToast(`Recipe "${saved.name}" updated.`, "success");
        } catch (err) {
            addToast(err instanceof Error ? err.message : "Failed to update recipe.", "error");
        } finally {
            setIsSaving(false);
        }
    }, [currentRecipe, rows, profile, addToast, qc]);

    const deleteCurrentRecipe = useCallback(async () => {
        if (!currentRecipe) return;
        const name = currentRecipe.name;
        setIsSaving(true);
        try {
            await apiDeleteRecipe(currentRecipe.id);
            qc.invalidateQueries({ queryKey: ["recipes"] });
            addToast(`Recipe "${name}" deleted.`, "success");
            clearRecipe();
        } catch (err) {
            addToast(err instanceof Error ? err.message : "Failed to delete recipe.", "error");
        } finally {
            setIsSaving(false);
        }
    }, [currentRecipe, addToast, qc, clearRecipe]);

    useEffect(() => {
        return () => {
            if (timerRef.current) clearTimeout(timerRef.current);
        };
    }, []);

    // Detect unsaved changes by comparing current state with saved recipe
    const hasUnsavedChanges = useMemo(() => {
        if (!currentRecipe) return false;

        // Check if profile changed
        if ((profile?.id ?? null) !== (currentRecipe.target_profile_id ?? null)) return true;

        // Check if ingredient count changed
        if (rows.length !== currentRecipe.ingredients.length) return true;

        // Check if any ingredient or weight changed
        const savedById = new Map(currentRecipe.ingredients.map((ri) => [ri.ingredient.id, ri]));
        for (const row of rows) {
            const saved = savedById.get(row.ingredient.id);
            if (!saved || saved?.weight_grams !== row.weight_grams) return true;
        }

        return false;
    }, [currentRecipe, rows, profile]);

    return {
        rows,
        result,
        loading,
        profile,
        currentRecipe,
        isSaving,
        hasUnsavedChanges,
        addIngredient,
        updateWeight,
        removeIngredient,
        changeProfile,
        loadRecipe,
        clearRecipe,
        saveAsNewRecipe,
        saveCurrentRecipe,
        deleteCurrentRecipe,
    };
}
