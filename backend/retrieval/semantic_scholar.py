import httpx
import os
import logging

BASE = "https://api.semanticscholar.org/graph/v1"
logger = logging.getLogger("semantic_scholar")

async def search_papers(query: str, limit: int = 10) -> list[dict]:
    api_key = os.getenv("SEMANTIC_SCHOLAR_API_KEY", "")
    headers = {}
    if api_key:
        headers["x-api-key"] = api_key
        
    try:
        async with httpx.AsyncClient() as client:
            r = await client.get(
                f"{BASE}/paper/search",
                params={
                    "query": query,
                    "limit": limit,
                    "fields": "paperId,title,authors,year,abstract,url,citationCount,referenceCount"
                },
                headers=headers,
                timeout=12
            )
            if r.status_code != 200:
                logger.warning(f"Semantic Scholar returned status {r.status_code}")
                return []
                
            papers = r.json().get("data", [])
            results = []
            for p in papers:
                if p.get("abstract") and p.get("paperId"):
                    results.append(_normalize(p))
            return results
    except Exception as e:
        logger.error(f"Semantic Scholar retrieval failed: {e}")
        return []

def _normalize(p: dict) -> dict:
    authors_list = p.get("authors", [])
    authors_str = ", ".join(a["name"] for a in authors_list) if authors_list else "Unknown Authors"
    return {
        "id": f"ss-{p['paperId']}",
        "title": p.get("title", "Untitled Paper"),
        "authors": authors_str,
        "year": p.get("year"),
        "abstract": p.get("abstract", ""),
        "url": p.get("url", f"https://www.semanticscholar.org/paper/{p['paperId']}"),
        "source": "Semantic Scholar",
        "citation_ids": []  # populated dynamically if needed
    }
