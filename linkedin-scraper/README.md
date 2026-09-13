# LinkedIn Scraper CLI

Bulk-scraper voor LinkedIn-profielen, bedrijfspagina's en vacatures. Gebouwd op `linkedin_scraper` (PyPI) met async/Playwright, ingebouwde rate-limit-handling, en resumable bulk-jobs.

## Vereisten

- Python 3.9+
- Een LinkedIn-account
- ~300MB schijfruimte (voor Playwright Chromium)

## Installatie

```bash
cd ~/efficienter-hq/linkedin-scraper
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
playwright install chromium
```

Verifieer:
```bash
python cli.py --help
```

Moet 5 subcommands tonen: `login`, `person`, `company`, `people`, `jobs`.

## Setup: Eenmalig inloggen

De eerste keer moet je handmatig inloggen bij LinkedIn (je eigen wachtwoord + eventuele 2FA/captcha). De tool bewaard daarna je sessie — alles daarna draait volledig automatisch.

```bash
python cli.py login
```

Dit opent een echt browservenster. Voer je LinkedIn-inloggegevens in, los 2FA op als nodig, en wacht tot het venster automatisch sluit. De sessie wordt opgeslagen als `session.json`.

## Gebruik

### 1. Losse profiel scrapen

```bash
python cli.py person https://www.linkedin.com/in/naam/
```

Output: mooi JSON naar stdout.

Optioneel opslaan in een JSONL-bestand:
```bash
python cli.py person https://www.linkedin.com/in/naam/ --out output/test.jsonl
```

### 2. Bedrijfspagina scrapen

```bash
python cli.py company https://www.linkedin.com/company/microsoft/
```

### 3. Bulk-scrape profielen

Maak een tekstbestand met LinkedIn-profiel-URLs, één per regel:

`profielen.txt`:
```
https://www.linkedin.com/in/alice/
https://www.linkedin.com/in/bob/
https://www.linkedin.com/in/charlie/
```

Scrape ze:
```bash
python cli.py people --file profielen.txt --out output/results.jsonl
```

Output: JSONL-bestand met één record per regel (JSON-object met `url`, `status`, `data`).

**Resumable**: Onderbreek met Ctrl+C na enkele URLs, voer exact hetzelfde commando opnieuw uit — het slaat al-verwerkte profielen over en gaat verder.

Meer opties:
```bash
python cli.py people --help
```

### 4. Vacatures zoeken en scrapen

```bash
python cli.py jobs --keywords "python developer" --location "Amsterdam" --limit 25 --out output/jobs.jsonl
```

Output: JSONL met volledige vacature-details per hit.

Opties:
- `--keywords` (verplicht): zoekterm
- `--location` (optioneel): lokatie-filter
- `--limit` (default 25): max. aantal vacatures
- `--out` (verplicht): JSONL output-bestand
- `--delay-min`/`--delay-max`: pauze tussen scrapes (default 5–15s)
- `--headless/--no-headless`: browser-modus (default headless)

## Hervatten na onderbreking

`people` en `jobs` zijn **resumable**: ze slaan al-verwerkte URLs over en gaan verder waar ze stopten.

```bash
# Start bulk-job
python cli.py people --file grote-lijst.txt --out output/results.jsonl

# (Ctrl+C na een paar minuten)

# Voer hetzelfde commando uit — gaat verder waar het stopte
python cli.py people --file grote-lijst.txt --out output/results.jsonl
```

## Rate limiting & pauzes

De tool:
- Pauzeert automatisch als LinkedIn je rate-limited (default: 5 minuten wachten)
- Voegt willekeurige vertraging in tussen scrapes (default 5–15s) om te voorkomen dat je geblokkeerd wordt
- Stopt na 3 opeenvolgende fouten (instelbaar met `--max-consecutive-errors`)

Zet `--delay-min` en `--delay-max` hoger als je voorzichtig wil zijn:
```bash
python cli.py people --file urls.txt --out output/results.jsonl --delay-min 15 --delay-max 30
```

## Problemen

### "Geen sessie gevonden"
Run eerst: `python cli.py login`

### "Sessie verlopen"
LinkedIn-sessies vervallen na een paar uur. Run opnieuw: `python cli.py login`

### "Rate limit geraakt"
De tool wacht automatisch. Dit is LinkedIn die je vraagt om te vertragen — het is normaal. Laat het draaien.

## Output format

JSONL (JSON Lines): elk scrape-resultaat is één JSON-regel:

```json
{"url": "https://www.linkedin.com/in/alice/", "status": "ok", "data": {"name": "Alice", "location": "Amsterdam", ...}}
{"url": "https://www.linkedin.com/in/bob/", "status": "ok", "data": {"name": "Bob", ...}}
{"url": "https://www.linkedin.com/in/charlie/", "status": "failed", "error": "Profiel niet gevonden"}
```

Parse dit later met:
```python
import json
with open("output/results.jsonl") as f:
    for line in f:
        record = json.loads(line)
        print(record["url"], record["status"])
```

## Veiligheid & privacy

- Je wachtwoord wordt **nooit** opgeslagen of gebruikt na de eerste login. Alles draait op cookies/sessie.
- `session.json` wordt genegeerd door git (zie `.gitignore`).
- Als je output JSONL'jes ergens opslaat buiten de `output/` map, gitignore die zelf — opgescraping LinkedIn-data mag niet in je repo belanden.

## Tips

- Test eerst met `--limit 2` of `--limit 5` voordat je grote bulk-jobs draait.
- Zet `--no-headless` als je debugging wil doen (ziet je de browser).
- LinkedIn detecteert headless-browsing; dit werkt alleen omdat we een echte sessie reuse en afzonderlijke scrapes doen met vertraging.
