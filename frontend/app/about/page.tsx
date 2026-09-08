export default function AboutPage() {
  return (
    <main className="mx-auto max-w-3xl p-6">
      <h1 className="text-5xl">How To Play</h1>
      <p className="mt-4 text-white/80">
        Register, start the case, spend actions to search locations, interrogate suspects, expose contradictions,
        and submit a final accusation with supporting clues.
      </p>
      <ul className="mt-6 list-disc space-y-2 pl-6 text-white/80">
        <li>Each location search costs one action.</li>
        <li>Dialogue may unlock topics and contradictions.</li>
        <li>The hidden solution stays server-side until resolution.</li>
      </ul>
    </main>
  );
}
