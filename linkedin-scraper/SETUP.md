# Setup Instructies

Voor jouw agent die dit lokaal gaat runnen.

## 1. Download/Clone deze repo

```bash
git clone https://github.com/efficienternl/linkedin-scraper.git
cd linkedin-scraper
```

## 2. Start de setup

**macOS/Linux:**
```bash
./run.sh
```

**Windows:**
```bash
python -m venv .venv
.venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
playwright install chromium
streamlit run app.py
```

## 3. Wat er gebeurt

`run.sh` doet automatisch:
- ✅ Virtual environment aanmaken
- ✅ Dependencies installeren
- ✅ Playwright Chromium downloaden
- ✅ Web interface starten op `http://localhost:8501`

## 4. Eerste keer: Inloggen

1. Open de web interface (http://localhost:8501)
2. Ga naar tab "🔐 Login"
3. Klik "Start inloggen"
4. Je krijgt een commando te zien
5. Paste dat in je terminal
6. Een browservenster opent → **jij logt zelf in bij LinkedIn**
7. Na login → sessie is opgeslagen

## 5. Nu kan je scrapen

- **Tab "👤 Profiel"** — één LinkedIn profiel scrapen
- **Tab "🏢 Bedrijf"** — bedrijfspagina scrapen
- **Tab "📋 Bulk Profielen"** — bulk-scrape uit tekstbestand
- **Tab "💼 Vacatures"** — vacatures zoeken & scrapen
- **Tab "🔍 Zoeken (Apify)"** — zoeken op LinkedIn via Apify

Alle commando's staan klaar om in je terminal te copy-pasten.

## 6. Output

Alles wordt als **JSONL** opgeslagen in de `output/` folder.
Één profiel per regel in JSON format.

## Troubleshooting

**"Geen sessie gevonden"**
→ Run eerst `python cli.py login` (zie Login tab)

**"Rate limit geraakt"**
→ Tool wacht automatisch. Dit is LinkedIn die zegt: "wacht even"

**Port 8501 al in gebruik**
→ Streamlit gebruiken op ander port:
```bash
streamlit run app.py --server.port 8502
```

## Token

Apify token zit al in `.env`. Niets bijzonders nodig.

## Vragen?

Kijk in `README.md` voor meer details.
