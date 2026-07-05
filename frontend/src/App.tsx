import React, { useState, useEffect, useRef } from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route, NavLink, Link } from "react-router-dom";
import { CalculatorView } from "./components/CalculatorView";
import { IngredientsView } from "./components/IngredientsView";
import { RecipesView } from "./components/RecipesView";
import { ProfilesView } from "./components/ProfilesView";
import { HomePage } from "./components/HomePage";
import { ThemeToggle } from "./components/ThemeToggle";
import { useTheme, type Theme } from "./hooks/useTheme";
import { ToastProvider } from "./hooks/ToastProvider";
import { ArrowLeft, IceCreamCone, Menu, X } from "lucide-react";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 30_000, // data is fresh for 30s — avoids refetch on navigation
      refetchOnWindowFocus: false, // prevents refetch on tab switch
      retry: 1, // one retry is enough for these endpoints
    },
  },
});

const navActive =
  "px-3 py-1.5 text-sm rounded-md font-medium bg-primary/10 text-primary";
const navInactive =
  "px-3 py-1.5 text-sm rounded-md font-medium text-base-content/60 hover:text-base-content transition-colors";

function Header({ theme, setTheme }: Readonly<{ theme: Theme; setTheme: (t: Theme) => void }>) {
  const [menuOpen, setMenuOpen] = useState(false);
  const menuButtonRef = useRef<HTMLButtonElement>(null);
  const mobileNavRef = useRef<HTMLDivElement>(null);

  function closeMenu() {
    setMenuOpen(false);
  }

  // Dismiss mobile menu with Escape key
  useEffect(() => {
    if (!menuOpen) return;
    function onKeyDown(e: KeyboardEvent) {
      if (e.key === "Escape") closeMenu();
    }
    document.addEventListener("keydown", onKeyDown);
    return () => document.removeEventListener("keydown", onKeyDown);
  }, [menuOpen]);

  // Focus management: move focus to first link when menu opens,
  // return focus to hamburger button when menu closes
  const wasOpenRef = useRef(false);
  useEffect(() => {
    if (menuOpen) {
      wasOpenRef.current = true;
      // use rAF to let React finish painting the DOM first
      requestAnimationFrame(() => {
        const firstLink =
          mobileNavRef.current?.querySelector<HTMLAnchorElement>("a");
        firstLink?.focus();
      });
    } else if (wasOpenRef.current) {
      wasOpenRef.current = false;
      menuButtonRef.current?.focus();
    }
  }, [menuOpen]);

  return (
    <header className="bg-base-100 border-b border-base-200 px-4 py-3">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        <div className="flex items-center gap-6">
          <Link to="/" className="flex items-center gap-2 hover:opacity-80 transition-opacity" onClick={closeMenu}>
            <IceCreamCone className="text-primary" size={24} />
            <h1 className="text-xl font-bold tracking-tight">iscreami</h1>
          </Link>
          <nav aria-label="Main navigation" className="hidden md:flex items-center gap-1">
            <NavLink
              to="/calculator"
              className={({ isActive }) => isActive ? navActive : navInactive}
            >
              Calculator
            </NavLink>
            <NavLink
              to="/ingredients"
              className={({ isActive }) => isActive ? navActive : navInactive}
            >
              Ingredients
            </NavLink>
            <NavLink
              to="/recipes"
              className={({ isActive }) => isActive ? navActive : navInactive}
            >
              Recipes
            </NavLink>
            <NavLink
              to="/profiles"
              className={({ isActive }) => isActive ? navActive : navInactive}
            >
              Profiles
            </NavLink>
          </nav>
        </div>
        <div className="hidden md:block">
          <ThemeToggle theme={theme} setTheme={setTheme} />
        </div>
        <button
          type="button"
          ref={menuButtonRef}
          className="md:hidden btn btn-ghost btn-sm"
          onClick={() => setMenuOpen((o) => !o)}
          aria-label={menuOpen ? "Close menu" : "Open menu"}
          aria-expanded={menuOpen}
        >
          {menuOpen ? <X size={20} /> : <Menu size={20} />}
        </button>
      </div>

      {/* Mobile menu */}
      {menuOpen && (
        <div ref={mobileNavRef} className="md:hidden border-t border-base-200 mt-3 pt-3 max-w-7xl mx-auto">
          <nav aria-label="Main navigation" className="flex flex-col gap-1 mb-3">
            <NavLink
              to="/calculator"
              className={({ isActive }) => isActive ? navActive : navInactive}
              onClick={closeMenu}
            >
              Calculator
            </NavLink>
            <NavLink
              to="/ingredients"
              className={({ isActive }) => isActive ? navActive : navInactive}
              onClick={closeMenu}
            >
              Ingredients
            </NavLink>
            <NavLink
              to="/recipes"
              className={({ isActive }) => isActive ? navActive : navInactive}
              onClick={closeMenu}
            >
              Recipes
            </NavLink>
            <NavLink
              to="/profiles"
              className={({ isActive }) => isActive ? navActive : navInactive}
              onClick={closeMenu}
            >
              Profiles
            </NavLink>
          </nav>
          <div className="pt-3 border-t border-base-200">
            <ThemeToggle theme={theme} setTheme={setTheme} />
          </div>
        </div>
      )}
    </header>
  );
}

const skipLinkStyle =
  "sr-only focus:not-sr-only focus:fixed focus:top-4 focus:left-4 focus:z-[10000] focus:px-4 focus:py-2 focus:bg-primary focus:text-primary-content focus:rounded-lg focus:shadow-lg focus:outline-none focus:text-sm focus:font-medium";

function AppContent() {
  const { theme, setTheme } = useTheme();
  return (
    <div className="min-h-screen bg-base-200 text-base-content">
      <a href="#main-content" className={skipLinkStyle}>
        Skip to main content
      </a>
      <Header theme={theme} setTheme={setTheme} />
      <div id="main-content" tabIndex={-1} className="outline-none">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/calculator" element={<CalculatorView />} />
          <Route path="/calculator/:recipeId" element={<CalculatorView />} />
          <Route path="/recipes" element={<RecipesView />} />
          <Route path="/profiles" element={<ProfilesView />} />
          <Route path="/ingredients" element={<IngredientsView />} />
          <Route
            path="*"
            element={
              <main className="max-w-7xl mx-auto px-4 py-16 text-center">
                <p className="text-4xl font-bold mb-4">404</p>
                <p className="text-base-content/60 mb-6">Page not found.</p>
                <Link
                  to="/"
                  className="inline-flex items-center gap-2 btn btn-primary"
                >
                  <ArrowLeft size={16} />
                  Back to Home
                </Link>
              </main>
            }
          />
        </Routes>
      </div>
    </div>
  );
}

class ErrorBoundary extends React.Component<
  { children: React.ReactNode },
  { hasError: boolean }
> {
  constructor(props: { children: React.ReactNode }) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(): { hasError: boolean } {
    return { hasError: true };
  }

  render() {
    if (this.state.hasError) {
      return (
        <main className="min-h-screen bg-base-200 flex items-center justify-center">
          <div className="text-center">
            <p className="text-2xl font-bold mb-2">Something went wrong</p>
            <p className="text-base-content/60 mb-6">An unexpected error occurred.</p>
            <button className="btn btn-primary" onClick={() => globalThis.location.reload()}>
              Reload
            </button>
          </div>
        </main>
      );
    }
    return this.props.children;
  }
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <ToastProvider>
          <ErrorBoundary>
            <AppContent />
          </ErrorBoundary>
        </ToastProvider>
      </BrowserRouter>
    </QueryClientProvider>
  );
}
