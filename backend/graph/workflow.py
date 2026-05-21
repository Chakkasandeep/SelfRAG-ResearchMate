from langgraph.graph import StateGraph, END
from agents.planning_agent import plan
from agents.retrieval_agent import retrieve
from agents.summarization_agent import summarize
from agents.self_rag_critic import critique
from agents.gap_detector import detect_gaps
from agents.synthesis_agent import synthesize
from typing import TypedDict, List, AsyncIterator, Dict, Any

class ResearchState(TypedDict):
    query: str
    subtopics: List[str]
    papers: List[dict]
    draft: str
    claim_verdicts: List[dict]   # [{claim, verdict, source_id}]
    gaps_found: bool
    final_review: str
    citations: List[dict]
    loop_count: int              # Counter to prevent infinite API retry loops

def build_graph():
    """Builds and compiles the Self-RAG state workflow machine."""
    g = StateGraph(ResearchState)
    
    # Register graph nodes
    g.add_node("plan",       plan)
    g.add_node("retrieve",   retrieve)
    g.add_node("summarize",  summarize)
    g.add_node("critique",   critique)
    g.add_node("gap_detect", detect_gaps)
    g.add_node("synthesize", synthesize)

    # Establish execution flows
    g.set_entry_point("plan")
    g.add_edge("plan",      "retrieve")
    g.add_edge("retrieve",  "summarize")
    g.add_edge("summarize", "critique")
    
    # Conditional edge routing: loop back to retrieve if gaps exist and loop count < 2
    def route_critic_verdict(state: ResearchState) -> str:
        # Check if we should search again or move straight to synthesis
        has_gaps = any(v["verdict"] == "Not Supported" for v in state.get("claim_verdicts", []))
        current_count = state.get("loop_count", 0)
        
        if has_gaps and current_count < 1:
            return "gap_detect"
        else:
            return "synthesize"

    g.add_conditional_edges("critique", route_critic_verdict)
    
    # Gap Detector increments loop count and retries retrieval
    def gap_to_retrieve_step(state: ResearchState) -> Dict[str, Any]:
        count = state.get("loop_count", 0)
        return {"loop_count": count + 1}
        
    g.add_node("increment_loop", lambda s: {"loop_count": s.get("loop_count", 0) + 1})
    g.add_edge("gap_detect", "increment_loop")
    g.add_edge("increment_loop", "retrieve")
    
    g.add_edge("synthesize", END)
    
    return g.compile()

async def run_research_pipeline(query: str) -> AsyncIterator[dict]:
    """
    Executes compiled state graph and yields step events live to the SSE stream.
    """
    graph = build_graph()
    state = {
        "query": query, 
        "subtopics": [], 
        "papers": [],
        "draft": "", 
        "claim_verdicts": [], 
        "gaps_found": False,
        "final_review": "", 
        "citations": [],
        "loop_count": 0
    }

    # Stream graph updates step by step
    async for step in graph.astream(state):
        node_name, node_data = list(step.items())[0]
        # Clean data keys for simplified JSON delivery
        yield {"stage": node_name, "data": node_data}
