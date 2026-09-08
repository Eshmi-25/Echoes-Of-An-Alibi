"use client";

import Link from "next/link";

import { AuthGuard } from "@/components/layout/auth-guard";

export default function InvestigationRootPage() {
  return (
    <AuthGuard>
      <main className="mx-auto max-w-3xl p-6">
        <h1 className="text-5xl">Investigation Hub</h1>
        <p className="mt-3 text-white/80">Open your dashboard to continue an active case or start a new one.</p>
        <Link href="/dashboard" className="mt-4 inline-block rounded-lg bg-noir-amber px-4 py-2 font-semibold text-black">
          Go to Dashboard
        </Link>
      </main>
    </AuthGuard>
  );
}
