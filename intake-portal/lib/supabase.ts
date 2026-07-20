import { createClient } from "@supabase/supabase-js";

// Publieke client (browser + publieke form-pagina) — anon key.
// Kan alleen wat Row Level Security toestaat: forms lezen, responses insturen.
export const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
);

// Admin client — ALLEEN server-side gebruiken (nooit in de browser).
// Gebruikt de service_role key en omzeilt RLS: voor forms maken + antwoorden lezen.
export function supabaseAdmin() {
  return createClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.SUPABASE_SERVICE_ROLE_KEY!,
    { auth: { persistSession: false } }
  );
}

// Een veld/vraag in een form
export type Field = {
  id: string;
  label: string;
  type: "text" | "textarea" | "email" | "tel" | "number" | "choice";
  required: boolean;
  standard: boolean; // true = standaard-veld, false = custom vraag
  options?: string[]; // bij type "choice": de keuzeopties
  allowOther?: boolean; // bij type "choice": voeg een "Anders"-optie toe
};

export type Form = {
  id: string;
  title: string;
  fields: Field[];
  created_at: string;
};
