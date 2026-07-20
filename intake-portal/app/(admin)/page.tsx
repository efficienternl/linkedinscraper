import Link from "next/link";
import { supabaseAdmin } from "@/lib/supabase";
import type { Form } from "@/lib/supabase";
import CopyLink from "@/components/CopyLink";
import DeleteForm from "@/components/DeleteForm";

export const dynamic = "force-dynamic";

export default async function Home() {
  const admin = supabaseAdmin();
  const { data } = await admin
    .from("forms")
    .select("*")
    .order("created_at", { ascending: false });
  const forms = (data ?? []) as Form[];

  return (
    <main className="mx-auto max-w-4xl px-6 py-10">
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-xl font-bold text-slate-900">Formulieren</h1>
        <Link
          href="/new"
          className="rounded-lg bg-emerald-500 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-emerald-600"
        >
          + Nieuw formulier
        </Link>
      </div>

      {forms.length === 0 ? (
        <p className="rounded-xl border border-dashed border-slate-300 p-10 text-center text-slate-500">
          Nog geen formulieren. Klik op &quot;Nieuw formulier&quot; om te beginnen.
        </p>
      ) : (
        <ul className="space-y-3">
          {forms.map((f) => (
            <li
              key={f.id}
              className="flex flex-col gap-3 rounded-xl border border-slate-200 bg-white p-4 sm:flex-row sm:items-center sm:justify-between"
            >
              <div>
                <p className="font-semibold text-slate-900">{f.title}</p>
                <p className="text-sm text-slate-500">
                  {f.fields.length} velden ·{" "}
                  {new Date(f.created_at).toLocaleDateString("nl-NL")}
                </p>
              </div>
              <div className="flex flex-wrap items-center gap-2">
                <CopyLink path={`/f/${f.id}`} />
                <Link
                  href={`/f/${f.id}`}
                  target="_blank"
                  className="rounded-lg border border-slate-300 bg-white px-3 py-1 text-sm font-medium text-slate-700 hover:bg-slate-50"
                >
                  Bekijken
                </Link>
                <Link
                  href={`/responses/${f.id}`}
                  className="rounded-lg bg-slate-100 px-3 py-1 text-sm font-medium text-slate-700 hover:bg-slate-200"
                >
                  Antwoorden
                </Link>
                <DeleteForm id={f.id} />
              </div>
            </li>
          ))}
        </ul>
      )}
    </main>
  );
}
