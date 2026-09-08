"use client";

import Link from "next/link";
import { useQuery } from "@tanstack/react-query";

import { AuthGuard } from "@/components/layout/auth-guard";
import { Panel } from "@/components/ui/panel";
import { api } from "@/services/api";

export default function DashboardPage() {
  const investigations = useQuery({ queryKey: ["investigations"], queryFn: api.investigations });

  return (
    <AuthGuard>
      <main className="mx-auto max-w-5xl p-4">
        <h1 className="text-5xl">Detective Dashboard</h1>
        <div className="mt-4 grid gap-4 md:grid-cols-2">
          <Panel title="Active Investigation">
            {investigations.isLoading ? <p>Loading cases...</p> : null}
            {investigations.data && investigations.data.length > 0 ? (
              <div>
                <p className="text-white/80">Case progress is tracked server-side.</p>
                <p className="mt-2 text-sm">Actions remaining: {investigations.data[0].actions_remaining}</p>
                <Link
                  href={`/investigation/${investigations.data[0].id}`}
                  className="mt-4 inline-block rounded-lg bg-noir-amber px-3 py-2 font-semibold text-black"
                >
                  Continue game
                </Link>
              </div>
            ) : (
              <p className="text-white/75">No active game yet.</p>
            )}
          </Panel>
          <Panel title="Start Case">
            <p className="text-white/80">Begin or restart The Midnight Gallery investigation.</p>
            <Link href="/investigation/new" className="mt-4 inline-block rounded-lg border border-white/20 px-3 py-2">
              Start or restart case
            </Link>
          </Panel>
        </div>
      </main>
    </AuthGuard>
  );
}
