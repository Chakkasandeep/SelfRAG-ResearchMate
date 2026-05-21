import os
import json
import logging
import re
from langchain_groq import ChatGroq
from utils.text_compressor import extract_claims

logger = logging.getLogger("self_rag_critic")

CRITIC_PROMPT = """You are a strict academic fact-checker.
CLAIM: {claim}
PAPER ABSTRACT: {abstract}

Evaluate strictly. Reply ONLY with a valid JSON object:
{{
  "relevant": true/false,
  "verdict": "Fully Supported" | "Partially Supported" | "Not Supported",
  "utility": 1-5,
  "reason": "one sentence explaining your judgment"
}}"""

async def critique_claim_groq(claim: str, paper: dict, api_key: str) -> dict:
    """Uses Groq Llama3 to critique a single claim against a paper abstract."""
    try:
        llm = ChatGroq(
            model="llama-3.1-8b-instant",  # active high-speed model
            api_key=api_key,
            temperature=0,
            max_tokens=256
        )
        prompt = CRITIC_PROMPT.format(
            claim=claim[:450],
            abstract=paper.get("abstract", "")[:750]
        )
        response = await llm.ainvoke(prompt)
        text = response.content.strip()
        # Clean potential LLM conversational wrapping
        text_match = re.search(r'\{.*\}', text, re.DOTALL)
        if text_match:
            text = text_match.group(0)
            
        data = json.loads(text)
        return {
            "relevant": bool(data.get("relevant", True)),
            "verdict": str(data.get("verdict", "Not Supported")),
            "utility": int(data.get("utility", 2)),
            "reason": str(data.get("reason", "Verification complete."))
        }
    except Exception as e:
        logger.warning(f"Groq claim critique failed: {e}. Defaulting to keyword check.")
        return critique_claim_local(claim, paper)

def critique_claim_local(claim: str, paper: dict) -> dict:
    """Deterministic keyword overlap critic for reliable offline execution."""
    abstract = paper.get("abstract", "").lower()
    claim_clean = claim.lower()
    
    # Strip citation tags from claim
    claim_clean = re.sub(r'\[cite:[^\]]+\]', '', claim_clean)
    
    # Clean claim words
    claim_words = set(re.findall(r'\b\w{4,}\b', claim_clean))
    abstract_words = set(re.findall(r'\b\w{4,}\b', abstract))
    
    overlap = claim_words.intersection(abstract_words)
    
    if len(overlap) >= 5:
        return {
            "relevant": True,
            "verdict": "Fully Supported",
            "utility": 5,
            "reason": f"Heavy overlap found for terms: {list(overlap)[:3]}."
        }
    elif len(overlap) >= 2:
        return {
            "relevant": True,
            "verdict": "Partially Supported",
            "utility": 3,
            "reason": f"Moderate keyword intersection with terms: {list(overlap)[:2]}."
        }
    else:
        return {
            "relevant": False,
            "verdict": "Not Supported",
            "utility": 1,
            "reason": "Insufficient semantic or lexical overlap in paper abstract."
        }

def _get_keyword_overlap(claim: str, paper: dict) -> set[str]:
    abstract = paper.get("abstract", "").lower()
    claim_clean = claim.lower()
    claim_clean = re.sub(r'\[cite:[^\]]+\]', '', claim_clean)
    claim_words = set(re.findall(r'\b\w{4,}\b', claim_clean))
    abstract_words = set(re.findall(r'\b\w{4,}\b', abstract))
    return claim_words.intersection(abstract_words)

async def critique(state: dict) -> dict:
    """
    Critic Agent node. Performs sentence-level verification against
    the abstracts of the retrieved paper database.
    Outputs a verdict list mapping claims to support status and source IDs.
    """
    draft = state.get("draft", "")
    papers = state.get("papers", [])
    
    # Segment draft into independent claim sentences
    claims = extract_claims(draft)
    
    # Map paper list by ID for immediate O(1) resolution
    papers_map = {p["id"]: p for p in papers}
    
    api_key = os.getenv("GROQ_API_KEY", "")
    use_groq = api_key and "change_this" not in api_key
    
    verdicts = []
    updated_draft = draft
    
    for claim in claims:
        # Resolve citation ID bound inside sentence (e.g. "[cite:ss-mock1]")
        cite_match = re.search(r'\[cite:([^\]]+)\]', claim)
        
        target_paper = None
        if cite_match:
            cite_id = cite_match.group(1).strip()
            target_paper = papers_map.get(cite_id)
            
        if not target_paper:
            # Sentence lacks citation tag or target paper not found in current map.
            # Let's search papers for any relevance/support!
            best_paper = None
            best_res = None
            
            # Filter and sort papers by keyword overlap
            matched_papers = []
            for paper in papers:
                overlap = _get_keyword_overlap(claim, paper)
                if len(overlap) >= 2:
                    matched_papers.append((len(overlap), paper))
            matched_papers.sort(key=lambda x: x[0], reverse=True)
            
            # Check top 3 papers with highest overlap
            for overlap_len, paper in matched_papers[:3]:
                if use_groq:
                    res = await critique_claim_groq(claim, paper, api_key)
                else:
                    res = critique_claim_local(claim, paper)
                
                if res.get("verdict") in ["Fully Supported", "Partially Supported"]:
                    best_paper = paper
                    best_res = res
                    break
            
            if best_paper and best_res:
                paper_id = best_paper["id"]
                # Auto-bind citation tag
                new_claim = claim + f" [cite:{paper_id}]"
                updated_draft = updated_draft.replace(claim, new_claim)
                
                verdicts.append({
                    "claim": new_claim,
                    "verdict": best_res.get("verdict"),
                    "source_id": paper_id,
                    "reason": best_res.get("reason") + " (Auto-resolved citation from paper abstract)"
                })
                logger.info(f"Auto-bound claim without citation tag to paper {paper_id}")
                continue
            else:
                # No paper matches or supports
                best_verdict = {
                    "claim": claim, 
                    "verdict": "Not Supported", 
                    "source_id": None, 
                    "reason": "No bound citations resolved."
                }
                verdicts.append(best_verdict)
                continue
            
        # Execute verification for already cited paper
        if use_groq:
            res = await critique_claim_groq(claim, target_paper, api_key)
        else:
            res = critique_claim_local(claim, target_paper)
            
        verdicts.append({
            "claim": claim,
            "verdict": res.get("verdict", "Not Supported"),
            "source_id": target_paper["id"],
            "reason": res.get("reason", "Lexical validation complete.")
        })
        
    logger.info(f"Self-RAG claim critique completed. Verified {len(verdicts)} claims.")
    return {**state, "draft": updated_draft, "claim_verdicts": verdicts}
