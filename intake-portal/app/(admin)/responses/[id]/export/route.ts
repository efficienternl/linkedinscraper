import { supabaseAdmin } from "@/lib/supabase";
import type { Form } from "@/lib/supabase";

type Response = { answers: Record<string, string>; submitted_at: string };

export async function GET(
  _req: Request,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id } = await params;
  const admin = supabaseAdmin();

  const { data: formData } = await admin
    .from("forms")
    .select("*")
    .eq("id", id)
    .single();
  if (!formData) return new Response("Niet gevonden", { status: 404 });
  const form = formData as Form;

  const { data: respData } = await admin
    .from("responses")
    .select("*")
    .eq("form_id", id)
    .order("submitted_at", { ascending: true });
  const responses = (respData ?? []) as Response[];

  const esc = (v: string) => `"${(v ?? "").replace(/"/g, '""')}"`;
  const header = ["Ingezonden op", ...form.fields.map((f) => f.label)];
  const rows = responses.map((r) =>
    [
      new Date(r.submitted_at).toLocaleString("nl-NL"),
      ...form.fields.map((f) => r.answers[f.id] ?? ""),
    ]
      .map(esc)
      .join(",")
  );
  const csv = [header.map(esc).join(","), ...rows].join("\n");

  const filename =
    (form.title || "export").replace(/[^a-z0-9]+/gi, "-").toLowerCase() + ".csv";

  // BOM zodat Excel UTF-8 correct opent
  return new Response("﻿" + csv, {
    headers: {
      "Content-Type": "text/csv; charset=utf-8",
      "Content-Disposition": `attachment; filename="${filename}"`,
    },
  });
}
