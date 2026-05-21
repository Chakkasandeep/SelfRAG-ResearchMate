import wikipediaapi
import logging

logger = logging.getLogger("wikipedia")

# Setup Wikipedia API with modern descriptive user-agent string as required by Wikimedia policy
wiki = wikipediaapi.Wikipedia(
    user_agent="ResearchMate/1.0 (contact@researchmate.ai; Research Literature Review Assistant)",
    language="en"
)

async def get_wikipedia_context(topic: str) -> dict | None:
    """
    Fetches brief page summary from Wikipedia to establish foundation/background concepts.
    """
    try:
        page = wiki.page(topic)
        if not page.exists():
            return None
            
        return {
            "id": f"wiki-{topic.replace(' ', '_')}",
            "title": page.title,
            "authors": "Wikipedia Contributors",
            "year": 2024,
            "abstract": page.summary[:1200],  # cap summaries to avoid text bloat
            "url": page.fullurl,
            "source": "Wikipedia",
        }
    except Exception as e:
        logger.error(f"Wikipedia concept search failed for '{topic}': {e}")
        return None
