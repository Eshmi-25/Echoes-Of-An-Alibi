"use client";

import { useParams } from "next/navigation";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useForm } from "react-hook-form";
import toast from "react-hot-toast";

import { AuthGuard } from "@/components/layout/auth-guard";
import { AppShell } from "@/components/layout/app-shell";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Panel } from "@/components/ui/panel";
import { api } from "@/services/api";

export default function NotesPage() {
  const params = useParams<{ investigationId: string }>();
  const id = Number(params.investigationId);
  const qc = useQueryClient();
  const notes = useQuery({ queryKey: ["notes", id], queryFn: () => api.notes(id) });
  const { register, handleSubmit, reset } = useForm<{ title: string; body: string }>();

  const create = useMutation({
    mutationFn: (values: { title: string; body: string }) => api.createNote(id, values),
    onSuccess: () => {
      reset();
      qc.invalidateQueries({ queryKey: ["notes", id] });
      toast.success("Note saved.");
    }
  });

  const remove = useMutation({
    mutationFn: (noteId: number) => api.deleteNote(id, noteId),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["notes", id] })
  });

  return (
    <AuthGuard>
      <AppShell investigationId={params.investigationId}>
        <div className="grid gap-4 md:grid-cols-2">
          <Panel title="Detective Notebook">
            <form className="space-y-2" onSubmit={handleSubmit((values) => create.mutate(values))}>
              <Input placeholder="Note title" {...register("title", { required: true })} />
              <textarea
                className="h-32 w-full rounded-xl border border-white/15 bg-white/5 p-3"
                placeholder="Record contradictions, motives, and timelines..."
                {...register("body", { required: true })}
              />
              <Button type="submit">Save Note</Button>
            </form>
          </Panel>
          <Panel title="Saved Notes">
            {notes.data?.length ? notes.data.map((n) => (
              <article key={n.id} className="mb-3 rounded-lg border border-white/10 bg-white/5 p-3">
                <h2 className="text-2xl">{n.title}</h2>
                <p className="text-sm text-white/80">{n.body}</p>
                <button
                  className="mt-2 rounded bg-noir-danger px-2 py-1 text-xs"
                  onClick={() => remove.mutate(n.id)}
                  aria-label={`Delete note ${n.title}`}
                >
                  Delete
                </button>
              </article>
            )) : <p className="text-white/70">No notes yet.</p>}
          </Panel>
        </div>
      </AppShell>
    </AuthGuard>
  );
}
