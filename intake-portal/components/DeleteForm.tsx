"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { deleteForm } from "@/lib/actions";

export default function DeleteForm({ id }: { id: string }) {
  const [busy, setBusy] = useState(false);
  const router = useRouter();

  async function onClick() {
    if (!confirm("Dit formulier en alle antwoorden verwijderen? Dit kan niet ongedaan worden gemaakt.")) {
      return;
    }
    setBusy(true);
    await deleteForm(id);
    router.refresh();
  }

  return (
    <button
      onClick={onClick}
      disabled={busy}
      className="rounded-lg px-3 py-1 text-sm font-medium text-red-600 hover:bg-red-50 disabled:opacity-50"
    >
      {busy ? "Bezig..." : "Verwijderen"}
    </button>
  );
}
