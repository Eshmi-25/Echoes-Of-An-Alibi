"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";

import { AuthGuard } from "@/components/layout/auth-guard";
import { AppShell } from "@/components/layout/app-shell";
import { Panel } from "@/components/ui/panel";
import { api } from "@/services/api";

export default function ResultPage() {
  const params = useParams<{ investigationId: string }>();
  const id = Number(params.investigationId);
  const result = useQuery({ queryKey: ["result", id], queryFn: () => api.result(id) });

  return (
    <AuthGuard>
      <AppShell investigationId={params.investigationId}>
        <Panel title="Case Ending">
          {result.isLoading ? <p>Scoring accusation...</p> : null}
          {result.data ? (
            <>
              <h1 className="text-4xl">{result.data.ending_title}</h1>
              <p className="mt-2 text-white/80">{result.data.ending_summary}</p>
              <p className="mt-3 text-xl text-noir-amber">Score: {result.data.score}</p>
              <div className="mt-4 flex gap-2">
                <Link href={`/investigation/${id}/review`} className="rounded-lg bg-noir-amber px-3 py-2 font-semibold text-black">Review Case</Link>
                <Link href="/investigation/new" className="rounded-lg border border-white/20 px-3 py-2">Start New Game</Link>
              </div>
            </>
          ) : (
            <p>No result yet. Submit your accusation first.</p>
          )}
        </Panel>
      </AppShell>
    </AuthGuard>
  );
}
