"""Apify LinkedIn search integration."""
import time
import requests
import click
import os


class ApifyClient:
    """Simple Apify API client for LinkedIn search."""

    def __init__(self, api_token: str):
        self.api_token = api_token
        self.base_url = "https://api.apify.com/v2"
        # Get actor ID from env or use default
        self.actor_id = os.getenv("APIFY_ACTOR_ID", "nwua9Oy5YrADL7ZAj")

    def search_profiles(
        self,
        keywords,
        location: str = None,
        job_title = None,
        seniority: str = None,
        manager_type: str = None,
        limit: int = 100,
    ) -> list:
        """
        Search LinkedIn profiles via Apify.

        Returns list of profile URLs matching search criteria.

        Args:
            keywords: Search term(s) - string or list of strings
            location: Location filter
            job_title: Specific job title(s) - string, list, or tuple
            seniority: "manager", "director", "executive" (includes higher levels)
            manager_type: Type of manager (e.g., "operations", "logistics", "supply chain")
            limit: Max results per keyword
        """
        # Handle both single string and list of keywords
        if isinstance(keywords, str):
            keywords_list = [keywords]
        else:
            keywords_list = keywords if isinstance(keywords, list) else [keywords]

        # Handle job titles (can be string, list, or tuple)
        if job_title is None:
            job_titles_list = [None]
        elif isinstance(job_title, str):
            job_titles_list = [job_title]
        elif isinstance(job_title, (list, tuple)):
            job_titles_list = list(job_title) if job_title else [None]
        else:
            job_titles_list = [None]

        # Build search URLs for all combinations of keywords + job titles
        search_urls = []
        for kw in keywords_list:
            for title in job_titles_list:
                search_urls.append(
                    self._build_search_url(kw, location, title, seniority, manager_type)
                )

        input_data = {
            "searchUrls": search_urls,
            "maxResults": min(limit, 1000),  # Apify limit per URL
        }

        click.echo(f"🔍 Starting Apify search: {', '.join(keywords_list)}", err=True)
        if location:
            click.echo(f"   Location: {location}", err=True)
        if job_title:
            click.echo(f"   Job title: {job_title}", err=True)
        if seniority:
            click.echo(f"   Seniority: {seniority}", err=True)
        if manager_type:
            click.echo(f"   Manager type: {manager_type}", err=True)

        # Call actor (uses self.actor_id from env or default)
        run_id = self._run_actor(self.actor_id, input_data)

        # Wait for completion
        click.echo(f"⏳ Waiting for Apify to finish (run: {run_id})...", err=True)
        results = self._wait_for_results(run_id)

        # Extract profile URLs
        profile_urls = self._extract_urls(results)
        click.echo(f"✓ Found {len(profile_urls)} profiles", err=True)

        return profile_urls

    def _build_search_url(
        self,
        keywords: str,
        location: str = None,
        job_title: str = None,
        seniority: str = None,
        manager_type: str = None,
    ) -> str:
        """Build LinkedIn search URL with filters."""
        search_parts = [keywords]

        # Add seniority levels (manager or higher) - includes both English & Dutch
        if seniority:
            seniority = seniority.lower()
            if seniority == "manager":
                search_parts.append('title:("manager" OR "manager" OR "medewerker" OR "coördinator")')
            elif seniority == "director":
                search_parts.append('title:("manager" OR "director" OR "head of" OR "hoofd" OR "vp" OR "vice president" OR "vicevoorzitter" OR "eigenaar" OR "owner" OR "directeur" OR "directrice")')
            elif seniority == "executive":
                search_parts.append('title:("manager" OR "director" OR "head of" OR "hoofd" OR "vp" OR "vice president" OR "vicevoorzitter" OR "ceo" OR "cto" OR "cfo" OR "coo" OR "owner" OR "eigenaar" OR "founder" OR "oprichter" OR "directeur" OR "directrice" OR "bestuursvoorzitter" OR "voorzitter")')

        # Add specific job title
        if job_title:
            if manager_type:
                search_parts.append(f'title:("{manager_type} manager" OR "{manager_type}")')
            else:
                search_parts.append(f'title:"{job_title}"')
        elif manager_type:
            # Just manager type without specific title
            search_parts.append(f'title:"{manager_type} manager"')

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
