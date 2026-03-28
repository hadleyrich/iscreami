import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useDebouncedValue } from "../hooks/useDebouncedValue";
import { Search, Plus, Pencil, Trash2 } from "lucide-react";
import { fetchIngredients, fetchCategories, deleteIngredient } from "../api";
import type { Ingredient } from "../types";
import { IngredientFormModal } from "./IngredientFormModal";
import { useToast } from "../hooks/useToast";
import { fmt, fmtKj } from "../lib/formatting";
import { InfoIcon } from "./InfoIcon";
import { TOOLTIPS } from "../lib/tooltips";

const PAGE_SIZE = 50;

const CATEGORY_COLORS: Record<string, string> = {
  sweetener:
    "bg-pink-100 text-pink-700 dark:bg-pink-900/50 dark:text-pink-300",
  dairy: "bg-blue-100 text-blue-700 dark:bg-blue-900/50 dark:text-blue-300",
  stabilizer:
    "bg-cyan-100 text-cyan-700 dark:bg-cyan-900/50 dark:text-cyan-300",
  emulsifier:
    "bg-orange-100 text-orange-700 dark:bg-orange-900/50 dark:text-orange-300",
  fat_oil:
    "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/50 dark:text-yellow-300",
  fruit:
    "bg-green-100 text-green-700 dark:bg-green-900/50 dark:text-green-300",
  flavoring:
    "bg-rose-100 text-rose-700 dark:bg-rose-900/50 dark:text-rose-300",
  alcohol:
    "bg-red-100 text-red-700 dark:bg-red-900/50 dark:text-red-300",
};

const SOURCE_LABELS: Record<string, string> = {
  seed: "Built-in",
  usda: "USDA",
  nzfcdb: "NZFCDB",
  manual: "Custom",
};

function sourceUrl(source: string, sourceId: string | null): string | null {
  if (!sourceId) return null;
  if (source === "nzfcdb")
    return `https://www.foodcomposition.co.nz/search/food/${sourceId}`;
  if (source === "usda")
    return `https://fdc.nal.usda.gov/food-details/${sourceId}/nutrients`;
  return null;
}

const ALL_SOURCES = [
  { value: "seed", label: "Built-in" },
  { value: "usda", label: "USDA" },
  { value: "nzfcdb", label: "NZFCDB" },
  { value: "manual", label: "Custom" },
];



