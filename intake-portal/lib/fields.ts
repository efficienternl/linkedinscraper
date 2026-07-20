import type { Field } from "./supabase";

// Standaard-velden die je per klant kunt aanvinken.
// Deze gelden voor bijna elke klant, ongeacht de build.
// Regel: als een standaard-veld is aangevinkt, is het altijd verplicht.
export const STANDARD_FIELDS: Field[] = [
  { id: "bedrijfsnaam", label: "Bedrijfsnaam (zoals op KvK)", type: "text", required: true, standard: true },
  { id: "kvk", label: "KvK-nummer", type: "text", required: true, standard: true },
  { id: "btw", label: "BTW-nummer", type: "text", required: true, standard: true },
  { id: "contactpersoon", label: "Contactpersoon + functie", type: "text", required: true, standard: true },
  { id: "telefoon", label: "Telefoon / WhatsApp", type: "tel", required: true, standard: true },
  { id: "email", label: "E-mailadres", type: "email", required: true, standard: true },
  { id: "adres", label: "Vestigingsadres", type: "text", required: true, standard: true },
  { id: "website", label: "Website", type: "text", required: true, standard: true },
  { id: "bereikbaarheid", label: "Bereikbaarheid / openingstijden", type: "textarea", required: true, standard: true },
  { id: "facturatie", label: "Facturatiegegevens (factuur-e-mail, evt. referentie)", type: "text", required: true, standard: true },
  { id: "huisstijl", label: "Logo & huisstijl (link naar assets of beschrijving)", type: "textarea", required: true, standard: true },
];

// Welke standaard-velden staan default aangevinkt
export const DEFAULT_CHECKED = ["bedrijfsnaam", "contactpersoon", "telefoon", "email"];
