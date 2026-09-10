"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { ReactNode } from "react";
import { Home, Map, NotebookPen, Scale, Users } from "lucide-react";

import { appConfig } from "@/lib/config";
import { cn } from "@/lib/utils";

const links = [
  { href: "/dashboard", label: "Dashboard / HQ", icon: Home },
  { href: "/locations", label: "Locations", icon: Map },
  { href: "/suspects", label: "Suspects", icon: Users },
  { href: "/notes", label: "Notes", icon: NotebookPen },
  { href: "/accuse", label: "Accuse", icon: Scale }
];

export function AppShell({ children, investigationId }: { children: ReactNode; investigationId?: string }) {
  const path = usePathname();

  return (
    <div className="grid min-h-screen grid-cols-1 md:grid-cols-[260px_1fr]">
      <aside className="border-r border-white/10 bg-black/30 p-4 backdrop-blur">
        <p className="text-xs uppercase tracking-[0.2em] text-noir-amber">{appConfig.appName}</p>
        <p className="mb-6 text-2xl">Caseboard</p>
        <nav className="space-y-2">
          {links.map((link) => {
            const href = investigationId
              ? `/investigation/${investigationId}${link.href === "/dashboard" ? "" : link.href}`
              : link.href;
            const active = path === href;
            const Icon = link.icon;
            return (
              <Link
                key={link.href}
                href={href}
                className={cn(
                  "flex items-center gap-2 rounded-lg px-3 py-2 text-sm transition",
                  active ? "bg-noir-amber text-black" : "hover:bg-white/10"
                )}
              >
                <Icon size={16} />
                {link.label}
              </Link>
            );
          })}
        </nav>
      </aside>
      <main className="p-4 md:p-8">{children}</main>
    </div>
  );
}
