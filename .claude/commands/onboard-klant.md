---
description: "Onboard een nieuwe Efficienter bouw-/softwareklant — interview + zet een klant-CLAUDE.md klaar in de klanten/-map"
---

# /onboard-klant — Klant Onboarding (Efficienter)

Onboard een nieuwe klant voor **Efficienter** (bureau dat maatwerk software/websites bouwt).
Dit is GEEN ads-onboarding — het gaat om **bouwprojecten** (Shopify, configurators, apps, automatiseringen).

Resultaat: een nette `klanten/{slug}/CLAUDE.md` met alles wat we over de klant en het project weten,
zodat elke sessie in die map meteen de juiste context heeft.

**Draai dit vanuit de root van de workspace** (`~/efficienter-hq`), zodat de klant in `klanten/` landt.

---

## STAP 0 — Lees eerst

- De workspace-`CLAUDE.md` (top-level) en `efficienter/CLAUDE.md` voor hoe Efficienter werkt,
  de voice, en het trajectproces. Gebruik dat als context.
- Bestaat `klanten/{slug}/` al? Dan updaten we die i.p.v. overschrijven — meld dat.

---

## STAP 1 — Interview (vraag één tegelijk)

Stel deze vragen ÉÉN VOOR ÉÉN. Sla over wat al in `$ARGUMENTS` of bekend is. Neem geen aannames —
bij twijfel: doorvragen, niks verzinnen.

1. **Klant + contact** — bedrijfsnaam, contactpersoon, wat ze doen (branche), hoe groot / wat voor bedrijf.
2. **Project + scope** — wat bouwen we precies? Welke tech-stack (Shopify, custom, app…)? Wat valt binnen en buiten scope?
3. **Status + planning** — waar staat het nu (net getekend / in aanbouw / bijna klaar)? Deadlines/milestones? Verwachte duur?
4. **Deal + betaling** — dealwaarde en betaalafspraak (vooraf, 50/50, in termijnen…).
5. **Content** — doen wij de copywriting/content? Zo ja, in welke stem/taal? En wie levert wijzigingen aan?
6. **Communicatie + toegang** — via welk kanaal schakel je (WhatsApp/mail)? Welke toegang hebben we nodig (Shopify-collaborator, domein/DNS, logins, merkassets)?
7. **Bijzonderheden** — dingen om rekening mee te houden (bijv. klant levert traag aan, specifieke wensen, deadlines die hard zijn).

Niet meer dan nodig. Bij een klein project mag je vragen combineren.

---

## STAP 2 — Kwaliteitscheck (vóór tonen)

- [ ] Geen verzonnen details — alles komt van de klant of is duidelijk gemarkeerd als "nog bevestigen".
- [ ] Dealwaarde, betaling, status en scope staan er concreet in.
- [ ] Als wij content doen: is de stem vastgelegd (of gemarkeerd als voorstel)?
- [ ] Toegang die we nodig hebben staat als checklist.
- [ ] Bijzonderheden (bijv. trage aanlevering) staan erin, want die sturen de planning.

---

## STAP 3 — Toon concept + keur goed

Toon de complete klant-CLAUDE.md (zie Format) en vraag: **"Akkoord om op te slaan, of iets aanpassen?"**
- Aanpassen → pas aan, toon opnieuw.
- Akkoord → STAP 4.

---

## STAP 4 — Opslaan (na akkoord)

- Maak `klanten/{slug}/` aan ({slug} = bedrijfsnaam in kebab-case, bijv. `de-sloten-specialist`).
- Schrijf `klanten/{slug}/CLAUDE.md`.
- Bevestig het pad. Stel voor om te committen/pushen (maar doe dat alleen als de gebruiker het vraagt).
- Bestaat het mapje al? Update de bestaande CLAUDE.md, overschrijf niet blind.

---

## OUTPUT FORMAT — de klant-CLAUDE.md

```markdown
# Klant — {Bedrijfsnaam}

{één zin: wie ze zijn + wat Efficienter voor ze bouwt}

Klant van [[Efficienter]].

## Klant Config
| Veld | Waarde |
|------|--------|
| Bedrijf | {naam} |
| Contactpersoon | {naam + rol} |
| Communicatie | {kanaal} |
| Branche | {wat ze doen} |
| Doel van de klant | {wat ze willen bereiken} |

## Project
| Veld | Waarde |
|------|--------|
| Wat we bouwen | {project + scope} |
| Tech-stack | {Shopify/custom/…} |
| Content | {doen wij copy? afspraken} |
| Status | {fase + datum} |
| Planning | {duur, milestones, deadlines} |
| Dealwaarde | {€} |
| Betaling | {afspraak} |

## Content & Voice (indien van toepassing)
{taal + toon; markeer als "VOORSTEL — bevestigen" als niet expliciet afgesproken}

## Toegang nodig
- [ ] {bv. Shopify collaborator access}
- [ ] {domein / DNS}
- [ ] {logins / accounts}
- [ ] {merkassets / logo / content-input}

## Rules for Claude
- {content-taal + stem}
- {bijzonderheden, bv. klant levert traag aan → hou daar rekening mee}
- Denk mee en push terug; geen AI-clichés; claim alleen wat afgesproken is.

## Key Info
- Contact: {naam + kanaal}
- Deal: {€ + betaling}
- Stack: {tech}
```

---

## STEM

- Nederlands, nuchter en concreet (Efficienter-stijl).
- De klant-CLAUDE.md is een intern werkdocument: helder en feitelijk, geen marketingtaal.
- Als wij content voor de klant maken, staat díe stem apart in de "Content & Voice"-sectie —
  verwar de interne stem niet met de stem waarin je content voor de klant schrijft.
