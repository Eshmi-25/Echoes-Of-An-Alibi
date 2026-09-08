"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";

import { AuthGuard } from "@/components/layout/auth-guard";
import { AppShell } from "@/components/layout/app-shell";
import { Panel } from "@/components/ui/panel";
import { api } from "@/services/api";

export default function HeadquartersPage() {
  const params = useParams<{ investigationId: string }>();
  const id = Number(params.investigationId);

  const inv = useQuery({ queryKey: ["investigation", id], queryFn: () => api.investigation(id) });
  const locations = useQuery({ queryKey: ["locations", id], queryFn: () => api.locations(id) });
  const suspects = useQuery({ queryKey: ["suspects", id], queryFn: () => api.suspects(id) });
  const clues = useQuery({ queryKey: ["clues", id], queryFn: () => api.clues(id) });

  const unlockedLocations = locations.data?.filter((l) => l.unlocked).length ?? 0;
  const interviewed = suspects.data?.filter((s) => s.interviewed_count > 0).length ?? 0;

  return (
    <AuthGuard>
      <AppShell investigationId={params.investigationId}>
        <h1 className="text-5xl">Investigation HQ</h1>
        <p className="text-white/75">Current objective: reconstruct the timeline before filing accusation.</p>
        <div className="mt-4 grid gap-4 md:grid-cols-3">
          <Panel title="Progress">
            <p>Actions remaining: {inv.data?.actions_remaining ?? "..."}</p>
            <p>Clues found: {clues.data?.length ?? 0}</p>
            <p>Suspects interviewed: {interviewed}</p>
            <p>Unlocked locations: {unlockedLocations}</p>
          </Panel>
          <Panel title="Recently Found Clues">
            {clues.data?.slice(-4).map((c) => <p key={c.clue_slug}>- {c.title}</p>) ?? "No clues yet."}
          </Panel>
          <Panel title="Quick Navigation">
            <div className="grid gap-2 text-sm">
              <Link href={`/investigation/${id}/locations`} className="rounded-lg border border-white/15 px-3 py-2">Explore Locations</Link>
              <Link href={`/investigation/${id}/suspects`} className="rounded-lg border border-white/15 px-3 py-2">Interrogate Suspects</Link>
              <Link href={`/investigation/${id}/board`} className="rounded-lg border border-white/15 px-3 py-2">Evidence Board</Link>
              <Link href={`/investigation/${id}/timeline`} className="rounded-lg border border-white/15 px-3 py-2">Timeline</Link>
            </div>
          </Panel>
        </div>
      </AppShell>
    </AuthGuard>
  );
}
