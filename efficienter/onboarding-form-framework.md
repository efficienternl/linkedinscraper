# Onboarding Form Framework — Efficienter

Het recept waarmee Claude de **best mogelijke intake-form** voor een nieuwe klant genereert.
Jij geeft een briefing → Claude genereert de vragen → jij zet ze zelf in Google Form (zodat je
kunt finetunen). Dit document zorgt dat de gegenereerde vragen scherp en compleet zijn.

> Gebouwd op basis van de echte onboarding-form van **De Sloten Specialist (Jesse)** — dat is de
> gouden standaard: het haalt niet alleen bedrijfsgegevens op, maar trekt de **kennis van de eigenaar**
> uit z'n hoofd zodat die in de build kan.

---

## Het principe

Een goede intake-form doet twee dingen:
1. **De basis vastleggen** — alles wat je nodig hebt om te bouwen en te lanceren (bedrijf, logistiek, juridisch).
2. **De expertise van de eigenaar extraheren** — de kennis, beslislogica en randgevallen die je product
   moet nabootsen (configurator, keuzehulp, flows). **Dit is de belangrijkste laag** en wordt het vaakst vergeten.

Regel: hoe meer de build de klant "vervangt" (een configurator die adviseert zoals de eigenaar zou doen),
hoe dieper je de expertise-laag uitvraagt.

---

## De 4 vaste lagen

### Laag 1 — Bedrijf & juridisch (bijna altijd)
- Officiële bedrijfsnaam (zoals op KvK), KvK- + BTW-nummer
- Contactpersoon + functie
- Telefoon / WhatsApp, e-mail(s) — algemeen én orders/support als dat verschilt
- Vestigingsadres (voor "contact"-pagina), social media links

### Laag 2 — Operationeel & logistiek (webshop/dienstverlening)
- Openingstijden per dag + afwijkende seizoens-/feestdagen
- Bereikbaarheid (telefoon vs winkel), response-tijd op mail, evt. noodservice
- Verzending: kosten, gratis vanaf €X, brievenbuspakket, levertijden, afhalen, verzendpartners

### Laag 3 — Retour & garantie (webshop met producten)
- Retourtermijn, wat is niet-retourneerbaar (maatwerk!), wie betaalt retourkosten
- Garantie per producttype + garantievoorwaarden

### Laag 4 — Expertise-extractie (HET GOUD — altijd, en per klant maatwerk)
Genereer hier vragen die de kennis van de eigenaar ophalen. Patronen:
- **Fouten**: "Welke fouten maken klanten bij zelf-bestellen die jij er nu telefonisch uit haalt?"
- **Beslislogica**: "Als een klant belt met een vaag verzoek — welke vragen stel je, in welke volgorde?"
  (→ dit wordt de keuzehulp/configurator-flow)
- **Advies**: "Wat is je standaard advies per situatie?" (→ de aanbevelings-logica van de tool)
- **Grenzen**: "Wanneer moet iemand tóch bellen i.p.v. de tool gebruiken?" (edge cases)
- **Eigen idee**: "Heb je zelf al een beeld van de keuzehulp — stappen, vragen?"
- **Specifieke flows**: bijzondere processen (nabestellen, certificaten, maatwerk) — wat kan wel/niet?

---

## Per projecttype — waar de nadruk ligt

| Type | Extra nadruk |
|------|-------------|
| **Webshop / website** | Lagen 1-4 volledig. Expertise-laag = productadvies/keuzehulp-logica. |
| **Custom software / app / CMS** | Gebruikersrollen, workflows, welke data, integraties, wie beheert wat. Expertise = het proces dat de software vervangt. |
| **Automatisering / integratie** | Huidig proces stap-voor-stap, welke tools/systemen, triggers, uitzonderingen, wat mag NIET automatisch. |
| **Audit / consulting** | Huidige situatie, doelen, budget/tijd, beslissers, wat is al geprobeerd. Minder logistiek, meer context. |
| **Anders** | Start bij Laag 1 + Laag 4, en vraag door op wat dit project uniek maakt. |

---

## Regels voor de gegenereerde vragen

- **Concreet en in de taal van de klant** — geen jargon. Eén onderwerp per vraag.
- **Vraag door op de expertise-laag** — dat is wat een generiek formulier mist.
- **Markeer welke vragen essentieel zijn** vs nice-to-have, zodat de klant niet afhaakt.
- **Vraag om foto's/voorbeelden** waar relevant (Jesse vraagt foto's van de deur/het slot).
- **Niet te lang** — alleen vragen die de build of lancering echt sturen. Bij twijfel: schrappen of nice-to-have.

---

## De briefing die Claude van jou nodig heeft

Om een goede form te genereren, geef minimaal:
- **Klant**: wie zijn ze, wat doen ze (branche)
- **Project**: wat bouwen we + type (webshop / app / automatisering / audit / anders)
- **Bijzonderheden**: alles wat je al weet (specifieke features, de configurator/keuzehulp, bekende randgevallen)

Hoe meer je meegeeft, hoe minder Claude hoeft te gokken en hoe scherper de vragen.
