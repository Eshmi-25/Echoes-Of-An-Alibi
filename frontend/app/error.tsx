"use client";

import Link from "next/link";

export default function ErrorPage({ reset }: { error: Error; reset: () => void }) {
  return (
    <main className="mx-auto flex min-h-screen max-w-2xl flex-col items-center justify-center gap-3 p-6 text-center">
      <h1 className="text-5xl text-noir-amber">Unexpected Lead Failure</h1>
      <p className="text-white/75">A runtime error occurred while processing this scene.</p>
      <div className="flex gap-2">
        <button className="rounded-lg bg-noir-amber px-4 py-2 font-semibold text-black" onClick={reset}>
          Retry
        </button>
        <Link href="/dashboard" className="rounded-lg border border-white/20 px-4 py-2">
          Back to Dashboard
        </Link>
      </div>
    </main>
  );
}
