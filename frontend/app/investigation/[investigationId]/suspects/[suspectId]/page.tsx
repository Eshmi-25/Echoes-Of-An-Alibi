"use client";

import { useParams } from "next/navigation";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useForm } from "react-hook-form";
import toast from "react-hot-toast";

import { appConfig } from "@/lib/config";
import { useUiStore } from "@/stores/ui-store";
import { AuthGuard } from "@/components/layout/auth-guard";
import { AppShell } from "@/components/layout/app-shell";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Panel } from "@/components/ui/panel";
import { api } from "@/services/api";

export default function SuspectDetailPage() {
  const params = useParams<{ investigationId: string; suspectId: string }>();
  const id = Number(params.investigationId);
  const suspectId = params.suspectId;
  const qc = useQueryClient();
  const selectedEvidence = useUiStore((s) => s.selectedEvidence);
  const setSelectedEvidence = useUiStore((s) => s.setSelectedEvidence);

  const suspect = useQuery({ queryKey: ["suspect", id, suspectId], queryFn: () => api.suspect(id, suspectId) });
  const messages = useQuery({ queryKey: ["messages", id, suspectId], queryFn: () => api.messages(id, suspectId) });
  const clues = useQuery({ queryKey: ["clues", id], queryFn: () => api.clues(id) });

  const { register, handleSubmit, reset, formState: { isSubmitting } } = useForm<{ message: string }>();

  const speak = useMutation({
    mutationFn: (message: string) => api.sendMessage(id, suspectId, { message, evidence_clue_slug: selectedEvidence ?? undefined }),
    onSuccess: (data) => {
      qc.invalidateQueries({ queryKey: ["messages", id, suspectId] });
      qc.invalidateQueries({ queryKey: ["suspects", id] });
      qc.invalidateQueries({ queryKey: ["contradictions", id] });
      reset();
      if (data.contradiction_exposed) {
        toast.success("Contradiction exposed.");
      }
      if (data.unlocked_topics.length > 0) {
        toast.success(`Unlocked topics: ${data.unlocked_topics.join(", ")}`);
      }
    },
    onError: (error) => toast.error(error instanceof Error ? error.message : "Dialogue failed")
  });

  const confront = useMutation({
    mutationFn: (message: string) => {
      if (!selectedEvidence) {
        throw new Error("Select evidence first");
      }
      return api.confront(id, suspectId, { message, clue_slug: selectedEvidence });
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["messages", id, suspectId] });
      toast.success("Confrontation sent.");
    },
    onError: (error) => toast.error(error instanceof Error ? error.message : "Confront failed")
  });

  return (
    <AuthGuard>
      <AppShell investigationId={params.investigationId}>
        <div className="grid gap-4 lg:grid-cols-[300px_1fr]">
          <Panel title="Suspect Profile">
            <div className="mb-3 flex items-center gap-3">
              <div className="h-14 w-14 rounded-full bg-gradient-to-br from-noir-soft to-noir-amber/40" aria-hidden />
              <div>
                <p className="text-xl">{String(suspect.data?.full_name ?? suspectId)}</p>
                <p className="text-sm text-white/70">{String(suspect.data?.occupation ?? "...")}</p>
              </div>
            </div>
            <p className="text-sm text-white/80">{String(suspect.data?.public_bio ?? "")}</p>
            <div className="mt-3 space-y-2 text-xs text-white/80">
              <p>Trust: {String((suspect.data?.state as { trust?: number } | undefined)?.trust ?? "-")}</p>
              <p>Pressure: {String((suspect.data?.state as { pressure?: number } | undefined)?.pressure ?? "-")}</p>
            </div>
            <div className="mt-4">
              <p className="mb-2 text-xs uppercase tracking-wider text-noir-amber">Evidence for confrontation</p>
              <select
                className="w-full rounded-xl border border-white/15 bg-white/5 p-2"
                value={selectedEvidence ?? ""}
                onChange={(e) => setSelectedEvidence(e.target.value || null)}
                aria-label="Select evidence"
              >
                <option value="">None selected</option>
                {clues.data?.map((clue) => (
                  <option key={clue.clue_slug} value={clue.clue_slug}>
                    {clue.title}
                  </option>
                ))}
              </select>
            </div>
          </Panel>

          <Panel title="Interrogation Room">
            <div className="mb-3 h-[360px] overflow-auto rounded-xl border border-white/10 bg-black/20 p-3">
              {messages.data?.length ? (
                messages.data.map((m, idx) => (
                  <div key={`${m.created_at}-${idx}`} className={`mb-3 ${m.role === "player" ? "text-right" : "text-left"}`}>
                    <p className="inline-block rounded-xl bg-white/10 px-3 py-2 text-sm">{m.content}</p>
                    {appConfig.enableAiDebug && m.ai_debug ? (
                      <p className="mt-1 text-[11px] text-white/50">AI: {JSON.stringify(m.ai_debug)}</p>
                    ) : null}
                  </div>
                ))
              ) : (
                <p className="text-sm text-white/60">No questions asked yet.</p>
              )}
            </div>
            <form
              onSubmit={handleSubmit(async (values) => {
                await speak.mutateAsync(values.message);
              })}
              className="flex gap-2"
            >
              <Input placeholder="Ask about timeline, motive, or evidence..." {...register("message", { required: true })} aria-label="Question input" />
              <Button type="submit" disabled={isSubmitting || speak.isPending}>{speak.isPending ? "..." : "Send"}</Button>
              <Button
                type="button"
                className="bg-white/20 text-white"
                disabled={confront.isPending}
                onClick={handleSubmit(async (values) => {
                  await confront.mutateAsync(values.message);
                })}
              >
                Confront
              </Button>
            </form>
            {speak.isPending || confront.isPending ? <p className="mt-2 text-xs text-white/60">Suspect is responding...</p> : null}
          </Panel>
        </div>
      </AppShell>
    </AuthGuard>
  );
}
