"use client";

import { useParams, useRouter } from "next/navigation";
import { useMutation, useQuery } from "@tanstack/react-query";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import toast from "react-hot-toast";

import { AuthGuard } from "@/components/layout/auth-guard";
import { AppShell } from "@/components/layout/app-shell";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Panel } from "@/components/ui/panel";
import { api } from "@/services/api";

const schema = z.object({
  attacker_slug: z.string().min(1),
  thief_slug: z.string().min(1),
  motive: z.string().min(4),
  supporting1: z.string().min(1),
  supporting2: z.string().min(1),
  explanation: z.string().min(10)
});

type FormValues = z.infer<typeof schema>;

export default function AccusePage() {
  const params = useParams<{ investigationId: string }>();
  const id = Number(params.investigationId);
  const router = useRouter();

  const suspects = useQuery({ queryKey: ["suspects", id], queryFn: () => api.suspects(id) });
  const clues = useQuery({ queryKey: ["clues", id], queryFn: () => api.clues(id) });

  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm<FormValues>({ resolver: zodResolver(schema) });

  const accuse = useMutation({
    mutationFn: (values: FormValues) =>
      api.accuse(id, {
        attacker_slug: values.attacker_slug,
        thief_slug: values.thief_slug,
        motive: values.motive,
        supporting_clues: [values.supporting1, values.supporting2],
        explanation: values.explanation
      }),
    onSuccess: () => {
      toast.success("Accusation submitted.");
      router.push(`/investigation/${id}/result`);
    },
    onError: (error) => toast.error(error instanceof Error ? error.message : "Accusation failed")
  });

  return (
    <AuthGuard>
      <AppShell investigationId={params.investigationId}>
        <Panel title="Final Accusation">
          <form className="grid gap-3 md:grid-cols-2" onSubmit={handleSubmit((v) => accuse.mutate(v))}>
            <label className="text-sm">Attacker
              <select className="mt-1 w-full rounded-xl border border-white/15 bg-white/5 p-2" {...register("attacker_slug")}>
                <option value="">Select suspect</option>
                {suspects.data?.filter((s) => s.unlocked).map((s) => <option key={s.suspect_slug} value={s.suspect_slug}>{s.suspect_slug}</option>)}
              </select>
            </label>
            <label className="text-sm">Thief
              <select className="mt-1 w-full rounded-xl border border-white/15 bg-white/5 p-2" {...register("thief_slug")}>
                <option value="">Select suspect</option>
                {suspects.data?.filter((s) => s.unlocked).map((s) => <option key={s.suspect_slug} value={s.suspect_slug}>{s.suspect_slug}</option>)}
              </select>
            </label>
            <label className="text-sm md:col-span-2">Motive
              <Input {...register("motive")} placeholder="Describe motive" />
            </label>
            <label className="text-sm">Supporting clue #1
              <select className="mt-1 w-full rounded-xl border border-white/15 bg-white/5 p-2" {...register("supporting1")}>
                <option value="">Select clue</option>
                {clues.data?.map((c) => <option key={c.clue_slug} value={c.clue_slug}>{c.title}</option>)}
              </select>
            </label>
            <label className="text-sm">Supporting clue #2
              <select className="mt-1 w-full rounded-xl border border-white/15 bg-white/5 p-2" {...register("supporting2")}>
                <option value="">Select clue</option>
                {clues.data?.map((c) => <option key={c.clue_slug} value={c.clue_slug}>{c.title}</option>)}
              </select>
            </label>
            <label className="text-sm md:col-span-2">Explanation
              <textarea className="mt-1 h-28 w-full rounded-xl border border-white/15 bg-white/5 p-3" {...register("explanation")} />
            </label>
            {Object.values(errors).length ? <p className="md:col-span-2 text-sm text-noir-danger">Please complete all accusation fields.</p> : null}
            <Button type="submit" disabled={isSubmitting || accuse.isPending}>{accuse.isPending ? "Submitting..." : "Submit accusation"}</Button>
          </form>
        </Panel>
      </AppShell>
    </AuthGuard>
  );
}
