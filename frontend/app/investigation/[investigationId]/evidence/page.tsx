"use client";

import { useParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";

import { AuthGuard } from "@/components/layout/auth-guard";
import { AppShell } from "@/components/layout/app-shell";
import { Panel } from "@/components/ui/panel";
import { api } from "@/services/api";

export default function EvidencePage() {
  const params = useParams<{ investigationId: string }>();
  const id = Number(params.investigationId);
  const clues = useQuery({ queryKey: ["clues", id], queryFn: () => api.clues(id) });
  const contradictions = useQuery({ queryKey: ["contradictions", id], queryFn: () => api.contradictions(id) });

  return (
    <AuthGuard>
      <AppShell investigationId={params.investigationId}>
        <div className="grid gap-4 md:grid-cols-2">
          <Panel title="Evidence Inventory">
            {clues.data?.length ? clues.data.map((c) => (
              <article key={c.clue_slug} className="mb-3 rounded-lg border border-white/10 bg-white/5 p-3">
                <h2 className="text-2xl">{c.title}</h2>
                <p className="text-sm text-white/80">{c.description}</p>
              </article>
            )) : <p className="text-white/70">No clues collected yet.</p>}
          </Panel>
          <Panel title="Contradictions">
            {contradictions.data?.length ? contradictions.data.map((c) => (
              <article key={c.slug} className="mb-3 rounded-lg border border-noir-danger/30 bg-noir-danger/10 p-3">
                <h2 className="text-2xl">{c.title}</h2>
                <p className="text-sm text-white/80">{c.description}</p>
              </article>
            )) : <p className="text-white/70">None exposed yet.</p>}
          </Panel>
        </div>
      </AppShell>
    </AuthGuard>
  );
}
