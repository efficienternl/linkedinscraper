"use server";

import { supabaseAdmin } from "./supabase";
import type { Field } from "./supabase";
import { notifyNewResponse } from "./email";
import { redirect } from "next/navigation";
import { revalidatePath } from "next/cache";

// Een nieuwe form aanmaken (admin, server-side).
export async function createForm(title: string, fields: Field[]) {
  const admin = supabaseAdmin();
  const { data, error } = await admin
    .from("forms")
    .insert({ title, fields })
    .select("id")
    .single();
  if (error) throw new Error(error.message);
  redirect(`/?nieuw=${data.id}`);
}

// Een form verwijderen (verwijdert ook de antwoorden via cascade).
export async function deleteForm(id: string) {
  const admin = supabaseAdmin();
  const { error } = await admin.from("forms").delete().eq("id", id);
  if (error) throw new Error(error.message);
  revalidatePath("/");
}

// Een ingevuld formulier van een klant opslaan + melding sturen.
export async function submitResponse(
  formId: string,
  answers: Record<string, string>
) {
  const admin = supabaseAdmin();
  const { error } = await admin
    .from("responses")
    .insert({ form_id: formId, answers });
  if (error) throw new Error(error.message);

  const { data: form } = await admin
    .from("forms")
    .select("title")
    .eq("id", formId)
    .single();
  await notifyNewResponse(form?.title ?? "Onboarding", formId);
}
