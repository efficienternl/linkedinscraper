"use client";

import { useState } from "react";
import { submitResponse } from "@/lib/actions";
import type { Form } from "@/lib/supabase";

export default function PublicForm({ form }: { form: Form }) {
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [otherActive, setOtherActive] = useState<Record<string, boolean>>({});
  const [saving, setSaving] = useState(false);
  const [done, setDone] = useState(false);
  const [err, setErr] = useState("");

  function set(id: string, value: string) {
    setAnswers((a) => ({ ...a, [id]: value }));
  }

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    for (const f of form.fields) {
      if (f.required && !answers[f.id]?.trim()) {
        setErr("Vul alle verplichte velden in (gemarkeerd met *).");
        return;
      }
    }
    setErr("");
    setSaving(true);
    try {
      await submitResponse(form.id, answers);
      setDone(true);
    } catch {
      setErr("Er ging iets mis bij het opslaan. Probeer het opnieuw.");
      setSaving(false);
    }
  }

  if (done) {
    return (
      <div className="rounded-xl border border-emerald-200 bg-emerald-50 p-8 text-center">
        <p className="text-lg font-semibold text-emerald-800">Bedankt!</p>
        <p className="mt-1 text-emerald-700">
          Je antwoorden zijn verstuurd. We nemen het door en gaan aan de slag.
        </p>
      </div>
    );
  }

  const inputCls =
    "w-full rounded-lg border border-slate-300 px-3 py-2 focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-100";

  return (
    <form onSubmit={submit} className="space-y-6">
      {form.fields.map((f) => (
        <div key={f.id}>
          <label className="mb-1.5 block text-sm font-medium text-slate-800">
            {f.label} {f.required && <span className="text-emerald-600">*</span>}
          </label>

          {f.type === "textarea" ? (
            <textarea
              value={answers[f.id] ?? ""}
              onChange={(e) => set(f.id, e.target.value)}
              rows={3}
              className={inputCls}
            />
          ) : f.type === "choice" ? (
            <div className="space-y-2">
              {(f.options ?? []).map((opt) => (
                <label
                  key={opt}
                  className="flex cursor-pointer items-center gap-2.5 rounded-lg border border-slate-200 px-3 py-2 hover:border-slate-300"
                >
                  <input
                    type="radio"
                    name={f.id}
                    checked={!otherActive[f.id] && answers[f.id] === opt}
                    onChange={() => {
                      setOtherActive((o) => ({ ...o, [f.id]: false }));
                      set(f.id, opt);
                    }}
                    className="accent-emerald-500"
                  />
                  <span className="text-sm text-slate-700">{opt}</span>
                </label>
              ))}
              {f.allowOther && (
                <div className="rounded-lg border border-slate-200 px-3 py-2">
                  <label className="flex cursor-pointer items-center gap-2.5">
                    <input
                      type="radio"
                      name={f.id}
                      checked={!!otherActive[f.id]}
                      onChange={() => {
                        setOtherActive((o) => ({ ...o, [f.id]: true }));
                        set(f.id, "");
                      }}
                      className="accent-emerald-500"
                    />
                    <span className="text-sm text-slate-700">Anders:</span>
                  </label>
                  {otherActive[f.id] && (
                    <input
                      value={answers[f.id] ?? ""}
                      onChange={(e) => set(f.id, e.target.value)}
                      placeholder="Vul zelf in..."
                      className={inputCls + " mt-2"}
                    />
                  )}
                </div>
              )}
            </div>
          ) : (
            <input
              type={f.type}
              value={answers[f.id] ?? ""}
              onChange={(e) => set(f.id, e.target.value)}
              className={inputCls}
            />
          )}
        </div>
      ))}

      {err && <p className="text-sm text-red-600">{err}</p>}

      <button
        type="submit"
        disabled={saving}
        className="w-full rounded-lg bg-emerald-500 px-5 py-3 font-semibold text-white shadow-sm hover:bg-emerald-600 disabled:opacity-50"
      >
        {saving ? "Versturen..." : "Versturen"}
      </button>
    </form>
  );
}
