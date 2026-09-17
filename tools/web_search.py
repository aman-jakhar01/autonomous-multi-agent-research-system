import os
from urllib.parse import urlparse

from dotenv import load_dotenv
from tavily import TavilyClient

from utils.source_utils import create_source
from utils.retry import retry


load_dotenv()


def get_domain(url: str) -> str:

    domain = urlparse(url).netloc.lower()

    if domain.startswith("www."):
        domain = domain[4:]

    return domain


HIGH_AUTHORITY_DOMAINS = {
    "gov.in",
    "nic.in",
    "gov",
    "who.int",
    "worldbank.org",
    "imf.org",
    "un.org",
    "oecd.org",
    "niti.gov.in",
    "rbi.org.in",
    "ibef.org",
}


ACADEMIC_DOMAINS = {
    "edu",
    "ac.in",
    "nature.com",
    "sciencedirect.com",
    "springer.com",
    "pubmed.ncbi.nlm.nih.gov",
    "arxiv.org",
}


NEWS_DOMAINS = {
    "reuters.com",
    "bbc.com",
    "bbc.co.uk",
    "thehindu.com",
    "indianexpress.com",
    "economictimes.indiatimes.com",
    "hindustantimes.com",
}


def calculate_source_quality(url: str) -> float:

    domain = get_domain(url)

    for trusted_domain in HIGH_AUTHORITY_DOMAINS:

        if domain == trusted_domain or domain.endswith(
            "." + trusted_domain
        ):
            return 1.0

    for academic_domain in ACADEMIC_DOMAINS:

        if domain == academic_domain or domain.endswith(
            "." + academic_domain
        ):
            return 0.85

    for news_domain in NEWS_DOMAINS:

        if domain == news_domain or domain.endswith(
            "." + news_domain
        ):
            return 0.75

    return 0.50


@retry(
    max_attempts=3,
    delay=2,
    backoff=2
)
def web_search(
    query: str,
    tavily_api_key: str | None = None
) -> list:

    """
    Search Tavily using either:
    - user-provided API key
    - .env fallback
    """

    api_key = (
        tavily_api_key
        or os.getenv("TAVILY_API_KEY")
    )

    if not api_key:
        raise ValueError(
            "Tavily API key is missing."
        )

    tavily = TavilyClient(
        api_key=api_key
    )

    response = tavily.search(
        query=query,
        search_depth="advanced",
        max_results=5
    )

    results = []

    for result in response["results"]:

        title = result.get("title", "")
        url = result.get("url", "")
        content = result.get("content", "")

        if not url:
            continue

        source = create_source(
            title=title,
            url=url,
            content=content
        )

        source.quality_score = (
            calculate_source_quality(url)
        )

        results.append(source)

    results.sort(
        key=lambda source:
        source.quality_score,
        reverse=True
    )

    return results