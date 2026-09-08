"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";

import { AuthGuard } from "@/components/layout/auth-guard";
import { AppShell } from "@/components/layout/app-shell";
import { Panel } from "@/components/ui/panel";
import { api } from "@/services/api";

export default function SuspectsPage() {
  const params = useParams<{ investigationId: string }>();
  const id = Number(params.investigationId);
  const suspects = useQuery({ queryKey: ["suspects", id], queryFn: () => api.suspects(id) });

  return (
    <AuthGuard>
      <AppShell investigationId={params.investigationId}>
        <Panel title="Suspects">
          <div className="grid gap-3 md:grid-cols-2">
            {suspects.data?.map((sus) => (
              <div key={sus.suspect_slug} className="rounded-xl border border-white/15 bg-white/5 p-3">
                <h2 className="text-2xl">{sus.suspect_slug}</h2>
                <p className="text-sm text-white/70">Trust {sus.trust} / Pressure {sus.pressure}</p>
                <p className="text-sm text-white/70">Interviews: {sus.interviewed_count}</p>
                {sus.unlocked ? (
                  <Link
                    href={`/investigation/${id}/suspects/${sus.suspect_slug}`}
                    className="mt-2 inline-block rounded-lg bg-noir-amber px-3 py-2 text-sm font-semibold text-black"
                  >
                    Interrogate
                  </Link>
                ) : (
                  <p className="text-sm text-noir-danger">Locked</p>
                )}
              </div>
            ))}
          </div>
        </Panel>
      </AppShell>
    </AuthGuard>
  );
}
