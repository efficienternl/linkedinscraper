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

        click.echo(f"🔍 Starting Apify search: {', '.join(keywords_list)}", err=True)
        if location:
            click.echo(f"   Location: {location}", err=True)
        if job_title:
            click.echo(f"   Job title: {job_title}", err=True)
        if seniority:
            click.echo(f"   Seniority: {seniority}", err=True)
        if manager_type:
            click.echo(f"   Manager type: {manager_type}", err=True)

        # Collect all profiles from all keyword searches
        all_profiles = []

        # Search for each keyword
        for kw in keywords_list:
            # Build input data for this search
            input_data = {
                "searchQuery": kw,
                "maxResults": min(limit, 1000),
            }

            # Add seniority level filter (use exact Apify values)
            if seniority:
                seniority_lower = seniority.lower()
                if seniority_lower == "manager":
                    input_data["seniorityLevelFilter"] = ["Entry Level Manager", "Experienced Manager"]
                elif seniority_lower == "director":
                    input_data["seniorityLevelFilter"] = ["Director", "Vice President"]
                elif seniority_lower == "executive":
                    input_data["seniorityLevelFilter"] = ["CXO", "Owner / Partner"]

            # Add job title filter
            if job_title:
                input_data["currentJobTitleFilter"] = [job_title]
            elif manager_type:
                input_data["currentJobTitleFilter"] = [manager_type]

            # Add location filter
            if location:
                input_data["locationFilter"] = [location]

            click.echo(f"  🔎 Searching: {kw}", err=True)

            # Call actor for this keyword
            run_id = self._run_actor(self.actor_id, input_data)

            # Wait for completion
            click.echo(f"  ⏳ Waiting (run: {run_id})...", err=True)
            results = self._wait_for_results(run_id)

            # Extract URLs for this search
            urls = self._extract_urls(results)
            click.echo(f"  ✓ Found {len(urls)}", err=True)
            all_profiles.extend(urls)

        profile_urls = all_profiles
        click.echo(f"✓ Total found: {len(profile_urls)} profiles", err=True)

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

        # Log what we got for debugging
        if not results:
            click.echo(f"  [DEBUG] Empty results from Apify", err=True)
            return urls

        click.echo(f"  [DEBUG] Got {len(results)} items from Apify", err=True)
        if results:
            click.echo(f"  [DEBUG] First item keys: {list(results[0].keys())}", err=True)

        for result in results:
            # Try multiple possible field names
            profile_url = None

            if "profileUrl" in result:
                profile_url = result["profileUrl"]
            elif "url" in result:
                if "linkedin.com" in result["url"]:
                    profile_url = result["url"]
            elif "link" in result:
                if "linkedin.com" in result["link"]:
                    profile_url = result["link"]
            elif "profile_url" in result:
                profile_url = result["profile_url"]

            if profile_url:
                urls.append(profile_url)
            else:
                # Log unexpected format
                click.echo(f"  [DEBUG] Unexpected result format: {list(result.keys())[:5]}", err=True)

        return urls
