"use client";

import Link from "next/link";
import Image from "next/image";
import { usePathname } from "next/navigation";

export default function AdminNav() {
  const path = usePathname();

  const tabs = [
    { href: "/", label: "Formulieren", active: path === "/" || path.startsWith("/responses") },
    { href: "/new", label: "Nieuw formulier", active: path.startsWith("/new") },
  ];

  return (
    <header className="border-b border-slate-200 bg-white">
      <div className="mx-auto flex max-w-4xl items-center justify-between px-6 py-3">
        <Link href="/" className="flex items-center">
          <Image src="/logo.png" alt="Efficienter" width={440} height={100} className="h-9 w-auto" priority />
        </Link>
        <nav className="flex items-center gap-1">
          {tabs.map((t) => (
            <Link
              key={t.href}
              href={t.href}
              className={
                "rounded-lg px-3 py-1.5 text-sm font-medium " +
                (t.active
                  ? "bg-emerald-50 text-emerald-700"
                  : "text-slate-600 hover:bg-slate-100")
              }
            >
              {t.label}
            </Link>
          ))}
        </nav>
      </div>
    </header>
  );
}
