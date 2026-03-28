import { Link } from "react-router-dom";
import { IceCreamCone, FlaskConical, BookOpen } from "lucide-react";
import { RecentRecipes } from "./RecentRecipes";

export function HomePage() {
  return (
    <main className="max-w-3xl mx-auto px-4 py-16 text-center">
      <IceCreamCone className="mx-auto text-primary mb-6" size={64} />
      <h2 className="text-3xl font-bold tracking-tight mb-3">
        Welcome to iscreami
      </h2>
      <p className="text-base-content/60 text-lg mb-12">
        Open-source ice cream recipe calculator. Build recipes, analyse
        composition, and optimise sweetness &amp; freezing point.
      </p>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-left mb-12">
        <Link
          to="/calculator"
          className="group flex items-start gap-4 bg-base-100 rounded-xl border border-base-200 p-5 shadow-sm hover:border-primary/50 transition-colors"
        >
          <FlaskConical
            className="text-pink-400 mt-0.5 shrink-0 group-hover:scale-110 transition-transform"
            size={28}
          />
          <div>
            <h3 className="font-semibold text-base-content mb-1">
              Calculator
            </h3>
            <p className="text-sm text-base-content/60">
              Build a recipe, adjust ingredient weights, and see real-time PAC,
              sweetness, and composition results.
            </p>
          </div>
        </Link>

        <Link
          to="/ingredients"
          className="group flex items-start gap-4 bg-base-100 rounded-xl border border-base-200 p-5 shadow-sm hover:border-primary/50 transition-colors"
        >
          <BookOpen
            className="text-primary mt-0.5 shrink-0 group-hover:scale-110 transition-transform"
            size={28}
          />
          <div>
            <h3 className="font-semibold text-base-content mb-1">
              Ingredients
            </h3>
            <p className="text-sm text-base-content/60">
              Browse and search the ingredient database, including nutritional
              data from USDA and NZ FOODfiles.
            </p>
          </div>
        </Link>
      </div>

      <div className="mt-16 text-left">
        <h3 className="text-lg font-semibold mb-4">Recent Recipes</h3>
        <RecentRecipes />
      </div>
    </main>
  );
}
