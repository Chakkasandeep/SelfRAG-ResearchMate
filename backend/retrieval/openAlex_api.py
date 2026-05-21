import httpx
import logging

logger = logging.getLogger("openalex")

async def search_openalex(query: str, limit: int = 10) -> list[dict]:
    """
    Search papers using OpenAlex catalog REST endpoints.
    Reconstructs abstracts from OpenAlex inverted index layout.
    """
    try:
        async with httpx.AsyncClient() as client:
            r = await client.get(
                "https://api.openalex.org/works",
                params={
                    "search": query,
                    "per-page": limit,
                    "filter": "has_abstract:true",
                    "select": "id,title,authorships,publication_year,abstract_inverted_index,primary_location"
                },
                timeout=12
            )
            if r.status_code != 200:
                logger.warning(f"OpenAlex returned status {r.status_code}")
                return []
                
            works = r.json().get("results", [])
            papers = []
            for w in works:
                parsed = _parse_work(w)
                if parsed:
                    papers.append(parsed)
            return papers
    except Exception as e:
        logger.error(f"OpenAlex paper search failed: {e}")
        return []

def _parse_work(w: dict) -> dict | None:
    abstract_idx = w.get("abstract_inverted_index")
    if not abstract_idx:
        return None
        
    try:
        # OpenAlex represents abstracts as {"word": [list_of_positions]}
        # We reconstruct it by sorting words by positions
        word_positions = []
        for word, positions in abstract_idx.items():
            for pos in positions:
                word_positions.append((word, pos))
                
        # Sort by position (index 1 of the tuple)
        word_positions.sort(key=lambda x: x[1])
        abstract = " ".join(word for word, _ in word_positions)
        
        # Parse authors
        authorships = w.get("authorships", [])
        authors_list = []
        for auth in authorships:
            disp = auth.get("author", {}).get("display_name")
            if disp:
                authors_list.append(disp)
        authors_str = ", ".join(authors_list) if authors_list else "Unknown Authors"
        
        # Parse landing URL
        primary_loc = w.get("primary_location") or {}
        url = primary_loc.get("landing_page_url") or primary_loc.get("pdf_url") or f"https://openalex.org/{w['id'].split('/')[-1]}"
        
        return {
            "id": f"oa-{w['id'].split('/')[-1]}",
            "title": w.get("title", "Untitled Work"),
            "authors": authors_str,
            "year": w.get("publication_year"),
            "abstract": abstract[:1200],
            "url": url,
            "source": "OpenAlex",
        }
    except Exception as e:
        logger.error(f"Failed parsing OpenAlex work: {e}")
        return None
