import { useQuery } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { X, IceCreamCone } from "lucide-react";
import { fetchRecipes } from "../api";

interface Props {
    open: boolean;
    onClose: () => void;
}

export function RecipePickerModal({ open, onClose }: Readonly<Props>) {
    const navigate = useNavigate();
    const { data, isLoading } = useQuery({
        queryKey: ["recipes"],
        queryFn: fetchRecipes,
        enabled: open,
    });

    function handleSelectRecipe(recipeId: string) {
        navigate(`/calculator/${recipeId}`);
        onClose();
    }

    if (!open) return null;

    return (
        <div className="modal modal-open">
            <div className="modal-box max-w-md">
                <div className="flex items-center justify-between mb-4">
                    <h3 className="font-bold text-lg">Load Recipe</h3>
                    <button
                        type="button"
                        className="btn btn-ghost btn-sm btn-circle"
                        onClick={onClose}
                        aria-label="Close"
                    >
                        <X size={16} />
                    </button>
                </div>

                {isLoading && (
                    <div className="flex justify-center py-8">
                        <span className="loading loading-spinner loading-md" />
                    </div>
                )}

                {!isLoading && (!data || data.items.length === 0) && (
                    <div className="text-center py-8 text-base-content/40">
                        <IceCreamCone size={40} className="mx-auto mb-2" />
                        <p>No saved recipes yet.</p>
                    </div>
                )}

                {!isLoading && data && data.items.length > 0 && (
                    <ul className="space-y-2 max-h-96 overflow-y-auto">
                        {data.items.map((recipe) => (
                            <li key={recipe.id}>
                                <button
                                    type="button"
                                    className="w-full text-left rounded-lg border border-base-200 bg-base-100 hover:bg-base-200 px-4 py-3 transition-colors"
                                    onClick={() => handleSelectRecipe(recipe.id)}
                                >
                                    <p className="font-medium text-sm">{recipe.name}</p>
                                    <p className="text-xs text-base-content/50 mt-0.5">
                                        {recipe.ingredients.length} ingredient{recipe.ingredients.length === 1 ? "" : "s"}
                                        {" · "}
                                        {new Date(recipe.updated_at).toLocaleDateString()}
                                    </p>
                                </button>
                            </li>
                        ))}
                    </ul>
                )}
            </div>
            <button
                type="button"
                className="modal-backdrop"
                onClick={onClose}
                aria-label="Close"
            />
        </div>
    );
}
