# Frontend Developer Guide

This guide covers everything you need to know to work on the iscreami React/TypeScript frontend: architecture, coding conventions, component patterns, state management, UI/UX conventions, and theming.

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Development Environment](#development-environment)
3. [Project Structure](#project-structure)
4. [Coding Conventions](#coding-conventions)
5. [API Client](#api-client)
6. [Type System](#type-system)
7. [State Management](#state-management)
8. [Routing](#routing)
9. [UI & Design Conventions](#ui--design-conventions)
10. [Theming (Dark / Light Mode)](#theming-dark--light-mode)
11. [Component Patterns](#component-patterns)
12. [Hooks](#hooks)
13. [Type Checking & Building](#type-checking--building)

---

## Architecture Overview

The frontend is a single-page application (SPA) built with React 19 and TypeScript. It follows a strict data-flow pattern:

```
User Interaction
      ↓
  Component (pure display, receives props)
      ↓
  Hook (state, side effects, API calls)
      ↓
  api.ts (typed fetch client)
      ↓
  Backend API (/api/v1/*)
```

**Key design rules:**

- **Components are pure display.** They receive props and emit events — they never call `fetch` directly.
- **All API calls go through `api.ts`.** Functions in `api.ts` are the only place that uses `fetch`.
- **Server state is managed with TanStack Query** (`@tanstack/react-query`). Client/UI state lives in hooks or `App.tsx`.
- **Types are defined once in `types.ts`** and imported everywhere — never define inline API response shapes in components.

---

## Development Environment

### Prerequisites

- Node.js 20+
- pnpm (install with `npm install -g pnpm` or `brew install pnpm`)

### Setup

```bash
cd frontend
pnpm install
pnpm dev
# Frontend dev server: http://localhost:5173
# API proxy forwards /api/* → http://localhost:8000
```

The Vite dev server is configured to proxy `/api/*` requests to `localhost:8000`, so you can run the backend separately and the frontend will talk to it seamlessly.

### Building for Production

```bash
cd frontend
pnpm build
# Output: frontend/dist/
```

The production build is served by the FastAPI backend as static files (mounted at `/`).

---

## Project Structure

```
frontend/src/
├── App.tsx             # Root component: layout, routing, providers
├── main.tsx            # Vite entry point
├── index.css           # Tailwind + DaisyUI config, custom theme tokens
├── api.ts              # Typed fetch client — all API calls live here
├── types.ts            # TypeScript interfaces (mirrors backend Pydantic schemas)
├── components/
│   ├── CalculatorView.tsx      # Recipe calculator UI
│   ├── CompositionTable.tsx    # Composition breakdown table
│   ├── FileUploadModal.tsx     # JSON import file picker modal
│   ├── FreezingSection.tsx     # Freezing curve chart (Recharts)
│   ├── HomePage.tsx            # Landing page
│   ├── IngredientFormModal.tsx # Create/edit ingredient form
│   ├── IngredientPanel.tsx     # Single ingredient row in calculator
│   ├── IngredientSearch.tsx    # Ingredient search modal
│   ├── IngredientsView.tsx     # Browse/search ingredients
│   ├── MetricCards.tsx         # Key metric summary cards
│   ├── NutritionTable.tsx      # Nutrition facts table
│   ├── ProfileFormModal.tsx    # Create/edit target profile form
│   ├── ProfilesView.tsx        # Browse/manage target profiles
│   ├── RecentRecipes.tsx       # Recent recipes list (homepage)
│   ├── RecipeHeader.tsx        # Recipe name + save/delete controls
│   ├── RecipePickerModal.tsx   # Load/save recipe modal
│   ├── RecipesView.tsx         # Browse/manage recipes
│   ├── SweetnessSection.tsx    # POD breakdown chart
│   └── ThemeToggle.tsx         # Dark/light/system theme selector
├── hooks/
│   ├── useRecipeCalculator.ts  # Calculator state: rows, results, debounced calculation
│   ├── useTheme.ts             # Dark/light theme state (localStorage)
│   ├── useToast.ts             # Toast notification consumer
│   ├── useDebouncedValue.ts    # Generic debounce hook
│   └── ToastProvider.tsx       # Toast context provider
└── lib/
    ├── formatting.ts   # Number formatting, unit conversions
    ├── tooltips.ts     # Tooltip string library for InfoIcon components
    └── validation.ts   # Form validation helpers
```

---

## Coding Conventions

### TypeScript

- **Strict mode** is enabled. All types must be explicit — no implicit `any`.
- Use `interface` for object shapes that extend or are implemented. Use `type` for unions, intersections, and aliases.
- Prefer `const` over `let`; never use `var`.
- All API response shapes are defined in `types.ts` — import from there, do not redeclare inline.
- Prefer named exports over default exports for components and hooks. `App.tsx` is the exception (default export required by Vite).

### React

- Use **functional components** with hooks — no class components (the `ErrorBoundary` in `App.tsx` is the only necessary exception).
- Memoize expensive derived values with `useMemo`; memoize callbacks passed to child components with `useCallback`.
- Do not use `useEffect` for data fetching — use TanStack Query (`useQuery`) instead.
- Use `React.ReactNode` as the type for children props.
- Mark props interfaces as `Readonly<>` when the component does not mutate them (enforced by the linter).

### File Naming

- Component files: `PascalCase.tsx` (e.g. `IngredientPanel.tsx`)
- Hook files: `camelCase.ts` prefixed with `use` (e.g. `useTheme.ts`)
- Utility files: `camelCase.ts` (e.g. `formatting.ts`)
- One component per file.

---

## API Client

All API calls go through functions defined in `frontend/src/api.ts`. Never call `fetch` directly in a component or hook.

### Base Request Function

```typescript
async function request<T>(path: string, init?: RequestInit): Promise<T>;
```

This function:

- Prepends `/api/v1` to the path
- Sets `Content-Type: application/json` on requests with a body
- Throws an `Error` with the server error message on non-2xx responses
- Returns `undefined` (cast to `T`) for `204 No Content` responses

### Available Functions

```typescript
// Ingredients
fetchIngredients(params?: { q?: string; category_id?: number; source?: string; offset?: number; limit?: number }, signal?: AbortSignal)
fetchIngredient(id: string)
createIngredient(data: IngredientInput)
updateIngredient(id: string, data: IngredientInput)
deleteIngredient(id: string)

// Categories
fetchCategories()

// Recipes
fetchRecipes()
fetchRecipe(id: string)
createRecipe(data)
updateRecipe(id: string, data)
deleteRecipe(id: string)
exportRecipe(id: string)
exportAllRecipes()
importRecipes(file: File)

// Target Profiles
fetchProfiles()
createProfile(data: TargetProfileInput)
updateProfile(id: number, data: TargetProfileInput)
deleteProfile(id: number)

// Calculator
calculate(data: CalculateRequest): Promise<CalculateResponse>
```

### Adding a New API Call

1. Add a new exported function to `api.ts` that uses `request<T>()`.
2. Add the corresponding TypeScript type to `types.ts` if a new response shape is needed.
3. Use the new function from a hook (not directly from a component).

```typescript
// api.ts
export async function fetchMyThing(id: string): Promise<MyThing> {
  return request<MyThing>(`/my-things/${id}`);
}
```

---

## Type System

Types are defined in `frontend/src/types.ts` using **Zod** for runtime validation and TypeScript inference.

### Structure

```typescript
import { z } from "zod";

// Define a Zod schema
const IngredientSchema = z.object({
  id: z.string(),
  name: z.string(),
  water_pct: z.number().nullable(),
  // ...
});

// Derive the TypeScript type from the schema
export type Ingredient = z.infer<typeof IngredientSchema>;
```

### Numeric Field Preprocessors

Form inputs return strings, but the API expects numbers or `null`. Use the `numericNullable` preprocessor for optional numeric fields in form schemas:

```typescript
const numericNullable = z.preprocess(
  (v) => (v === "" || v === null || v === undefined ? null : Number(v)),
  z.number().nullable(),
);
```

Apply this to all optional numeric composition fields in `IngredientInput`.

### Key Types

| Type                | Description                                 |
| ------------------- | ------------------------------------------- |
| `Ingredient`        | Full ingredient with all composition fields |
| `IngredientInput`   | Form input type for create/update           |
| `Recipe`            | Recipe with nested `RecipeIngredientOut[]`  |
| `CalculateRequest`  | Payload for `POST /calculate`               |
| `CalculateResponse` | Full calculation result                     |
| `CompositionResult` | Percentages for all composition metrics     |
| `PACResult`         | `pac_mix` and `pac_water` values            |
| `FreezingResult`    | Freezing point, serving temp, curve data    |
| `SweetnessResult`   | POD value and per-ingredient breakdown      |
| `NutritionResult`   | Per-100g and per-serving nutrition facts    |
| `TargetProfile`     | Named ranges for metric comparison          |
| `MetricComparison`  | Single metric's value vs. target range      |

---

## State Management

### Server State — TanStack Query

Use `useQuery` and `useMutation` for all server-fetched data:

```typescript
import { useQuery } from "@tanstack/react-query";
import { fetchCategories } from "../api";

function MyComponent() {
  const { data: categories, isLoading } = useQuery({
    queryKey: ["ingredient-categories"],
    queryFn: fetchCategories,
  });
}
```

Query keys follow the pattern `[resource-name]` for lists and `[resource-name, id]` for single items.

After a mutation, invalidate the relevant query to trigger a refetch:

```typescript
const qc = useQueryClient();
qc.invalidateQueries({ queryKey: ["recipes"] });
```

### Client / UI State — React Hooks

UI state (open modals, form values, calculator rows) lives in custom hooks or `useState` in the nearest relevant component. The `useRecipeCalculator` hook is the primary example — it manages the full calculator state including debounced API calls.

---

## Routing

The app uses **React Router v7** (`react-router-dom`).

Routes are defined in `App.tsx`:

| Path                       | Component         | Description                            |
| -------------------------- | ----------------- | -------------------------------------- |
| `/`                        | `HomePage`        | Landing page                           |
| `/calculator`              | `CalculatorView`  | Recipe calculator (empty)              |
| `/calculator/:recipeId`    | `CalculatorView`  | Recipe calculator (loads saved recipe) |
| `/recipes`                 | `RecipesView`     | Browse/manage recipes                  |
| `/profiles`                | `ProfilesView`    | Manage target profiles                 |
| `/ingredients`             | `IngredientsView` | Browse ingredients                     |
| `*`                        | Inline 404        | Not found                              |

### Navigation

Use `NavLink` for navigation items (applies active styles automatically) and `Link` for other internal links. Never use `<a href>` for internal navigation.

```tsx
import { NavLink, Link } from "react-router-dom";

// Navigation (active styling)
<NavLink to="/calculator" className={({ isActive }) => isActive ? activeClass : inactiveClass}>
    Calculator
</NavLink>

// Regular link
<Link to="/">Home</Link>
```

### Adding a New Page

1. Create `frontend/src/components/MyPage.tsx`.
2. Add a `<Route>` in `App.tsx`.
3. Add a `<NavLink>` in the `Header` component if it should appear in the navigation bar.

---

## UI & Design Conventions

### CSS Stack

- **Tailwind CSS v4** — utility classes via the `@tailwindcss/vite` plugin. There is no `tailwind.config.js`; configuration is in `index.css`.
- **DaisyUI v5** — semantic component library on top of Tailwind. Imported via `@plugin "daisyui"` in `index.css`.

### Colour Palette

Always use **DaisyUI semantic tokens** in preference to raw Tailwind colour classes like `gray-100`. This ensures colours adapt correctly between light and dark themes.

| Token                         | Use                                               |
| ----------------------------- | ------------------------------------------------- |
| `bg-base-100`                 | Primary background (cards, modals)                |
| `bg-base-200`                 | Page background                                   |
| `bg-base-300`                 | Subtle borders, dividers                          |
| `text-base-content`           | Primary text                                      |
| `text-base-content/60`        | Secondary / muted text                            |
| `border-base-200`             | Default border colour                             |
| `bg-primary` / `text-primary` | Pink accent (interactive elements, active states) |

Do **not** use raw colour classes like `bg-gray-100`, `text-gray-600`, or `border-gray-200` — these do not adapt to dark mode.

### DaisyUI Component Classes

Prefer DaisyUI component classes over manually composing Tailwind utilities for common UI patterns:

```tsx
// Buttons
<button className="btn btn-primary">Save</button>
<button className="btn btn-ghost btn-sm">Cancel</button>

// Inputs
<input className="input input-bordered w-full" />
<select className="select select-bordered" />

// Tables
<table className="table">...</table>

// Badges
<span className="badge badge-primary">Active</span>

// Join (group inputs/buttons)
<div className="join">
    <input className="input join-item" />
    <button className="btn join-item">Search</button>
</div>
```

### Layout

- Maximum content width: `max-w-7xl mx-auto px-4` (matches the header).
- Use `gap-*` on flex/grid containers rather than margin on individual children.
- Vertical spacing between sections: `py-6` or `py-8`.

### Typography

- Page headings: `text-2xl font-bold` or `text-xl font-semibold`
- Section headings: `text-lg font-semibold`
- Labels: `text-sm font-medium text-base-content/70`
- Muted/secondary text: `text-base-content/60`

### Icons

Use **Lucide React** (`lucide-react`) for all icons. Import only the icons you use:

```tsx
import { Plus, Trash2, Search } from "lucide-react";

<Plus size={16} />;
```

Default icon size in buttons: `16`. Larger standalone icons: `20` or `24`.

### Loading & Error States

- Show a spinner or skeleton for loading states using DaisyUI's `loading` class.
- Show toast notifications for non-blocking errors using the `useToast` hook.
- Show inline error messages for form validation.

---

## Theming (Dark / Light Mode)

The app supports three theme modes: `light`, `dark`, and `system` (follows OS preference). Theme state is persisted in `localStorage`.

### How It Works

Two mechanisms are used simultaneously for full compatibility:

1. **Tailwind dark mode** — A `.dark` class on `<html>` enables `dark:` variant classes.
2. **DaisyUI themes** — A `data-theme="dark"` or `data-theme="light"` attribute on `<html>` enables DaisyUI's theme tokens.

Both are set together by `useTheme.ts` whenever the theme changes.

### Anti-FOUC (Flash of Unstyled Content)

An inline script in `index.html` runs synchronously before React renders to apply the correct theme immediately, preventing a flash of the wrong theme on page load.

### Using the Theme in Components

- Use `dark:` Tailwind variants for things DaisyUI tokens don't cover.
- Use DaisyUI semantic tokens (e.g. `bg-base-100`, `text-base-content`) for everything else — they switch automatically.
- Do **not** read the theme from `localStorage` directly in components; use the `useTheme` hook if needed.

### Primary Colour

The primary (accent) colour is **pink**:

- Light mode: `oklch(0.656 0.178 353)` ≈ `#ec4899`
- Dark mode: `oklch(0.718 0.152 350)` ≈ `#f472b6`

Defined as CSS custom properties in `index.css` and accessible via `text-primary`, `bg-primary`, etc.

---

## Component Patterns

### Pure Display Components

Components receive all data as props and emit events via callback props. They do not fetch data or manage server state.

```tsx
interface Props {
  ingredients: Ingredient[];
  onSelect: (ingredient: Ingredient) => void;
}

export function IngredientList({ ingredients, onSelect }: Readonly<Props>) {
  return (
    <ul>
      {ingredients.map((ing) => (
        <li key={ing.id}>
          <button onClick={() => onSelect(ing)}>{ing.name}</button>
        </li>
      ))}
    </ul>
  );
}
```

### Modal Pattern

Modals are controlled components. The parent controls `isOpen` and provides an `onClose` callback:

```tsx
interface Props {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: (value: string) => void;
}

export function MyModal({ isOpen, onClose, onConfirm }: Readonly<Props>) {
  if (!isOpen) return null;
  // ...
}
```

### Forms

Use controlled inputs with local `useState` for form state. Validate with Zod schemas from `types.ts`:

```tsx
const [value, setValue] = useState("");

const handleSubmit = (e: React.FormEvent) => {
  e.preventDefault();
  const parsed = MySchema.safeParse({ value });
  if (!parsed.success) {
    // show validation error
    return;
  }
  onSubmit(parsed.data);
};
```

### Charts (Recharts)

Recharts is used for the freezing curve chart in `FreezingSection.tsx`. Charts are responsive — always wrap in a `ResponsiveContainer`:

```tsx
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  ResponsiveContainer,
  Tooltip,
} from "recharts";

<ResponsiveContainer width="100%" height={200}>
  <LineChart data={curveData}>
    <XAxis dataKey="temperature_c" />
    <YAxis />
    <Tooltip />
    <Line
      type="monotone"
      dataKey="frozen_pct"
      stroke="var(--color-primary)"
      dot={false}
    />
  </LineChart>
</ResponsiveContainer>;
```

---

## Hooks

### `useRecipeCalculator`

The main calculator hook. Manages:

- `rows: RecipeRow[]` — ingredients in the current recipe with weights
- `result: CalculateResponse | null` — latest calculation result
- `loading: boolean` — whether a calculation is in flight
- `profile: TargetProfile | null` — selected target profile
- `currentRecipe: Recipe | null` — saved recipe being edited

API: `addIngredient`, `removeIngredient`, `updateWeight`, `changeProfile`, `loadRecipe`, `saveAsNewRecipe`, `saveCurrentRecipe`, `deleteCurrentRecipe`, `clearRecipe`.

Calculation is **debounced** — any change to `rows` or `profile` triggers a `POST /calculate` after 300 ms.

### `useTheme`

Manages theme state (`light` | `dark` | `system`). Persists to `localStorage` and applies classes to `<html>` immediately on change.

### `useToast`

Provides `addToast(message: string)` for showing transient notifications. Requires `<ToastProvider>` in the component tree (already present in `App.tsx`).

### `useDebouncedValue`

Generic hook that delays updating a value until a specified delay has passed with no new value:

```typescript
const debouncedSearch = useDebouncedValue(searchQuery, 300);
```

### Writing a New Hook

- Name the file `useCamelCase.ts`.
- Export a single function named identically to the file.
- Keep the hook focused on a single responsibility.
- If the hook fetches data, use `useQuery` from TanStack Query.
- Return a stable object (use `useMemo` if necessary to avoid unnecessary re-renders).

---

## Type Checking & Building

```bash
cd frontend

# Type check only (no output files)
pnpm tsc --noEmit

# Production build
pnpm build

# Development server
pnpm dev
```

After making any change to a `.tsx` or `.ts` file, run `pnpm tsc --noEmit` to check for type errors before committing. The CI pipeline will fail on type errors.
