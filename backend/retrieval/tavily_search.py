import os
import logging
from tavily import TavilyClient

logger = logging.getLogger("tavily_search")

async def web_search(query: str, max_results: int = 5) -> list[dict]:
    """
    Search general web sources using Tavily Search API.
    Bypasses and logs warning if API key is not configured.
    """
    api_key = os.getenv("TAVILY_API_KEY", "")
    if not api_key or "change_this" in api_key:
        logger.warning("Tavily API key not configured. Skipping Tavily web search.")
        return []
        
    try:
        logger.info(f"Initiating Tavily web search for query: '{query}'")
        # Standard synchronous client execution
        client = TavilyClient(api_key=api_key)
        results = client.search(
            query=query,
            search_depth="advanced",
            max_results=max_results,
            include_answer=True
        )
        
        papers = []
        for r in results.get("results", []):
            url = r.get("url", "")
            url_hash = str(abs(hash(url)))
            papers.append({
                "id": f"web-{url_hash}",
                "title": r.get("title", "Web Source Document"),
                "authors": url,  # For web sources, use URL domain/string as author attribution
                "year": 2024,
                "abstract": r.get("content", "")[:900],
                "url": url,
                "source": "Tavily Web",
            })
        return papers
    except Exception as e:
        logger.error(f"Tavily search retrieval failed: {e}")
        return []
