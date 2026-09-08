import { ReactNode } from "react";

import { cn } from "@/lib/utils";

export function Panel({ title, children, className }: { title?: string; children: ReactNode; className?: string }) {
  return (
    <section className={cn("noir-card p-4", className)}>
      {title ? <h2 className="mb-2 text-2xl text-noir-amber">{title}</h2> : null}
      {children}
    </section>
  );
}
