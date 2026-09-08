import Link from "next/link";
import { ChevronRight, Compass, Drama, Shield } from "lucide-react";

import { Panel } from "@/components/ui/panel";

export default function LandingPage() {
  return (
    <main className="mx-auto flex min-h-screen max-w-6xl flex-col justify-center gap-8 p-6">
      <section className="grid gap-6 md:grid-cols-[1.4fr_1fr]">
        <Panel className="p-8">
          <p className="text-xs uppercase tracking-[0.3em] text-noir-amber">Portfolio Game</p>
          <h1 className="mt-2 text-6xl leading-none">Echoes of the Alibi</h1>
          <p className="mt-2 text-xl text-white/75">Every suspect remembers the night differently.</p>
          <p className="mt-6 max-w-2xl text-white/80">
            Investigate The Midnight Gallery. Search scenes, interrogate AI-driven suspects, expose contradictions,
            and file your final accusation before your investigation actions run out.
          </p>
          <div className="mt-8 flex flex-wrap gap-3">
            <Link
              href="/register"
              className="inline-flex items-center gap-2 rounded-xl bg-noir-amber px-5 py-3 font-semibold text-black"
            >
              Start Investigation
              <ChevronRight size={18} />
            </Link>
            <Link href="/about" className="rounded-xl border border-white/20 px-5 py-3 text-white/90">
              How To Play
            </Link>
          </div>
        </Panel>
        <Panel className="space-y-4 p-6">
          <Feature icon={<Compass size={20} />} title="Explore" text="Search 4+ locations to reveal locked clues." />
          <Feature icon={<Drama size={20} />} title="Interrogate" text="Constrained suspect dialogue with fallback mode." />
          <Feature icon={<Shield size={20} />} title="Deduce" text="Backend-owned truth and deterministic scoring." />
        </Panel>
      </section>
    </main>
  );
}

function Feature({ icon, title, text }: { icon: React.ReactNode; title: string; text: string }) {
  return (
    <div className="rounded-xl border border-white/10 bg-white/5 p-3">
      <div className="mb-2 inline-flex rounded-lg bg-noir-soft p-2 text-noir-amber">{icon}</div>
      <h2 className="text-2xl">{title}</h2>
      <p className="text-sm text-white/75">{text}</p>
    </div>
  );
}
