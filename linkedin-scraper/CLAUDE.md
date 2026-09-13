# LinkedIn Scraper

Gedeelde tool (niet een los product) — bulk-scraping voor profielen, bedrijfspagina's en vacatures van LinkedIn, voor leadgen/verrijking.

Gebouwd op `linkedin_scraper` (PyPI v3.1.2), async/Playwright, resumable jobs, ingebouwde rate-limit-handling.

## Waarom

LeadClip en LeadsInbox hebben leadlijsten nodig. Dit is de scraper om die lijsten te vullen/verrijken vanuit LinkedIn.

## Hoe gebruiken

1. `python cli.py login` — handmatig inloggen, eenmalig
2. `python cli.py person <url>` — losse profiel
3. `python cli.py people --file urls.txt --out output/results.jsonl` — bulk, resumable
4. `python cli.py company <url>` — bedrijfspagina
5. `python cli.py jobs --keywords "..." --location "..." --limit 25 --out jobs.jsonl` — vacatures

Zie `README.md` voor volledige docs.

## Geen wachtwoord-handling

De tool vraagt of bewaard **nooit** je LinkedIn-wachtwoord. Eerste login is handmatig (jij voert het in), daarna werkt alles op opgeslagen sessie (cookies).
