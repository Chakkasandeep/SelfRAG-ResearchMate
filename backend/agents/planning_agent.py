import os
import json
import logging
from langchain_groq import ChatGroq

logger = logging.getLogger("planning_agent")

async def plan(state: dict) -> dict:
    """
    Planning Agent node. Parses user research query and breaks it down 
    into a structured list of 3-4 subtopics.
    Supports smart fallback to a high-quality local template if Groq is unavailable.
    """
    query = state.get("query", "")
    
    api_key = os.getenv("GROQ_API_KEY", "")
    # Check for empty or default placeholder keys
    if not api_key or "change_this" in api_key:
        logger.info("Groq API key not configured. Generating high-quality local research plan.")
        subtopics = _generate_local_plan(query)
        return {**state, "subtopics": subtopics}
        
    try:
        llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            api_key=api_key,
            temperature=0.2,
            max_tokens=256
        )
        
        prompt = f"""You are a senior academic research planner.
Analyze the following literature review query:
"{query}"

Break this query down into exactly 3 to 4 distinct, scientific, and search-optimized subtopics or keywords.
Reply ONLY with a valid JSON array of strings. No conversational preamble. No extra characters.
Example response:
["subtopic1", "subtopic2", "subtopic3"]"""

        response = await llm.ainvoke(prompt)
        text = response.content.strip()
        
        # Try to parse JSON array
        subtopics = json.loads(text)
        if isinstance(subtopics, list) and len(subtopics) > 0:
            logger.info(f"Generated research subtopics via Groq: {subtopics}")
            return {**state, "subtopics": [str(s) for s in subtopics]}
            
        raise ValueError("Response was not a valid list of subtopics")
    except Exception as e:
        logger.warning(f"Groq planning call failed or parsed incorrectly: {e}. Utilizing fallback local plan.")
        subtopics = _generate_local_plan(query)
        return {**state, "subtopics": subtopics}

def _generate_local_plan(query: str) -> list[str]:
    """Generates highly realistic subtopics optimized for academic searches based on the input query."""
    clean_q = query.strip()
    return [
        f"{clean_q} technological foundations",
        f"algorithmic state-of-the-art in {clean_q}",
        f"practical applications and clinical challenges of {clean_q}",
        f"ethical socio-technical implications and future trends in {clean_q}"
    ]
