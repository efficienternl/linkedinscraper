"""Apify LinkedIn search integration."""
import time
import requests
import click


class ApifyClient:
    """Simple Apify API client for LinkedIn search."""

    def __init__(self, api_token: str):
        self.api_token = api_token
        self.base_url = "https://api.apify.com/v2"

    def search_profiles(
        self,
        keywords: str,
        location: str = None,
        job_title: str = None,
        limit: int = 100,
    ) -> list:
        """
        Search LinkedIn profiles via Apify.

        Returns list of profile URLs matching search criteria.
        """
        # Use the LinkedIn Search Results Scraper actor
        actor_id = "nwua9Oy5YrADL7ZAj"  # LinkedIn Search Results Scraper

        input_data = {
            "searchUrls": [self._build_search_url(keywords, location, job_title)],
            "maxResults": min(limit, 1000),  # Apify limit
        }

        click.echo(f"🔍 Starting Apify search: {keywords}", err=True)
        if location:
            click.echo(f"   Location: {location}", err=True)
        if job_title:
            click.echo(f"   Job title: {job_title}", err=True)

        # Call actor
        run_id = self._run_actor(actor_id, input_data)

        # Wait for completion
        click.echo(f"⏳ Waiting for Apify to finish (run: {run_id})...", err=True)
        results = self._wait_for_results(run_id)

        # Extract profile URLs
        profile_urls = self._extract_urls(results)
        click.echo(f"✓ Found {len(profile_urls)} profiles", err=True)

        return profile_urls

    def _build_search_url(self, keywords: str, location: str = None, job_title: str = None) -> str:
        """Build LinkedIn search URL with filters."""
        search_parts = [keywords]

        if job_title:
            search_parts.append(f'title:"{job_title}"')

        query = " ".join(search_parts)
        url = f"https://www.linkedin.com/search/results/people/?keywords={query}"

        if location:
            url += f"&location={location}"

        return url

    def _run_actor(self, actor_id: str, input_data: dict) -> str:
        """Start an Apify actor run."""
        url = f"{self.base_url}/acts/{actor_id}/runs"
        headers = {"Authorization": f"Bearer {self.api_token}"}

        try:
            response = requests.post(url, json=input_data, headers=headers, timeout=30)
            response.raise_for_status()
            data = response.json()
            return data["data"]["id"]
        except Exception as e:
            raise Exception(f"Apify actor start failed: {e}")

    def _wait_for_results(self, run_id: str, timeout: int = 600) -> list:
        """Poll for actor completion and get results."""
        url = f"{self.base_url}/actor-runs/{run_id}"
        headers = {"Authorization": f"Bearer {self.api_token}"}

        start_time = time.time()

        while time.time() - start_time < timeout:
            try:
                response = requests.get(url, headers=headers, timeout=30)
                response.raise_for_status()
                data = response.json()
                status = data["data"]["status"]

                if status == "SUCCEEDED":
                    # Get dataset results
                    dataset_id = data["data"]["defaultDatasetId"]
                    return self._get_dataset(dataset_id)
                elif status in ("FAILED", "ABORTED", "TIMED_OUT"):
                    raise Exception(f"Actor run failed with status: {status}")

                click.echo(f"  Status: {status}...", err=True)
                time.sleep(5)

            except Exception as e:
                raise Exception(f"Failed to check actor status: {e}")

        raise Exception(f"Actor run timed out after {timeout}s")

    def _get_dataset(self, dataset_id: str) -> list:
        """Fetch results from Apify dataset."""
        url = f"{self.base_url}/datasets/{dataset_id}/items"
        headers = {"Authorization": f"Bearer {self.api_token}"}

        try:
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise Exception(f"Failed to fetch dataset: {e}")

    def _extract_urls(self, results: list) -> list:
        """Extract LinkedIn profile URLs from Apify results."""
        urls = []

        for result in results:
            # Different results formats depending on actor
            if "profileUrl" in result:
                urls.append(result["profileUrl"])
            elif "url" in result and "linkedin.com/in/" in result["url"]:
                urls.append(result["url"])
            elif "link" in result and "linkedin.com/in/" in result["link"]:
                urls.append(result["link"])

        return urls
