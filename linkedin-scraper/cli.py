#!/usr/bin/env python
"""LinkedIn scraper CLI."""
import asyncio
import sys
from pathlib import Path
import click

from linkedin_scraper import (
    PersonScraper,
    CompanyScraper,
    JobScraper,
    JobSearchScraper,
    BrowserManager,
    AuthenticationError,
)
from linkedin_scraper.core.auth import wait_for_manual_login
from linkedin_cli.config import SESSION_FILE, OUTPUT_DIR, HEADLESS
from linkedin_cli.jsonl_store import normalize_url, load_existing_keys, append_jsonl, print_json
from linkedin_cli.bulk import scrape_urls_to_jsonl
from linkedin_cli.apify import ApifyClient


@click.group()
def cli():
    """LinkedIn scraper CLI voor bulk-scraping van profielen, bedrijven en vacatures."""
    pass


@cli.command()
@click.option("--session-file", default=SESSION_FILE, show_default=True, help="Pad naar sessiebestand.")
def login(session_file: str) -> None:
    """Handmatig inloggen bij LinkedIn en sessie opslaan."""
    asyncio.run(_login(session_file))


async def _login(session_file: str) -> None:
    """Login implementation."""
    try:
        async with BrowserManager(headless=False) as browser:
            await browser.page.goto("https://www.linkedin.com/login")
            click.echo("🔐 Log handmatig in bij LinkedIn in het geopende venster.")
            click.echo("   (maximaal 5 minuten, inclusief 2FA/captcha)")

            try:
                await wait_for_manual_login(browser.page, timeout=300000)
            except AuthenticationError as e:
                click.echo(f"✗ Login mislukt: {e}", err=True)
                raise SystemExit(1)

            await browser.save_session(session_file)
            click.echo(f"✓ Ingelogd. Sessie opgeslagen als: {session_file}")
    except Exception as e:
        click.echo(f"✗ Fout bij inloggen: {e}", err=True)
        raise SystemExit(1)


@cli.command()
@click.argument("url")
@click.option("--session-file", default=SESSION_FILE, show_default=True)
@click.option("--headless/--no-headless", default=HEADLESS, show_default=True)
@click.option("--out", type=click.Path(), default=None, help="Optioneel: opslaan als JSONL bestand.")
def person(url: str, session_file: str, headless: bool, out: str) -> None:
    """Scrape LinkedIn profiel."""
    asyncio.run(_scrape_one(PersonScraper, url, session_file, headless, out))


@cli.command()
@click.argument("url")
@click.option("--session-file", default=SESSION_FILE, show_default=True)
@click.option("--headless/--no-headless", default=HEADLESS, show_default=True)
@click.option("--out", type=click.Path(), default=None, help="Optioneel: opslaan als JSONL bestand.")
def company(url: str, session_file: str, headless: bool, out: str) -> None:
    """Scrape LinkedIn bedrijfspagina."""
    asyncio.run(_scrape_one(CompanyScraper, url, session_file, headless, out))


async def _scrape_one(scraper_cls, url: str, session_file: str, headless: bool, out: str) -> None:
    """Scrape a single URL and output as JSON."""
    session_path = Path(session_file)
    if not session_path.exists():
        click.echo(f"✗ Geen sessie gevonden: {session_file}", err=True)
        click.echo("Run eerst: python cli.py login", err=True)
        raise SystemExit(1)

    try:
        async with BrowserManager(headless=headless) as browser:
            await browser.load_session(session_file)
            scraper = scraper_cls(browser.page)
            result = await scraper.scrape(url)

            record = {
                "url": url,
                "status": "ok",
                "data": result.model_dump(mode="json")
            }

            print_json(record)

            if out:
                append_jsonl(out, record)
                click.echo(f"✓ Opgeslagen in: {out}", err=True)

    except AuthenticationError:
        click.echo("✗ Sessie verlopen of ongeldig.", err=True)
        click.echo("Run: python cli.py login", err=True)
        raise SystemExit(1)
    except Exception as e:
        click.echo(f"✗ Fout: {e}", err=True)
        raise SystemExit(1)


