"use client";

import { useRouter } from "next/navigation";
import { useMutation, useQuery } from "@tanstack/react-query";
import toast from "react-hot-toast";

import { AuthGuard } from "@/components/layout/auth-guard";
import { Button } from "@/components/ui/button";
import { Panel } from "@/components/ui/panel";
import { api } from "@/services/api";

export default function NewGamePage() {
  const router = useRouter();
  const cases = useQuery({ queryKey: ["cases"], queryFn: api.cases });

  const start = useMutation({
    mutationFn: (caseId: number) => api.startInvestigation(caseId),
    onSuccess: (result) => {
      toast.success("Investigation started.");
      router.push(`/investigation/${result.id}/briefing`);
    },
    onError: (error) => toast.error(error instanceof Error ? error.message : "Could not start")
  });

  return (
    <AuthGuard>
      <main className="mx-auto max-w-4xl p-4">
        <h1 className="text-5xl">New Investigation</h1>
        <Panel className="mt-4" title="Case Selection">
          {cases.isLoading ? <p>Loading case files...</p> : null}
          {cases.data?.map((c) => (
            <div key={c.id} className="mb-3 rounded-xl border border-white/10 bg-white/5 p-3">
              <p className="text-2xl">{c.title}</p>
              <p className="text-sm text-white/70">Single polished mystery scenario.</p>
              <Button className="mt-2" onClick={() => start.mutate(c.id)} disabled={start.isPending}>
                {start.isPending ? "Preparing..." : "Start Case"}
              </Button>
            </div>
          ))}
        </Panel>
      </main>
    </AuthGuard>
  );
}
