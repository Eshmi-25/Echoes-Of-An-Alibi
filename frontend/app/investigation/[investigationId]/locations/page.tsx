"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";

import { AuthGuard } from "@/components/layout/auth-guard";
import { AppShell } from "@/components/layout/app-shell";
import { Panel } from "@/components/ui/panel";
import { api } from "@/services/api";

export default function LocationsPage() {
  const params = useParams<{ investigationId: string }>();
  const id = Number(params.investigationId);
  const locations = useQuery({ queryKey: ["locations", id], queryFn: () => api.locations(id) });

  return (
    <AuthGuard>
      <AppShell investigationId={params.investigationId}>
        <Panel title="Exploration">
          <div className="grid gap-3 md:grid-cols-2">
            {locations.data?.map((loc) => (
              <div key={loc.location_slug} className="rounded-xl border border-white/15 bg-white/5 p-3">
                <h2 className="text-2xl">{loc.location_slug}</h2>
                <p className="text-sm text-white/70">Searches: {loc.searched_count}</p>
                {loc.unlocked ? (
                  <Link
                    href={`/investigation/${id}/locations/${loc.location_slug}`}
                    className="mt-2 inline-block rounded-lg bg-noir-amber px-3 py-2 text-sm font-semibold text-black"
                  >
                    Investigate
                  </Link>
                ) : (
                  <p className="mt-2 text-sm text-noir-danger">Locked</p>
                )}
              </div>
            ))}
          </div>
        </Panel>
      </AppShell>
    </AuthGuard>
  );
}
