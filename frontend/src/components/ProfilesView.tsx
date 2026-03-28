import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Plus, Pencil, Trash2 } from "lucide-react";
import { fetchProfiles, deleteProfile } from "../api";
import type { TargetProfile } from "../types";
import { ProfileFormModal } from "./ProfileFormModal";
import { useToast } from "../hooks/useToast";

function fmtRange(min: number | null | undefined, max: number | null | undefined): string {
  if (min == null && max == null) return "—";
  if (min == null) return `≤ ${max}`;
  if (max == null) return `≥ ${min}`;
  return `${min} to ${max}`;
}

export function ProfilesView() {
  const [modalOpen, setModalOpen] = useState(false);
  const [editingProfile, setEditingProfile] = useState<TargetProfile | null>(null);
  const [deletingProfile, setDeletingProfile] = useState<TargetProfile | null>(null);

  const qc = useQueryClient();
  const { addToast } = useToast();

  const { data: profiles, isLoading } = useQuery({
    queryKey: ["profiles"],
    queryFn: fetchProfiles,
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => deleteProfile(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["profiles"] });
      addToast("Profile deleted.", "success");
      setDeletingProfile(null);
    },
    onError: (err: Error) => {
      addToast(err.message, "error");
      setDeletingProfile(null);
    },
  });

  function openAdd() {
    setEditingProfile(null);
    setModalOpen(true);
  }

  function openEdit(profile: TargetProfile) {
    setEditingProfile(profile);
    setModalOpen(true);
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-6">
      <div className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div className="min-w-0">
          <h1 className="text-2xl font-bold">Profiles</h1>
          <p className="text-sm text-base-content/60 mt-1">
            Target ranges for recipe metrics. Assign a profile to a recipe to see how it compares.
          </p>
        </div>
        <button
          type="button"
          className="btn btn-primary btn-sm w-full sm:w-auto sm:shrink-0"
          onClick={openAdd}
        >
          <Plus size={15} />
          Add profile
        </button>
      </div>

      {/* Table */}
      <div className="bg-base-100 rounded-xl shadow-sm border border-base-200 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="table table-sm w-full">
            <thead>
              <tr className="border-b border-base-200 bg-base-200">
                <th className="text-left px-4 py-3 font-medium text-base-content/60">
                  Name
                </th>
                <th className="text-left px-4 py-3 font-medium text-base-content/60 whitespace-nowrap">
                  Total solids (%)
                </th>
                <th className="text-left px-4 py-3 font-medium text-base-content/60 whitespace-nowrap">
                  Total fat (%)
                </th>
                <th className="text-left px-4 py-3 font-medium text-base-content/60 whitespace-nowrap">
                  Serving temp (°C)
                </th>
                <th className="text-left px-4 py-3 font-medium text-base-content/60 whitespace-nowrap">
                  Sweetness (POD)
                </th>
                <th className="px-4 py-3" />
              </tr>
            </thead>
            <tbody>
              {isLoading && (
                <tr>
                  <td colSpan={6} className="text-center py-10 text-base-content/40 animate-pulse">
                    Loading…
                  </td>
                </tr>
              )}
              {!isLoading && profiles?.length === 0 && (
                <tr>
                  <td colSpan={6} className="text-center py-10 text-base-content/40">
                    No profiles found. Add one to get started.
                  </td>
                </tr>
              )}
              {profiles?.map((profile) => (
                <tr
                  key={profile.id}
                  className="border-b border-base-200 hover:bg-base-200/40 transition-colors"
                >
                  <td className="px-4 py-2.5 font-medium whitespace-nowrap">{profile.name}</td>
                  <td className="px-4 py-2.5 text-sm tabular-nums">
                    {fmtRange(profile.total_solids_min, profile.total_solids_max)}
                  </td>
                  <td className="px-4 py-2.5 text-sm tabular-nums">
                    {fmtRange(profile.total_fat_min, profile.total_fat_max)}
                  </td>
                  <td className="px-4 py-2.5 text-sm tabular-nums">
                    {fmtRange(profile.serving_temp_min, profile.serving_temp_max)}
                  </td>
                  <td className="px-4 py-2.5 text-sm tabular-nums">
                    {fmtRange(profile.sweetness_min, profile.sweetness_max)}
                  </td>
                  <td className="px-4 py-2.5">
                    <div className="flex justify-end gap-1">
                      <button
                        type="button"
                        className="btn btn-ghost btn-xs btn-circle"
                        aria-label="Edit"
                        onClick={() => openEdit(profile)}
                      >
                        <Pencil size={13} />
                      </button>
                      <button
                        type="button"
                        className="btn btn-ghost btn-xs btn-circle text-error"
                        aria-label="Delete"
                        onClick={() => setDeletingProfile(profile)}
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
      </div>

      {profiles && (
        <p className="text-xs text-base-content/40 mt-2">
          {profiles.length.toLocaleString()} profile{profiles.length === 1 ? "" : "s"} total
        </p>
      )}

      {modalOpen && (
        <ProfileFormModal
          key={editingProfile?.id ?? "new"}
          open
          profile={editingProfile}
          onClose={() => setModalOpen(false)}
        />
      )}

      {/* Delete confirmation */}
      <dialog className="modal" open={deletingProfile != null}>
        <div className="modal-box max-w-sm">
          <h3 className="font-bold text-lg">Delete profile?</h3>
          <p className="py-3 text-sm text-base-content/70">
            <span className="font-medium">{deletingProfile?.name}</span> will be
            permanently removed. If it's assigned to any recipes, deletion will be blocked.
          </p>
          <div className="modal-action">
            <button
              type="button"
              className="btn btn-ghost btn-sm"
              onClick={() => setDeletingProfile(null)}
            >
              Cancel
            </button>
            <button
              type="button"
              className="btn btn-error btn-sm"
              disabled={deleteMutation.isPending}
              onClick={() =>
                deletingProfile && deleteMutation.mutate(deletingProfile.id)
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
          <button onClick={() => setDeletingProfile(null)}>close</button>
        </form>
      </dialog>
    </div>
  );
}
