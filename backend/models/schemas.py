from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class PaperSchema(BaseModel):
    id: str
    title: str
    authors: str
    year: Optional[int] = None
    abstract: str
    url: str
    source: str
    citation_ids: Optional[List[str]] = Field(default_factory=list)

class ClaimVerdictSchema(BaseModel):
    claim: str
    verdict: str  # "Fully Supported" | "Partially Supported" | "Not Supported"
    source_id: Optional[str] = None
    reason: Optional[str] = None

class ResearchStateSchema(BaseModel):
    query: str
    subtopics: List[str]
    papers: List[PaperSchema]
    draft: str
    claim_verdicts: List[ClaimVerdictSchema]
    gaps_found: bool
    final_review: str
    citations: List[PaperSchema]
