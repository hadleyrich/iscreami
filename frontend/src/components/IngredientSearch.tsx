import { useEffect, useMemo, useRef, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { fetchIngredients } from "../api";
import type { Ingredient } from "../types";

const DROPDOWN_ID = "ingredient-search-listbox";

interface IngredientSearchProps {
  readonly onSelect: (ingredient: Ingredient) => void;
}

export function IngredientSearch({ onSelect }: IngredientSearchProps) {
  const [query, setQuery] = useState("");
  const [debouncedQuery, setDebouncedQuery] = useState("");
  // "dismissed" tracks whether the user has explicitly closed the dropdown
  // (Escape or click-outside). Resets automatically on any input change or focus.
  const [dismissed, setDismissed] = useState(false);
  const [activeIndex, setActiveIndex] = useState(-1);
  const containerRef = useRef<HTMLDivElement>(null);
  const listRef = useRef<HTMLUListElement>(null);

  // Update the debounced query inside the timer callback (never synchronously)
  useEffect(() => {
    const t = setTimeout(() => setDebouncedQuery(query.trim()), 200);
    return () => clearTimeout(t);
  }, [query]);

  const { data } = useQuery({
    queryKey: ["ingredient-search", debouncedQuery],
    queryFn: ({ signal }) =>
      fetchIngredients({ q: debouncedQuery, limit: 15 }, signal),
    enabled: debouncedQuery.length > 0,
  });

  const results = useMemo(() => data?.items ?? [], [data]);

  // Derive open state — no separate boolean state needed
  const dropdownOpen =
    !dismissed && results.length > 0 && query.trim().length > 0;

  // Scroll the highlighted item into view
  useEffect(() => {
    if (activeIndex < 0 || !listRef.current) return;
    const item = listRef.current.children[activeIndex] as HTMLElement;
    item?.scrollIntoView({ block: "nearest" });
  }, [activeIndex]);

  // Click-outside closes the dropdown
  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (
        containerRef.current &&
        !containerRef.current.contains(e.target as Node)
      ) {
        setDismissed(true);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  function handleChange(e: React.ChangeEvent<HTMLInputElement>) {
    setQuery(e.target.value);
    setDismissed(false);
    setActiveIndex(-1);
  }

  function handleSelect(ing: Ingredient) {
    onSelect(ing);
    setQuery("");
    setDebouncedQuery("");
    setDismissed(true);
    setActiveIndex(-1);
  }

  function handleKeyDown(e: React.KeyboardEvent<HTMLInputElement>) {
    if (e.key === "Escape") {
      setDismissed(true);
      setActiveIndex(-1);
      return;
    }
    if (!dropdownOpen) return;
    if (e.key === "ArrowDown") {
      e.preventDefault();
      setActiveIndex((i) => Math.min(i + 1, results.length - 1));
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      setActiveIndex((i) => Math.max(i - 1, 0));
    } else if (e.key === "Enter" && activeIndex >= 0) {
      e.preventDefault();
      handleSelect(results[activeIndex]);
    }
  }

  return (
    <div ref={containerRef} className="relative">
      <input
        type="text"
        role="combobox"
        aria-label="Search ingredients"
        aria-expanded={dropdownOpen}
        aria-autocomplete="list"
        aria-controls={DROPDOWN_ID}
        aria-activedescendant={
          activeIndex >= 0 ? `ingredient-option-${activeIndex}` : undefined
        }
        value={query}
        onChange={handleChange}
        onFocus={() => setDismissed(false)}
        onKeyDown={handleKeyDown}
        placeholder="Search ingredients..."
        className="input input-bordered input-sm w-full"
      />
      {dropdownOpen && (
        <ul
          ref={listRef}
          id={DROPDOWN_ID}
          aria-label="Ingredient suggestions"
          className="absolute z-50 w-full mt-1 bg-base-100 border border-base-200
                     rounded-lg shadow-lg max-h-64 overflow-y-auto overflow-x-hidden p-1"
        >
          {results.map((ing, i) => (
            <li key={ing.id}>
              <button
                id={`ingredient-option-${i}`}
                type="button"
                tabIndex={-1}
                className={`w-full text-left px-3 py-2 text-sm rounded-md whitespace-normal wrap-break-word leading-snug ${
                  i === activeIndex ? "bg-base-200" : "hover:bg-base-200"
                }`}
                onClick={() => handleSelect(ing)}
              >
                <span className="block font-medium text-base-content/90">{ing.name}</span>
                {ing.category && (
                  <span className="block mt-0.5 text-xs text-base-content/45">
                    {ing.category.name}
                  </span>
                )}
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