@cli.command()
@click.option("--file", "file_path", required=True, type=click.Path(exists=True), help="Tekstbestand, één LinkedIn-URL per regel.")
@click.option("--out", required=True, type=click.Path(), help="JSONL output bestand (resumable).")
@click.option("--session-file", default=SESSION_FILE, show_default=True)
@click.option("--headless/--no-headless", default=HEADLESS, show_default=True)
@click.option("--delay-min", default=5.0, show_default=True, help="Min. pauze tussen scrapes (seconden).")
@click.option("--delay-max", default=15.0, show_default=True, help="Max. pauze tussen scrapes (seconden).")
@click.option("--max-consecutive-errors", default=3, show_default=True, help="Stoppen na N opeenvolgende fouten.")
def people(
    file_path: str,
    out: str,
    session_file: str,
    headless: bool,
    delay_min: float,
    delay_max: float,
    max_consecutive_errors: int,
) -> None:
    """Bulk-scrape LinkedIn profielen uit een bestand."""
    urls = _read_url_file(file_path)
    if not urls:
        click.echo("✗ Geen URLs gevonden in bestand.", err=True)
        raise SystemExit(1)

    asyncio.run(
        _bulk_scrape(
            PersonScraper,
            urls,
            out,
            session_file,
            headless,
            (delay_min, delay_max),
            max_consecutive_errors,
        )
    )


@cli.command()
@click.option("--keywords", required=True, help="Zoekterm (e.g. 'python developer').")
@click.option("--location", default=None, help="Locatie filter (e.g. 'Amsterdam').")
@click.option("--limit", default=25, show_default=True, help="Max. aantal vacatures.")
@click.option("--out", required=True, type=click.Path(), help="JSONL output bestand.")
@click.option("--session-file", default=SESSION_FILE, show_default=True)
@click.option("--headless/--no-headless", default=HEADLESS, show_default=True)
@click.option("--delay-min", default=5.0, show_default=True, help="Min. pauze tussen scrapes (seconden).")
@click.option("--delay-max", default=15.0, show_default=True, help="Max. pauze tussen scrapes (seconden).")
@click.option("--max-consecutive-errors", default=3, show_default=True)
def jobs(
    keywords: str,
    location: str,
    limit: int,
    out: str,
    session_file: str,
    headless: bool,
    delay_min: float,
    delay_max: float,
    max_consecutive_errors: int,
) -> None:
    """Zoek vacatures en scrape details."""
    asyncio.run(
        _search_and_scrape_jobs(
            keywords,
            location,
            limit,
            out,
            session_file,
            headless,
            (delay_min, delay_max),
            max_consecutive_errors,
        )
    )


async def _search_and_scrape_jobs(
    keywords: str,
    location: str,
    limit: int,
    out: str,
    session_file: str,
    headless: bool,
    delay_range: tuple,
    max_consecutive_errors: int,
) -> None:
    """Search jobs and scrape each result."""
    session_path = Path(session_file)
    if not session_path.exists():
        click.echo(f"✗ Geen sessie gevonden: {session_file}", err=True)
        click.echo("Run eerst: python cli.py login", err=True)
        raise SystemExit(1)

    try:
        async with BrowserManager(headless=headless) as browser:
            await browser.load_session(session_file)

            click.echo(f"🔍 Zoeken naar vacatures: {keywords}", err=True)
            if location:
                click.echo(f"   Locatie: {location}", err=True)

            search_scraper = JobSearchScraper(browser.page)
            job_urls = await search_scraper.search(
                keywords=keywords,
                location=location,
                limit=limit,
            )

            if not job_urls:
                click.echo("✗ Geen vacatures gevonden.", err=True)
                raise SystemExit(1)

            click.echo(f"✓ Gevonden: {len(job_urls)} vacatures", err=True)
            click.echo("", err=True)

            await scrape_urls_to_jsonl(
                job_urls,
                browser.page,
                JobScraper,
                out,
                delay_range=delay_range,
                max_consecutive_errors=max_consecutive_errors,
            )

    except AuthenticationError:
        click.echo("✗ Sessie verlopen of ongeldig.", err=True)
        click.echo("Run: python cli.py login", err=True)
        raise SystemExit(1)
    except Exception as e:
        click.echo(f"✗ Fout: {e}", err=True)
        raise SystemExit(1)


async def _bulk_scrape(
    scraper_cls,
    urls: list,
    out: str,
    session_file: str,
    headless: bool,
    delay_range: tuple,
    max_consecutive_errors: int,
) -> None:
    """Bulk scrape using shared engine."""
    session_path = Path(session_file)
    if not session_path.exists():
        click.echo(f"✗ Geen sessie gevonden: {session_file}", err=True)
        click.echo("Run eerst: python cli.py login", err=True)
        raise SystemExit(1)

    try:
        async with BrowserManager(headless=headless) as browser:
            await browser.load_session(session_file)
            await scrape_urls_to_jsonl(
                urls,
                browser.page,
                scraper_cls,
                out,
                delay_range=delay_range,
                max_consecutive_errors=max_consecutive_errors,
            )
    except AuthenticationError:
        click.echo("✗ Sessie verlopen of ongeldig.", err=True)
        click.echo("Run: python cli.py login", err=True)
        raise SystemExit(1)
    except Exception as e:
        click.echo(f"✗ Fout: {e}", err=True)
        raise SystemExit(1)


