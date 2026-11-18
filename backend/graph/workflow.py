from langgraph.graph import StateGraph, END
from agents.planning_agent import plan
from agents.retrieval_agent import retrieve
from agents.summarization_agent import summarize
from agents.self_rag_critic import critique
from agents.gap_detector import detect_gaps
from agents.synthesis_agent import synthesize
from typing import TypedDict, List, AsyncIterator, Dict, Any
from guardrails.rails import check_output, smalltalk_response

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
    retrieval_rejections: List[dict]
    pipeline_blocked: dict | None
    last_rail_status: dict | None

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
    def route_plan(state: ResearchState) -> str:
        return END if state.get("pipeline_blocked") else "retrieve"

    def route_summarize(state: ResearchState) -> str:
        return END if state.get("pipeline_blocked") else "critique"

    g.add_conditional_edges("plan", route_plan)
    g.add_edge("retrieve", "summarize")
    g.add_conditional_edges("summarize", route_summarize)
    
    # Conditional edge routing: loop back to retrieve if gaps exist and loop count < 2
    def route_critic_verdict(state: ResearchState) -> str:
        if state.get("pipeline_blocked"):
            return END
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
    reply = smalltalk_response(query)
    if reply:
        yield {
            "stage": "smalltalk",
            "data": {"type": "smalltalk", "message": reply},
        }
        return

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
        "loop_count": 0,
        "retrieval_rejections": [],
        "pipeline_blocked": None,
        "last_rail_status": None,
    }

    # Stream graph updates step by step
    pipeline_blocked = None
    async for step in graph.astream(state):
        node_name, node_data = list(step.items())[0]
        if node_data.get("pipeline_blocked"):
            pipeline_blocked = node_data["pipeline_blocked"]
        if node_name == "synthesize":
            final_review = node_data.get("final_review", "")
            citations = node_data.get("citations", [])
            papers = node_data.get("papers", [])
            rail_result = await check_output(final_review, citations, papers)

            if rail_result.action == "block":
                final_review = f"This review was withheld by output guardrails: {rail_result.reason}"
                citations = []
                node_data["final_review"] = final_review
                node_data["citations"] = citations
                node_data["rail_blocked"] = {
                    "stage": "output",
                    "reason": rail_result.reason,
                }
                node_data["last_rail_status"] = {
                    "blocked": True,
                    "stage": "output",
                    "reason": rail_result.reason,
                }
            elif rail_result.action == "rewrite":
                final_review = rail_result.output or final_review
                node_data["final_review"] = final_review
                node_data["rail_rewritten"] = {
                    "stage": "output",
                    "reason": rail_result.reason,
                }
                node_data["last_rail_status"] = {
                    "blocked": False,
                    "rewritten": True,
                    "stage": "output",
                    "reason": rail_result.reason,
                }
            else:
                node_data["last_rail_status"] = {
                    "blocked": False,
                    "rewritten": False,
                    "stage": "output",
                    "reason": rail_result.reason,
                }
        # Clean data keys for simplified JSON delivery
        yield {"stage": node_name, "data": node_data}

    if pipeline_blocked:
        blocked_stage = pipeline_blocked["stage"]
        blocked_reason = pipeline_blocked["reason"]
        if "unavailable" in blocked_reason.lower():
            blocked_message = "The input safety check is unavailable right now. Please try again shortly."
        elif blocked_stage == "plan":
            blocked_message = "That request couldn't pass the input check. Please try a clear academic research topic or question."
        else:
            blocked_message = "I couldn't continue because the input did not pass the safety check. Please revise it and try again."
        yield {
            "stage": "pipeline_blocked",
            "data": {
                "type": "pipeline_blocked",
                "stage": blocked_stage,
                "reason": blocked_reason,
                "message": blocked_message,
            },
        }
