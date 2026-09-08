"use client";

import { useParams, useRouter } from "next/navigation";
import { useMutation } from "@tanstack/react-query";

import { AuthGuard } from "@/components/layout/auth-guard";
import { AppShell } from "@/components/layout/app-shell";
import { Button } from "@/components/ui/button";
import { Panel } from "@/components/ui/panel";
import { api } from "@/services/api";

export default function SettingsPage() {
  const params = useParams<{ investigationId: string }>();
  const id = Number(params.investigationId);
  const router = useRouter();

  const restart = useMutation({
    mutationFn: () => api.restart(id),
    onSuccess: () => router.push(`/investigation/${id}/briefing`)
  });

  return (
    <AuthGuard>
      <AppShell investigationId={params.investigationId}>
        <Panel title="Settings">
          <p className="text-white/80">Restarting clears current notes, dialogue, board links, and accusation.</p>
          <Button
            className="mt-4 bg-noir-danger text-white"
            onClick={() => {
              const confirmed = window.confirm("Restart this case? This cannot be undone.");
              if (confirmed) {
                restart.mutate();
              }
            }}
          >
            Restart Case
          </Button>
        </Panel>
      </AppShell>
    </AuthGuard>
  );
}
