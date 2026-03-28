import { useState } from "react";
import { Link } from "react-router-dom";
import { useQueryClient } from "@tanstack/react-query";
import { ArrowRight, Calendar, Download, Target, Trash2, Utensils, Weight } from "lucide-react";
import { deleteRecipe, exportRecipe } from "../api";
import { useToast } from "../hooks/useToast";
import type { Recipe } from "../types";

interface RecipeCardProps {
  readonly recipe: Recipe;
}

export function RecipeCard({ recipe }: RecipeCardProps) {
  const queryClient = useQueryClient();
  const { addToast } = useToast();
  const [deleteConfirmOpen, setDeleteConfirmOpen] = useState(false);

  async function handleExport() {
    try {
      const data = await exportRecipe(recipe.id);
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `${recipe.name}.json`;
      document.body.appendChild(link);
      link.click();
      link.remove();
      URL.revokeObjectURL(url);
      addToast("Recipe exported", "success");
    } catch (err) {
      addToast(err instanceof Error ? err.message : "Failed to export recipe", "error");
    }
  }

  async function handleDelete() {
    try {
      await deleteRecipe(recipe.id);
      await queryClient.invalidateQueries({ queryKey: ["recipes"] });
      addToast("Recipe deleted", "success");
    } catch (err) {
      addToast(err instanceof Error ? err.message : "Failed to delete recipe", "error");
    } finally {
      setDeleteConfirmOpen(false);
    }
  }

  return (
    <>
      <div className="group flex flex-col bg-base-100 rounded-xl border border-base-200 p-4 hover:border-primary/50 hover:shadow-md transition-all">
        <Link
          to={`/calculator/${recipe.id}`}
          className="flex items-start justify-between gap-3 mb-2"
        >
          <div className="flex-1 min-w-0">
            <h3 className="font-semibold text-base-content group-hover:text-primary transition-colors truncate">
              {recipe.name}
            </h3>
            {recipe.description && (
              <p className="text-xs text-base-content/60 line-clamp-2 mt-0.5">
                {recipe.description}
              </p>
            )}
          </div>
          <ArrowRight
            size={16}
            className="text-base-content/40 group-hover:text-primary group-hover:translate-x-0.5 transition-all shrink-0 mt-0.5"
          />
        </Link>

        <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
          <div className="flex flex-wrap items-center gap-x-3 gap-y-1 text-xs text-base-content/50">
            <div className="flex items-center gap-1 whitespace-nowrap">
              <Utensils size={13} />
              {recipe.ingredients.length} ingredient{recipe.ingredients.length === 1 ? "" : "s"}
            </div>
            <div className="flex items-center gap-1 whitespace-nowrap">
              <Weight size={13} />
              {recipe.total_weight_grams}g
            </div>
            {recipe.target_profile && (
              <div className="flex items-center gap-1 whitespace-nowrap">
                <Target size={13} />
                {recipe.target_profile.name}
              </div>
            )}
            <div className="flex items-center gap-1 whitespace-nowrap">
              <Calendar size={13} />
              {new Date(recipe.updated_at).toLocaleDateString(undefined, {
                month: "short",
                day: "numeric",
              })}
            </div>
          </div>
          <div className="flex items-center gap-1 self-end shrink-0 sm:self-auto">
            <button
              type="button"
              className="btn btn-xs btn-ghost"
              title="Export recipe"
              onClick={() => void handleExport()}
            >
              <Download size={13} />
            </button>
            <button
              type="button"
              className="btn btn-xs btn-ghost text-error hover:bg-error/10"
              title="Delete recipe"
              onClick={() => setDeleteConfirmOpen(true)}
            >
              <Trash2 size={13} />
            </button>
          </div>
        </div>
      </div>

      {deleteConfirmOpen && (
        <div className="modal modal-open">
          <div className="modal-box max-w-sm">
            <h3 className="font-bold text-lg mb-2">Delete Recipe</h3>
            <p className="text-base-content/70">
              Delete <strong>{recipe.name}</strong>? This cannot be undone.
            </p>
            <div className="modal-action">
              <button
                type="button"
                className="btn btn-ghost"
                onClick={() => setDeleteConfirmOpen(false)}
              >
                Cancel
              </button>
              <button
                type="button"
                className="btn btn-error"
                onClick={() => void handleDelete()}
              >
                Delete
              </button>
            </div>
          </div>
          <button
            type="button"
            className="modal-backdrop"
            onClick={() => setDeleteConfirmOpen(false)}
            aria-label="Close delete dialog"
          />
        </div>
      )}
    </>
  );
}
