"use client";

import { useState } from "react";

type Pair = { label: string; value: string };

export default function CopyMarkdown({
  title,
  date,
  pairs,
}: {
  title: string;
  date: string;
  pairs: Pair[];
}) {
  const [copied, setCopied] = useState(false);

  function copy() {
    const md =
      `## ${title} (${date})\n\n` +
      pairs
        .map((p) => `**${p.label}:** ${p.value.trim() ? p.value : "(niet ingevuld)"}`)
        .join("\n");
    navigator.clipboard.writeText(md);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  }

  return (
    <button
      onClick={copy}
      className="rounded-lg border border-slate-300 bg-white px-3 py-1 text-sm font-medium text-slate-700 hover:bg-slate-50"
    >
      {copied ? "Gekopieerd!" : "Kopieer als markdown"}
    </button>
  );
}
