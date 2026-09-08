import Link from "next/link";

export default function NotFound() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center gap-4 p-6 text-center">
      <h1 className="text-6xl text-noir-amber">404</h1>
      <p className="text-lg text-white/80">This lead went cold.</p>
      <Link href="/" className="rounded-xl bg-noir-amber px-4 py-2 font-semibold text-black">
        Return to HQ
      </Link>
    </main>
  );
}
