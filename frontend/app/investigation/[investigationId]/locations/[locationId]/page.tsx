"use client";

import { useParams, useRouter } from "next/navigation";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import toast from "react-hot-toast";

import { AuthGuard } from "@/components/layout/auth-guard";
import { AppShell } from "@/components/layout/app-shell";
import { Button } from "@/components/ui/button";
import { Panel } from "@/components/ui/panel";
import { api } from "@/services/api";

export default function LocationDetailPage() {
  const params = useParams<{ investigationId: string; locationId: string }>();
  const id = Number(params.investigationId);
  const locationId = params.locationId;
  const queryClient = useQueryClient();
  const router = useRouter();

  const location = useQuery({ queryKey: ["location", id, locationId], queryFn: () => api.location(id, locationId) });

  const search = useMutation({
    mutationFn: () => api.searchLocation(id, locationId),
    onSuccess: (result) => {
      queryClient.invalidateQueries({ queryKey: ["locations", id] });
      queryClient.invalidateQueries({ queryKey: ["investigation", id] });
      queryClient.invalidateQueries({ queryKey: ["clues", id] });
      toast.success(`Found ${result.found_clues.length} clue(s)`);
      if (result.newly_unlocked_locations.length || result.newly_unlocked_suspects.length) {
        toast.success("New leads unlocked.");
      }
    },
    onError: (error) => toast.error(error instanceof Error ? error.message : "Search failed")
  });

  return (
    <AuthGuard>
      <AppShell investigationId={params.investigationId}>
        <Panel title="Location Detail">
          <h1 className="text-4xl">{String(location.data?.name ?? locationId)}</h1>
          <p className="mt-2 text-white/80">{String(location.data?.description ?? "Loading...")}</p>
          <div className="mt-4 flex gap-3">
            <Button onClick={() => search.mutate()} disabled={search.isPending}>
              {search.isPending ? "Searching..." : "Search Location (1 action)"}
            </Button>
            <Button className="bg-white/20 text-white" onClick={() => router.push(`/investigation/${id}/locations`)}>
              Back to Locations
            </Button>
          </div>
        </Panel>
      </AppShell>
    </AuthGuard>
  );
}
