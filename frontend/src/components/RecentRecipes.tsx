import { useQuery } from "@tanstack/react-query";
import { ChefHat } from "lucide-react";
import { fetchRecipes } from "../api";
import { RecipeCard } from "./RecipeCard";

export function RecentRecipes() {
  const { data, isLoading, error } = useQuery({
    queryKey: ["recipes"],
    queryFn: fetchRecipes,
  });

  const recentRecipes = data?.items.slice(0, 3) ?? [];

  if (isLoading) {
    return (
      <div className="flex justify-center py-8">
        <span className="loading loading-spinner loading-md" />
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="text-center py-8 text-base-content/40">
        <p>Could not load recipes</p>
      </div>
    );
  }

  if (recentRecipes.length === 0) {
    return (
      <div className="text-center py-8 text-base-content/40">
        <ChefHat size={32} className="mx-auto mb-2 opacity-50" />
        <p className="text-sm">No recipes yet. Start by creating one!</p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {recentRecipes.map((recipe) => (
        <RecipeCard key={recipe.id} recipe={recipe} />
      ))}
    </div>
  );
}
