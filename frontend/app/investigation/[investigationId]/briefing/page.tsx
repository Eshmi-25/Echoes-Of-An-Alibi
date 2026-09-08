"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";

import { AuthGuard } from "@/components/layout/auth-guard";
import { AppShell } from "@/components/layout/app-shell";
import { Panel } from "@/components/ui/panel";
import { api } from "@/services/api";

export default function BriefingPage() {
  const params = useParams<{ investigationId: string }>();
  const id = Number(params.investigationId);
  const inv = useQuery({ queryKey: ["investigation", id], queryFn: () => api.investigation(id) });

  const caseId = inv.data?.case_id;
  const caseQuery = useQuery({
    queryKey: ["case", caseId],
    queryFn: () => api.caseById(caseId as number),
    enabled: Boolean(caseId)
  });

  return (
    <AuthGuard>
      <AppShell investigationId={params.investigationId}>
        <Panel title="Case Briefing">
          <h1 className="text-4xl">The Midnight Gallery</h1>
          <p className="mt-3 text-white/80">{caseQuery.data?.briefing ?? "Loading briefing..."}</p>
          <p className="mt-3 text-sm text-white/70">Actions available: {inv.data?.actions_remaining ?? "..."}</p>
          <Link href={`/investigation/${id}`} className="mt-4 inline-block rounded-lg bg-noir-amber px-4 py-2 font-semibold text-black">
            Enter Headquarters
          </Link>
        </Panel>
      </AppShell>
    </AuthGuard>
  );
}
