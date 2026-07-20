"use client";

import { useState } from "react";
import { STANDARD_FIELDS, DEFAULT_CHECKED } from "@/lib/fields";
import { createForm } from "@/lib/actions";
import type { Field } from "@/lib/supabase";

type Custom = {
  label: string;
  type: "text" | "textarea" | "choice";
  required: boolean;
  options: string[];
  allowOther: boolean;
};

export default function NewForm() {
  const [title, setTitle] = useState("");
  const [checked, setChecked] = useState<Record<string, boolean>>(
    Object.fromEntries(
      STANDARD_FIELDS.map((f) => [f.id, DEFAULT_CHECKED.includes(f.id)])
    )
  );
  const [custom, setCustom] = useState<Custom[]>([]);
  const [saving, setSaving] = useState(false);
  const [err, setErr] = useState("");

  function addCustom(type: Custom["type"]) {
    setCustom((c) => [
      ...c,
      {
        label: "",
        type,
        required: false,
        options: type === "choice" ? ["", ""] : [],
        allowOther: false,
      },
    ]);
  }
  function updateCustom(i: number, patch: Partial<Custom>) {
    setCustom((c) => c.map((q, idx) => (idx === i ? { ...q, ...patch } : q)));
  }
  function removeCustom(i: number) {
    setCustom((c) => c.filter((_, idx) => idx !== i));
  }
  function setOption(qi: number, oi: number, value: string) {
    setCustom((c) =>
      c.map((q, idx) =>
        idx === qi
          ? { ...q, options: q.options.map((o, j) => (j === oi ? value : o)) }
          : q
      )
    );
  }
  function addOption(qi: number) {
    setCustom((c) =>
      c.map((q, idx) => (idx === qi ? { ...q, options: [...q.options, ""] } : q))
    );
  }
  function removeOption(qi: number, oi: number) {
    setCustom((c) =>
      c.map((q, idx) =>
        idx === qi
          ? { ...q, options: q.options.filter((_, j) => j !== oi) }
          : q
      )
    );
  }

  async function save() {
    const fields: Field[] = [
      ...STANDARD_FIELDS.filter((f) => checked[f.id]),
      ...custom
        .filter((c) => c.label.trim())
        .map((c, i) => {
          const base: Field = {
            id: `custom_${i}`,
            label: c.label.trim(),
            type: c.type,
            required: c.required,
            standard: false,
          };
          if (c.type === "choice") {
            base.options = c.options.map((o) => o.trim()).filter(Boolean);
            base.allowOther = c.allowOther;
          }
          return base;
        }),
    ];
    if (!title.trim()) {
      setErr("Geef het formulier een titel.");
      return;
    }
    if (fields.length === 0) {
      setErr("Kies minstens één veld of voeg een vraag toe.");
      return;
    }
    const badChoice = fields.find(
      (f) => f.type === "choice" && (!f.options || f.options.length < 2)
    );
    if (badChoice) {
      setErr(`Geef de meerkeuzevraag "${badChoice.label}" minstens 2 opties.`);
      return;
    }
    setErr("");
    setSaving(true);
    await createForm(title.trim(), fields);
  }

  const inputCls =
    "w-full rounded-lg border border-slate-300 px-3 py-2 focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-100";

  return (
    <main className="mx-auto max-w-2xl px-6 py-10">
      <h1 className="mb-6 text-2xl font-bold text-slate-900">Nieuw formulier</h1>

      <label className="mb-1 block text-sm font-medium text-slate-700">
        Titel
      </label>
      <input
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        className={inputCls + " mb-8"}
        placeholder="Onboarding De Sloten Specialist"
      />

      <h2 className="mb-1 font-semibold text-slate-900">Standaard-gegevens</h2>
      <p className="mb-3 text-sm text-slate-500">
        Vink aan wat je van deze klant wilt weten. Aangevinkte velden zijn altijd verplicht.
      </p>
      <div className="mb-8 space-y-2">
        {STANDARD_FIELDS.map((f) => (
          <label
            key={f.id}
            className="flex cursor-pointer items-center gap-3 rounded-lg border border-slate-200 bg-white px-3 py-2 hover:border-slate-300"
          >
            <input
              type="checkbox"
              checked={checked[f.id]}
              onChange={(e) =>
                setChecked((c) => ({ ...c, [f.id]: e.target.checked }))
              }
              className="h-4 w-4 accent-emerald-500"
            />
            <span className="text-sm text-slate-700">{f.label}</span>
          </label>
        ))}
      </div>

      <h2 className="mb-1 font-semibold text-slate-900">Custom vragen</h2>
      <p className="mb-3 text-sm text-slate-500">
        Voeg vragen toe die specifiek zijn voor deze klant of build.
      </p>
      <div className="mb-4 space-y-3">
        {custom.map((q, i) => (
          <div key={i} className="rounded-lg border border-slate-200 bg-white p-4">
            <input
              value={q.label}
              onChange={(e) => updateCustom(i, { label: e.target.value })}
              placeholder="Je vraag..."
              className={inputCls + " mb-3"}
            />

            {q.type === "choice" && (
              <div className="mb-3 space-y-2">
                <p className="text-xs font-medium text-slate-500">Opties</p>
                {q.options.map((o, oi) => (
                  <div key={oi} className="flex items-center gap-2">
                    <input
                      value={o}
                      onChange={(e) => setOption(i, oi, e.target.value)}
                      placeholder={`Optie ${oi + 1}`}
                      className={inputCls + " py-1.5"}
                    />
                    {q.options.length > 2 && (
                      <button
                        type="button"
                        onClick={() => removeOption(i, oi)}
                        className="text-slate-400 hover:text-red-500"
                      >
                        ✕
                      </button>
                    )}
                  </div>
                ))}
                <button
                  type="button"
                  onClick={() => addOption(i)}
                  className="text-sm font-medium text-emerald-600 hover:underline"
                >
                  + Optie toevoegen
                </button>
                <label className="mt-1 flex items-center gap-2 text-sm text-slate-600">
                  <input
                    type="checkbox"
                    checked={q.allowOther}
                    onChange={(e) => updateCustom(i, { allowOther: e.target.checked })}
                    className="accent-emerald-500"
                  />
                  Voeg een &quot;Anders&quot;-optie toe
                </label>
              </div>
            )}

            <div className="flex flex-wrap items-center gap-4 text-sm text-slate-600">
              <span className="rounded bg-slate-100 px-2 py-0.5 text-xs font-medium text-slate-500">
                {q.type === "text"
                  ? "Kort antwoord"
                  : q.type === "textarea"
                  ? "Lang antwoord"
                  : "Meerkeuze"}
              </span>
              <label className="flex items-center gap-1">
                <input
                  type="checkbox"
                  checked={q.required}
                  onChange={(e) => updateCustom(i, { required: e.target.checked })}
                  className="accent-emerald-500"
                />
                Verplicht
              </label>
              <button
                type="button"
                onClick={() => removeCustom(i)}
                className="ml-auto text-red-500 hover:underline"
              >
                Verwijderen
              </button>
            </div>
          </div>
        ))}
      </div>

      <div className="mb-8 flex flex-wrap gap-2">
        <button
          type="button"
          onClick={() => addCustom("text")}
          className="rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-sm font-medium text-slate-700 hover:bg-slate-50"
        >
          + Kort antwoord
        </button>
        <button
          type="button"
          onClick={() => addCustom("textarea")}
          className="rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-sm font-medium text-slate-700 hover:bg-slate-50"
        >
          + Lang antwoord
        </button>
        <button
          type="button"
          onClick={() => addCustom("choice")}
          className="rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-sm font-medium text-slate-700 hover:bg-slate-50"
        >
          + Meerkeuze
        </button>
      </div>

      {err && <p className="mb-3 text-sm text-red-600">{err}</p>}

      <button
        onClick={save}
        disabled={saving}
        className="rounded-lg bg-emerald-500 px-5 py-2.5 font-semibold text-white shadow-sm hover:bg-emerald-600 disabled:opacity-50"
      >
        {saving ? "Opslaan..." : "Formulier aanmaken"}
      </button>
    </main>
  );
}
