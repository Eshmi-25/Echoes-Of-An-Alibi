"use client";

import { useParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";

import { AuthGuard } from "@/components/layout/auth-guard";
import { AppShell } from "@/components/layout/app-shell";
import { Panel } from "@/components/ui/panel";
import { api } from "@/services/api";

export default function TimelinePage() {
  const params = useParams<{ investigationId: string }>();
  const id = Number(params.investigationId);

  const clues = useQuery({ queryKey: ["clues", id], queryFn: () => api.clues(id) });
  const contradictions = useQuery({ queryKey: ["contradictions", id], queryFn: () => api.contradictions(id) });

  return (
    <AuthGuard>
      <AppShell investigationId={params.investigationId}>
        <Panel title="Reconstructed Timeline">
          <ol className="space-y-3 border-l border-noir-amber/60 pl-4">
            {clues.data?.map((clue, index) => (
              <li key={clue.clue_slug} className="relative">
                <span className="absolute -left-[23px] top-1 h-3 w-3 rounded-full bg-noir-amber" />
                <p className="text-sm text-white/60">Step {index + 1}</p>
                <p className="text-lg">{clue.title}</p>
              </li>
            ))}
          </ol>
          <p className="mt-4 text-sm text-white/70">Contradictions exposed: {contradictions.data?.length ?? 0}</p>
        </Panel>
      </AppShell>
    </AuthGuard>
  );
}
