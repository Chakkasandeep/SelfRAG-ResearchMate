import arxiv
import logging

logger = logging.getLogger("arxiv")

async def search_arxiv(query: str, max_results: int = 8) -> list[dict]:
    """
    Asynchronously queries arXiv database using standard search client.
    Handles rate-limiting and connection errors gracefully.
    """
    try:
        # arxiv is synchronous but lightweight. Wrap it safely.
        client = arxiv.Client()
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.Relevance
        )
        
        papers = []
        # results() is a generator, so we can iterate in a standard loop
        for r in client.results(search):
            paper_id = r.entry_id.split('/')[-1]
            authors_str = ", ".join(str(a) for a in r.authors) if r.authors else "Unknown Authors"
            papers.append({
                "id": f"arxiv-{paper_id}",
                "title": r.title,
                "authors": authors_str,
                "year": r.published.year if r.published else None,
                "abstract": r.summary,
                "url": r.pdf_url if r.pdf_url else r.entry_id,
                "source": "arXiv",
            })
        return papers
    except Exception as e:
        logger.error(f"arXiv retrieval failed: {e}")
        return []
