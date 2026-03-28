import { useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { Plus, Download, Upload } from "lucide-react";
import { fetchRecipes, exportAllRecipes, importRecipes } from "../api";
import { useState } from "react";
import { FileUploadModal } from "./FileUploadModal";
import { useToast } from "../hooks/useToast";
import { RecipeCard } from "./RecipeCard";

export function RecipesView() {
  const navigate = useNavigate();
  const { addToast } = useToast();
  const [importModalOpen, setImportModalOpen] = useState(false);
  const [importLoading, setImportLoading] = useState(false);
  const [importError, setImportError] = useState<string | null>(null);
  const [importSuccess, setImportSuccess] = useState(0);

  const { data: recipesData, isLoading, refetch } = useQuery({
    queryKey: ["recipes"],
    queryFn: fetchRecipes,
  });

  const recipes = recipesData?.items ?? [];

  async function handleExportAll() {
    try {
      const data = await exportAllRecipes();
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = "recipes-export.json";
      document.body.appendChild(link);
      link.click();
      link.remove();
      URL.revokeObjectURL(url);
      addToast(`Exported ${data.length} recipes`, "success");
    } catch (err) {
      addToast(err instanceof Error ? err.message : "Failed to export recipes", "error");
    }
  }

  async function handleImportFile(file: File) {
    setImportLoading(true);
    setImportError(null);
    setImportSuccess(0);
    try {
      const results = await importRecipes(file);
      setImportSuccess(results.length);
      await refetch();
      setTimeout(() => {
        setImportModalOpen(false);
        setImportSuccess(0);
      }, 2000);
      addToast(`Imported ${results.length} recipe${results.length === 1 ? "" : "s"}`, "success");
    } catch (err) {
      const errMsg = err instanceof Error ? err.message : "Failed to import recipes";
      setImportError(errMsg);
      addToast(errMsg, "error");
    } finally {
      setImportLoading(false);
    }
  }

  return (
    <main className="max-w-7xl mx-auto px-4 py-6">
      <div className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div className="min-w-0">
          <h1 className="text-2xl font-bold text-base-content">Recipes</h1>
          <p className="mt-1 text-sm text-base-content/60">
            Browse and manage your saved ice cream recipes
          </p>
        </div>
        <div className="grid w-full grid-cols-2 gap-2 sm:flex sm:w-auto sm:shrink-0 sm:flex-wrap sm:justify-end">
          <button
            type="button"
            className="btn btn-primary btn-sm gap-1 col-span-2 sm:col-span-1"
            onClick={() => navigate("/calculator")}
          >
            <Plus size={15} />
            New Recipe
          </button>
          <button
            type="button"
            className="btn btn-outline btn-sm gap-1"
            onClick={() => setImportModalOpen(true)}
          >
            <Upload size={15} />
            Import
          </button>
          {recipes.length > 0 && (
            <button
              type="button"
              className="btn btn-outline btn-sm gap-1"
              onClick={() => void handleExportAll()}
            >
              <Download size={15} />
              Export All
            </button>
          )}
        </div>
      </div>

      {isLoading && (
        <div className="flex items-center justify-center py-12">
          <span className="loading loading-spinner loading-lg"></span>
        </div>
      )}

      {!isLoading && recipes.length === 0 && (
        <div className="bg-base-100 rounded-xl border border-base-200 p-12 text-center">
          <p className="text-base-content/60 mb-4">No recipes yet</p>
          <button
            type="button"
            className="btn btn-primary gap-2"
            onClick={() => navigate("/calculator")}
          >
            <Plus size={18} />
            Create your first recipe
          </button>
        </div>
      )}

      {!isLoading && recipes.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {recipes.map((recipe) => (
            <RecipeCard key={recipe.id} recipe={recipe} />
          ))}
        </div>
      )}

      {/* File upload modal */}
      <FileUploadModal
        open={importModalOpen}
        onClose={() => {
          setImportModalOpen(false);
          setImportError(null);
          setImportSuccess(0);
        }}
        onFileSelect={handleImportFile}
        isLoading={importLoading}
        error={importError}
        successCount={importSuccess}
      />
    </main>
  );
}
