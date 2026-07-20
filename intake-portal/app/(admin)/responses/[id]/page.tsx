import Link from "next/link";
import { supabaseAdmin } from "@/lib/supabase";
import type { Form } from "@/lib/supabase";
import { notFound } from "next/navigation";
import CopyMarkdown from "@/components/CopyMarkdown";

export const dynamic = "force-dynamic";

type Response = {
  id: string;
  answers: Record<string, string>;
  submitted_at: string;
};

export default async function ResponsesPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const admin = supabaseAdmin();

  const { data: formData } = await admin
    .from("forms")
    .select("*")
    .eq("id", id)
    .single();
  if (!formData) notFound();
  const form = formData as Form;

  const { data: respData } = await admin
    .from("responses")
    .select("*")
    .eq("form_id", id)
    .order("submitted_at", { ascending: false });
  const responses = (respData ?? []) as Response[];

  return (
    <main className="mx-auto max-w-4xl px-6 py-10">
      <div className="mb-6 flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-xl font-bold text-slate-900">{form.title}</h1>
          <p className="text-sm text-slate-500">
            {responses.length} {responses.length === 1 ? "reactie" : "reacties"}
          </p>
        </div>
        <div className="flex items-center gap-2">
          {responses.length > 0 && (
            <a
              href={`/responses/${id}/export`}
              className="rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-sm font-medium text-slate-700 hover:bg-slate-50"
            >
              Download CSV
            </a>
          )}
          <Link
            href="/"
            className="text-sm font-medium text-slate-500 hover:text-slate-800"
          >
            Alle formulieren
          </Link>
        </div>
      </div>

      {responses.length === 0 ? (
        <p className="rounded-xl border border-dashed border-slate-300 p-10 text-center text-slate-500">
          Nog geen reacties. Deel de link met je klant.
        </p>
      ) : (
        <div className="space-y-6">
          {responses.map((r) => {
            const date = new Date(r.submitted_at).toLocaleString("nl-NL");
            const pairs = form.fields.map((f) => ({
              label: f.label,
              value: r.answers[f.id] ?? "",
            }));
            return (
              <div key={r.id} className="rounded-xl border border-slate-200 bg-white p-5">
                <div className="mb-3 flex items-center justify-between">
                  <p className="text-xs text-slate-400">{date}</p>
                  <CopyMarkdown title={form.title} date={date} pairs={pairs} />
                </div>
                <dl className="space-y-3">
                  {pairs.map((p, i) => (
                    <div key={i}>
                      <dt className="text-sm font-medium text-slate-500">{p.label}</dt>
                      <dd className="whitespace-pre-wrap text-slate-800">
                        {p.value.trim() ? p.value : "(niet ingevuld)"}
                      </dd>
                    </div>
                  ))}
                </dl>
              </div>
            );
          })}
        </div>
      )}
    </main>
  );
}
