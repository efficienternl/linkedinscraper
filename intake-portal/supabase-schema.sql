-- Intake Portal — database schema
-- Draai dit één keer in je Supabase project: Dashboard → SQL Editor → plak → Run.

-- Forms: elke form die je maakt (titel + de velden/vragen)
create table if not exists forms (
  id uuid primary key default gen_random_uuid(),
  title text not null,
  fields jsonb not null default '[]',
  created_at timestamptz not null default now()
);

-- Responses: elk ingevuld formulier van een klant
create table if not exists responses (
  id uuid primary key default gen_random_uuid(),
  form_id uuid not null references forms(id) on delete cascade,
  answers jsonb not null default '{}',
  submitted_at timestamptz not null default now()
);

-- Row Level Security aanzetten
alter table forms enable row level security;
alter table responses enable row level security;

-- Publiek: iedereen met de link mag een form LEZEN (nodig om 'm te tonen)
drop policy if exists "public can read forms" on forms;
create policy "public can read forms" on forms for select using (true);

-- Publiek: iedereen mag een ingevuld formulier INSTUREN
drop policy if exists "public can insert responses" on responses;
create policy "public can insert responses" on responses for insert with check (true);

-- Let op: forms MAKEN en responses LEZEN doen wij server-side met de service_role key,
-- die RLS omzeilt. Klanten kunnen dus geen andermans antwoorden lezen.