def _read_url_file(file_path: str) -> list:
    """Read URLs from file, one per line."""
    urls = []
    try:
        with open(file_path, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    urls.append(line)
    except Exception as e:
        click.echo(f"✗ Fout bij lezen bestand: {e}", err=True)
        raise SystemExit(1)
    return urls


@cli.command()
@click.option("--keywords", multiple=True, required=True, help="Zoekterm(en) - gebruik meerdere keren voor meerdere keywords (e.g. --keywords 'transport' --keywords 'logistics').")
@click.option("--job-title", multiple=True, default=(), help="Functietitel(s) - gebruik meerdere keren (e.g. --job-title 'manager' --job-title 'director').")
@click.option("--seniority", default=None, type=click.Choice(["manager", "director", "executive"]), help="Seniority level: manager, director, of executive (en hoger).")
@click.option("--manager-type", default=None, help="Type manager (e.g. 'operations', 'logistics', 'supply chain').")
@click.option("--location", default=None, help="Locatie filter (e.g. 'Netherlands').")
@click.option("--limit", default=100, show_default=True, help="Max. aantal profielen per keyword.")
@click.option("--out", required=True, type=click.Path(), help="JSONL output bestand.")
@click.option("--session-file", default=SESSION_FILE, show_default=True)
@click.option("--headless/--no-headless", default=HEADLESS, show_default=True)
@click.option("--delay-min", default=5.0, show_default=True, help="Min. pauze tussen scrapes (seconden).")
@click.option("--delay-max", default=15.0, show_default=True, help="Max. pauze tussen scrapes (seconden).")
@click.option("--max-consecutive-errors", default=3, show_default=True)
@click.option("--apify-token", default=None, help="Apify API token (of uit .env: APIFY_TOKEN).")
def search(
    keywords: tuple,
    job_title: tuple,
    seniority: str,
    manager_type: str,
    location: str,
    limit: int,
    out: str,
    session_file: str,
    headless: bool,
    delay_min: float,
    delay_max: float,
    max_consecutive_errors: int,
    apify_token: str,
) -> None:
    """Zoek via Apify en scrape alle profielen."""
    asyncio.run(
        _search_via_apify(
            list(keywords),  # Convert tuple to list
            list(job_title) if job_title else None,  # Convert to list or None
            seniority,
            manager_type,
            location,
            limit,
            out,
            session_file,
            headless,
            (delay_min, delay_max),
            max_consecutive_errors,
            apify_token,
        )
    )


async def _search_via_apify(
    keywords: list,
    job_title: list,
    seniority: str,
    manager_type: str,
    location: str,
    limit: int,
    out: str,
    session_file: str,
    headless: bool,
    delay_range: tuple,
    max_consecutive_errors: int,
    apify_token: str,
) -> None:
    """Search via Apify and scrape results."""
    import os

    # Get token from param or env
    token = apify_token or os.getenv("APIFY_TOKEN")
    if not token:
        click.echo("✗ APIFY_TOKEN niet gevonden.", err=True)
        click.echo("Gebruik: --apify-token <token> of zet APIFY_TOKEN in .env", err=True)
        raise SystemExit(1)

    # Handle multiple job titles or single manager_type
    job_titles_to_search = job_title if job_title else (None,)

    # Search via Apify (combines all keywords + all job titles)
    try:
        apify = ApifyClient(token)
        profile_urls = apify.search_profiles(
            keywords=keywords,
            location=location,
            job_title=job_titles_to_search,  # Can be list or None
            seniority=seniority,
            manager_type=manager_type,
            limit=limit,
        )
    except Exception as e:
        click.echo(f"✗ Apify search mislukt: {e}", err=True)
        raise SystemExit(1)

    if not profile_urls:
        click.echo("✗ Geen profielen gevonden.", err=True)
        raise SystemExit(1)

    click.echo("", err=True)

    # Scrape all profiles
    session_path = Path(session_file)
    if not session_path.exists():
        click.echo(f"✗ Geen sessie gevonden: {session_file}", err=True)
        click.echo("Run eerst: python cli.py login", err=True)
        raise SystemExit(1)

    try:
        async with BrowserManager(headless=headless) as browser:
            await browser.load_session(session_file)
            await scrape_urls_to_jsonl(
                profile_urls,
                browser.page,
                PersonScraper,
                out,
                delay_range=delay_range,
                max_consecutive_errors=max_consecutive_errors,
            )
    except AuthenticationError:
        click.echo("✗ Sessie verlopen of ongeldig.", err=True)
        click.echo("Run: python cli.py login", err=True)
        raise SystemExit(1)
    except Exception as e:
        click.echo(f"✗ Fout: {e}", err=True)
        raise SystemExit(1)


if __name__ == "__main__":
    cli()
