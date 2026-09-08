"use client";

import { useParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";

import { AuthGuard } from "@/components/layout/auth-guard";
import { AppShell } from "@/components/layout/app-shell";
import { Panel } from "@/components/ui/panel";
import { api } from "@/services/api";

export default function ReviewPage() {
  const params = useParams<{ investigationId: string }>();
  const id = Number(params.investigationId);

  const clues = useQuery({ queryKey: ["clues", id], queryFn: () => api.clues(id) });
  const contradictions = useQuery({ queryKey: ["contradictions", id], queryFn: () => api.contradictions(id) });
  const notes = useQuery({ queryKey: ["notes", id], queryFn: () => api.notes(id) });

  return (
    <AuthGuard>
      <AppShell investigationId={params.investigationId}>
        <h1 className="text-5xl">Completed Case Review</h1>
        <div className="mt-4 grid gap-4 md:grid-cols-3">
          <Panel title="Clues Found"><p>{clues.data?.length ?? 0}</p></Panel>
          <Panel title="Contradictions"><p>{contradictions.data?.length ?? 0}</p></Panel>
          <Panel title="Notes"><p>{notes.data?.length ?? 0}</p></Panel>
        </div>
      </AppShell>
    </AuthGuard>
  );
}
