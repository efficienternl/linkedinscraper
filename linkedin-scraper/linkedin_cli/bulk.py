"""Bulk scraping engine with resumability and rate-limit handling."""
import asyncio
import random
from typing import List, Type
from playwright.async_api import Page
import click

from linkedin_scraper import (
    BrowserManager,
    PersonScraper,
    CompanyScraper,
    JobScraper,
    AuthenticationError,
    RateLimitError,
    ProfileNotFoundError,
    ElementNotFoundError,
    NetworkError,
    ScrapingError,
)
from .jsonl_store import normalize_url, load_existing_keys, append_jsonl


async def scrape_urls_to_jsonl(
    urls: List[str],
    page: Page,
    scraper_cls: Type,
    out_path: str,
    delay_range: tuple = (5.0, 15.0),
    max_consecutive_errors: int = 3,
) -> None:
    """Scrape URLs to JSONL, with resumability and rate-limit handling."""
    done = load_existing_keys(out_path)
    consecutive_errors = 0
    total = len(urls)
    processed = 0

    for idx, url in enumerate(urls, 1):
        key = normalize_url(url)
        if key in done:
            click.echo(f"[{idx}/{total}] Overslaan (al gedaan): {url}", err=True)
            continue

        scraper = scraper_cls(page)
        try:
            click.echo(f"[{idx}/{total}] Scraping: {url}", err=True)
            result = await scraper.scrape(url)
            append_jsonl(out_path, {
                "url": url,
                "status": "ok",
                "data": result.model_dump(mode="json")
            })
            click.echo(f"  ✓ OK", err=True)
            consecutive_errors = 0
            processed += 1

        except RateLimitError as e:
            wait = e.suggested_wait_time or 300
            click.echo(f"  ⚠️  Rate limit geraakt, wacht {wait}s...", err=True)
            append_jsonl(out_path, {
                "url": url,
                "status": "rate_limited",
                "wait_time": wait
            })
            await asyncio.sleep(wait)

            try:
                result = await scraper_cls(page).scrape(url)
                append_jsonl(out_path, {
                    "url": url,
                    "status": "ok",
                    "data": result.model_dump(mode="json")
                })
                click.echo(f"  ✓ OK (na retry)", err=True)
                consecutive_errors = 0
                processed += 1
            except Exception as e2:
                append_jsonl(out_path, {
                    "url": url,
                    "status": "failed",
                    "error": str(e2)
                })
                click.echo(f"  ✗ Fout: {e2}", err=True)
                consecutive_errors += 1

        except AuthenticationError:
            append_jsonl(out_path, {
                "url": url,
                "status": "failed",
                "error": "Sessie verlopen of ongeldig"
            })
            click.echo("  ✗ Sessie verlopen. Run: python cli.py login", err=True)
            raise SystemExit(3)

        except (ProfileNotFoundError, ElementNotFoundError, NetworkError, ScrapingError) as e:
            append_jsonl(out_path, {
                "url": url,
                "status": "failed",
                "error": str(e)
            })
            click.echo(f"  ✗ Fout: {e}", err=True)
            consecutive_errors += 1

        if consecutive_errors >= max_consecutive_errors:
            click.echo(f"\n✗ Gestopt na {consecutive_errors} opeenvolgende fouten.", err=True)
            raise SystemExit(1)

        await asyncio.sleep(random.uniform(*delay_range))

    click.echo(f"\n✓ Klaar: {processed} succesvol, {total - processed} overgeslagen/mislukt", err=True)
