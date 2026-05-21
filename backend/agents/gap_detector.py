import logging

logger = logging.getLogger("gap_detector")

async def detect_gaps(state: dict) -> dict:
    """
    Gap Detector Agent. Inspects claim verdicts to identify claims marked as "Not Supported".
    If unsupported claims exist, flags that gaps were found and generates a search query 
    to retrieve missing references.
    """
    verdicts = state.get("claim_verdicts", [])
    query = state.get("query", "")
    
    unsupported_claims = [v for v in verdicts if v["verdict"] == "Not Supported"]
    
    if not unsupported_claims:
        logger.info("Self-RAG: All claims successfully verified. No research gaps detected.")
        return {**state, "gaps_found": False}
        
    logger.info(f"Self-RAG: Detected {len(unsupported_claims)} unsupported claims. Planning search expansion.")
    
    # Generate search terms from unsupported claim keywords
    gap_keywords = []
    for c in unsupported_claims[:2]:
        claim_text = c["claim"]
        # Extract long nouns/verbs as candidate keywords
        words = [w.strip(",.!?\"()").lower() for w in claim_text.split() if len(w) > 5]
        if words:
            gap_keywords.append(" ".join(words[:3]))
            
    # Compile expansion subtopics
    extended_subtopics = list(state.get("subtopics", []))
    for keyword in gap_keywords:
        if keyword not in extended_subtopics:
            extended_subtopics.append(keyword)
            
    # Mark gaps as found to trigger conditional LangGraph loop back to retrieval
    return {
        **state,
        "subtopics": extended_subtopics[:5],
        "gaps_found": True
    }