export function IngredientsView() {
  const [searchInput, setSearchInput] = useState("");
  const [categoryId, setCategoryId] = useState<number | null>(null);
  const [source, setSource] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [modalOpen, setModalOpen] = useState(false);
  const [editingIngredient, setEditingIngredient] = useState<Ingredient | null>(null);
  const [deletingIngredient, setDeletingIngredient] = useState<Ingredient | null>(null);

  const qc = useQueryClient();
  const { addToast } = useToast();

  const deleteMutation = useMutation({
    mutationFn: (id: string) => deleteIngredient(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["ingredients"] });
      addToast("Ingredient deleted.", "success");
      setDeletingIngredient(null);
    },
    onError: (err: Error) => {
      addToast(err.message, "error");
      setDeletingIngredient(null);
    },
  });

  function openAdd() {
    setEditingIngredient(null);
    setModalOpen(true);
  }

  function openEdit(ing: Ingredient) {
    setEditingIngredient(ing);
    setModalOpen(true);
  }

  const search = useDebouncedValue(searchInput, 300);

  const { data: categories } = useQuery({
    queryKey: ["categories"],
    queryFn: fetchCategories,
  });

  const { data, isLoading } = useQuery({
    queryKey: ["ingredients", search, categoryId, source, page],
    queryFn: () =>
      fetchIngredients({
        q: search || undefined,
        category_id: categoryId ?? undefined,
        source: source ?? undefined,
        offset: (page - 1) * PAGE_SIZE,
        limit: PAGE_SIZE,
      }),
  });

  const totalPages = data ? Math.ceil(data.total / PAGE_SIZE) : 1;
  const start = (page - 1) * PAGE_SIZE + 1;
  const end = data ? Math.min(page * PAGE_SIZE, data.total) : 0;

  return (
    <div className="max-w-7xl mx-auto px-4 py-6">
      <div className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div className="min-w-0">
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold">Ingredients</h1>
          </div>
          <p className="text-sm text-base-content/60 mt-1">
            Composition and nutrition data for available ingredients.
          </p>
        </div>
        <button
          type="button"
          className="btn btn-primary btn-sm w-full sm:w-auto sm:shrink-0"
          onClick={openAdd}
        >
          <Plus size={15} />
          Add ingredient
        </button>
      </div>

      {/* Filters */}
      <div className="flex gap-3 mb-4 flex-wrap">
        <div className="relative flex-1 min-w-48">
          <Search
            className="absolute left-3 top-1/2 -translate-y-1/2 text-base-content/40"
            size={16}
          />
          <input
            type="text"
            aria-label="Search ingredients by name"
            placeholder="Search ingredients by name..."
            value={searchInput}
            onChange={(e) => { setSearchInput(e.target.value); setPage(1); }}
            className="input input-bordered input-sm w-full pl-9 pr-3"
          />
        </div>
        <select
          value={categoryId ?? ""}
          onChange={(e) => {
            setCategoryId(e.target.value ? Number(e.target.value) : null);
            setPage(1);
          }}
          className="select select-bordered select-sm w-full sm:w-auto"
        >
          <option value="">All categories</option>
          {categories?.map((c) => (
            <option key={c.id} value={c.id}>
              {c.name}
            </option>
          ))}
        </select>
        <select
          value={source ?? ""}
          onChange={(e) => {
            setSource(e.target.value || null);
            setPage(1);
          }}
          className="select select-bordered select-sm w-full sm:w-auto"
        >
          <option value="">All sources</option>
          {ALL_SOURCES.map((s) => (
            <option key={s.value} value={s.value}>
              {s.label}
            </option>
          ))}
        </select>
      </div>

      {/* Table */}
      <div className="bg-base-100 rounded-xl shadow-sm border border-base-200 overflow-hidden">
        <div className="overflow-x-auto md:overflow-visible">
          <table className="table table-sm w-full">
            <thead>
              <tr className="border-b border-base-200 bg-base-200">
                <th className="text-left px-4 py-3 font-medium text-base-content/60 whitespace-nowrap">
                  Name
                </th>
                <th className="text-left px-4 py-3 font-medium text-base-content/60 whitespace-nowrap">
                  Category
                </th>
                <th className="text-left px-4 py-3 font-medium text-base-content/60 whitespace-nowrap">
                  Source
                </th>
                <th className="text-right px-4 py-3 font-medium text-base-content/60 whitespace-nowrap">
                  Energy
                </th>
                <th className="text-right px-4 py-3 font-medium text-base-content/60 whitespace-nowrap">
                  <div className="flex items-center justify-end gap-1">
                    <span>Total solids</span>
                    <InfoIcon label={TOOLTIPS.totalSolids} position="bottom" />
                  </div>
                </th>
                <th className="text-right px-4 py-3 font-medium text-base-content/60 whitespace-nowrap">
                  <div className="flex items-center justify-end gap-1">
                    <span>Fat</span>
                    <InfoIcon label={TOOLTIPS.totalFat} position="bottom" />
                  </div>
                </th>
                <th className="text-right px-4 py-3 font-medium text-base-content/60 whitespace-nowrap">
                  <div className="flex items-center justify-end gap-1">
                    <span>Protein</span>
                    <InfoIcon label={TOOLTIPS.protein} position="bottom" />
                  </div>
                </th>
                <th className="text-right px-4 py-3 font-medium text-base-content/60 whitespace-nowrap">
                  Alcohol
                </th>
                <th className="text-right px-4 py-3 font-medium text-base-content/60 whitespace-nowrap">
                  <div className="flex items-center justify-end gap-1">
                    <span>PAC</span>
                    <InfoIcon label={TOOLTIPS.pac} position="bottom" />
                  </div>
                </th>
                <th className="text-right px-4 py-3 font-medium text-base-content/60 whitespace-nowrap">
                  <div className="flex items-center justify-end gap-1">
                    <span>Sweetness</span>
                    <InfoIcon label={TOOLTIPS.sweetness} position="bottom" />
                  </div>
                </th>
                <th className="px-4 py-3" />
              </tr>
            </thead>
            <tbody>
              {isLoading && (
                <tr>
                  <td
                    colSpan={11}
                    className="text-center py-10 text-base-content/40 animate-pulse"
                  >
                    Loading…
                  </td>
                </tr>
              )}
              {!isLoading && data?.items.length === 0 && (
                <tr>
                  <td
                    colSpan={11}
                    className="text-center py-10 text-base-content/40"
                  >
                    No ingredients found.
                  </td>
                </tr>
              )}
              {data?.items.map((ing) => (
                <tr
                  key={ing.id}
                  className="border-b border-base-200 hover:bg-base-200/40 transition-colors"
                >
                  <td className="px-4 py-2.5 font-medium">{ing.name}</td>
                  <td className="px-4 py-2.5">
                    {ing.category ? (
                      <span
                        className={`badge badge-sm ${
                          CATEGORY_COLORS[ing.category.slug] ??
                          "bg-base-200 text-base-content/60"
                        }`}
                      >
                        {ing.category.name}
                      </span>
                    ) : (
                      <span className="text-base-content/40 text-xs">—</span>
                    )}
                  </td>
                  <td className="px-4 py-2.5 text-base-content/60">
                    {(() => {
                      const url = sourceUrl(ing.source, ing.source_id);
                      const label = SOURCE_LABELS[ing.source] ?? ing.source;
                      return url ? (
                        <a
                          href={url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="hover:underline text-blue-600 dark:text-blue-400"
                        >
                          {label}
                        </a>
                      ) : (
                        label
                      );
                    })()}
                  </td>
                  <td className="px-4 py-2.5 text-right tabular-nums">
                    {fmtKj(ing.energy_kj_per_100g)}
                  </td>
                  <td className="px-4 py-2.5 text-right tabular-nums">
                    {fmt(ing.total_solids_pct)}
                  </td>
                  <td className="px-4 py-2.5 text-right tabular-nums">
                    {fmt(ing.total_fat_pct)}
                  </td>
                  <td className="px-4 py-2.5 text-right tabular-nums">
                    {fmt(ing.protein_pct)}
                  </td>
                  <td className="px-4 py-2.5 text-right tabular-nums">
                    {fmt(ing.alcohol_pct)}
                  </td>
                  <td className="px-4 py-2.5 text-right tabular-nums">
                    {fmt(ing.pac)}
                  </td>
                  <td className="px-4 py-2.5 text-right tabular-nums">
                    {fmt(ing.pod)}
                  </td>
                  <td className="px-4 py-2.5">
                    <div className="flex justify-end gap-1">
                      <button
                        type="button"
                        className="btn btn-ghost btn-xs btn-circle"
                        aria-label="Edit"
                        onClick={() => openEdit(ing)}
                      >
                        <Pencil size={13} />
                      </button>
                      <button
                        type="button"
                        className="btn btn-ghost btn-xs btn-circle text-error"
                        aria-label="Delete"
                        onClick={() => setDeletingIngredient(ing)}
                      >
                        <Trash2 size={13} />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        {data && data.total > PAGE_SIZE && (
          <div className="flex items-center justify-between px-4 py-3 border-t border-base-200">
            <span className="text-sm text-base-content/60">
              {start}–{end} of {data.total}
            </span>
            <div className="flex gap-2">
              <button
                type="button"
                className="btn btn-sm disabled:opacity-40"
                disabled={page === 1}
                onClick={() => setPage((p) => p - 1)}
              >
                Previous
              </button>
              <button
                type="button"
                className="btn btn-sm disabled:opacity-40"
                disabled={page >= totalPages}
                onClick={() => setPage((p) => p + 1)}
              >
                Next
              </button>
            </div>
          </div>
        )}
      </div>

      {data && (
        <p className="text-xs text-base-content/40 mt-2">
          {data.total.toLocaleString()} ingredient{data.total === 1 ? "" : "s"}{" "}
          total
        </p>
      )}

      {modalOpen && (
        <IngredientFormModal
          key={editingIngredient?.id ?? "new"}
          open
          ingredient={editingIngredient}
          onClose={() => setModalOpen(false)}
        />
      )}

      {/* Delete confirmation */}
      <dialog className="modal" open={deletingIngredient != null}>
        <div className="modal-box max-w-sm">
          <h3 className="font-bold text-lg">Delete ingredient?</h3>
          <p className="py-3 text-sm text-base-content/70">
            <span className="font-medium">{deletingIngredient?.name}</span> will
            be permanently removed. If it's used in any recipes, deletion will
            be blocked.
          </p>
          <div className="modal-action">
            <button
              type="button"
              className="btn btn-ghost btn-sm"
              onClick={() => setDeletingIngredient(null)}
            >
              Cancel
            </button>
            <button
              type="button"
              className="btn btn-error btn-sm"
              disabled={deleteMutation.isPending}
              onClick={() =>
                deletingIngredient && deleteMutation.mutate(deletingIngredient.id)
              }
            >
              {deleteMutation.isPending && (
                <span className="loading loading-spinner loading-xs" />
              )}
              Delete
            </button>
          </div>
        </div>
        <form method="dialog" className="modal-backdrop">
          <button onClick={() => setDeletingIngredient(null)}>close</button>
        </form>
      </dialog>
    </div>
  );
}
