import Image from "next/image";
import { supabaseAdmin } from "@/lib/supabase";
import type { Form } from "@/lib/supabase";
import PublicForm from "@/components/PublicForm";
import { notFound } from "next/navigation";

export const dynamic = "force-dynamic";

export default async function FormPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const admin = supabaseAdmin();
  const { data } = await admin.from("forms").select("*").eq("id", id).single();
  if (!data) notFound();
  const form = data as Form;

  return (
    <main className="mx-auto max-w-xl px-6 py-12">
      <div className="mb-6 flex justify-center">
        <Image src="/logo.png" alt="Efficienter" width={180} height={115} className="h-12 w-auto" priority />
      </div>
      <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm sm:p-8">
        <h1 className="text-xl font-bold text-slate-900">{form.title}</h1>
        <p className="mt-1 mb-6 text-slate-500">
          Vul dit formulier in, dan kunnen we van start. Duurt een paar minuten.
        </p>
        <PublicForm form={form} />
      </div>
    </main>
  );
}
