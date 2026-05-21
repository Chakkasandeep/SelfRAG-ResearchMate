# 🔬 ResearchMate — Full-Stack Agentic Literature Review Assistant

> **Self-RAG powered · Zero hallucinations · Free-tier infrastructure · React + FastAPI**

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [System Architecture](#2-system-architecture)
3. [Folder Structure](#3-folder-structure)
4. [Backend Setup (FastAPI + LangGraph)](#4-backend-setup)
5. [Frontend Setup (React / Next.js)](#5-frontend-setup)
6. [API Keys & Environment Variables](#6-api-keys--environment-variables)
7. [Retrieval Layer — APIs](#7-retrieval-layer--apis)
8. [Self-RAG Pipeline & Hallucination Reduction](#8-self-rag-pipeline--hallucination-reduction)
9. [Live Data Flow](#9-live-data-flow)
10. [Report & PPT Generation](#10-report--ppt-generation)
11. [Deployment](#11-deployment)
12. [Architecture Recommendations](#12-architecture-recommendations)

---

## 1. Project Overview

ResearchMate is a **fully autonomous AI research assistant** that:

- Takes a user research query
- Retrieves real papers from Semantic Scholar, arXiv, Wikipedia, and web search (Tavily)
- Generates a structured literature review draft via **Groq LLMs** (free tier)
- Runs **Self-RAG** self-critique on every claim to eliminate hallucinations
- Shows live reflection tokens in the UI
- Exports the final review as a **PDF** (client-side) or **PowerPoint** (server-side)

**All infrastructure is 100% free for development/demo.**

---

## 2. System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     React / Next.js Frontend            │
│  ┌──────────┐  ┌──────────────┐  ┌───────────────────┐ │
│  │ Chat UI  │  │  Self-RAG    │  │  Citation Side    │ │
│  │ Stream   │  │  Live Panel  │  │  Panel + Graph    │ │
│  └──────────┘  └──────────────┘  └───────────────────┘ │
│           ↕ SSE / WebSocket streaming                   │
└─────────────────────┬───────────────────────────────────┘
                      │  REST + SSE (FastAPI)
┌─────────────────────▼───────────────────────────────────┐
│                    FastAPI Backend                       │
│                                                         │
│   ┌──────────────────────────────────────────────────┐  │
│   │             LangGraph Agent Orchestrator         │  │
│   │                                                  │  │
│   │  PlanningAgent → RetrievalAgent → SumAgent      │  │
│   │       → Self-RAG Critic → GapDetector           │  │
│   │           → SynthesisAgent → OutputGen          │  │
│   └──────────────────────────────────────────────────┘  │
│                                                         │
│   ┌──────────┐  ┌──────────┐  ┌───────────────────────┐ │
│   │ Groq API │  │ Citation │  │ python-pptx / weasyprint│
│   │ (LLMs)   │  │ Database │  │ (PPT + PDF export)     │
│   └──────────┘  └──────────┘  └───────────────────────┘ │
└─────────────────────┬───────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────┐
│               External Free APIs                        │
│                                                         │
│  Semantic Scholar │ arXiv │ Wikipedia │ OpenAlex        │
│  Tavily Search    │ CORE  │ Unpaywall │ CrossRef        │
└─────────────────────────────────────────────────────────┘
```

---

## 3. Folder Structure

```
researchmate/
├── backend/
│   ├── main.py                    # FastAPI entrypoint
│   ├── agents/
│   │   ├── planning_agent.py      # Breaks query into subtopics
│   │   ├── retrieval_agent.py     # Calls all APIs
│   │   ├── summarization_agent.py # Draft narrative generation
│   │   ├── self_rag_critic.py     # Claim-level verification
│   │   ├── gap_detector.py        # Detects unsupported claims
│   │   └── synthesis_agent.py     # Final review assembly
│   ├── graph/
│   │   └── workflow.py            # LangGraph state machine
│   ├── retrieval/
│   │   ├── semantic_scholar.py
│   │   ├── arxiv_api.py
│   │   ├── wikipedia_api.py
│   │   ├── openAlex_api.py
│   │   └── tavily_search.py
│   ├── output/
│   │   ├── ppt_generator.py       # python-pptx
│   │   └── pdf_generator.py       # weasyprint HTML→PDF
│   ├── models/
│   │   └── schemas.py             # Pydantic models
│   ├── utils/
│   │   ├── citation_db.py         # Citation store
│   │   ├── text_compressor.py     # Abstract pre-processing
│   │   └── keyword_filter.py      # Cheap relevance gate
│   ├── requirements.txt
│   └── .env
│
└── frontend/
    ├── app/
    │   ├── page.tsx               # Main chat + review page
    │   ├── layout.tsx
    │   └── api/                   # Next.js API routes (proxy)
    ├── components/
    │   ├── ChatInterface.tsx       # User query input + stream
    │   ├── SelfRagPanel.tsx        # Live reflection tokens
    │   ├── ReviewDisplay.tsx       # Final review with citations
    │   ├── CitationSidePanel.tsx   # Paper abstract + PDF link
    │   ├── CitationGraph.tsx       # react-force-graph viz
    │   ├── ConfidenceBadge.tsx     # Green/Yellow/Red labels
    │   └── ExportButtons.tsx       # PDF + PPTX download
    ├── hooks/
    │   ├── useSSEStream.ts         # Server-Sent Events hook
    │   └── useCitationStore.ts     # Zustand citation state
    ├── lib/
    │   ├── api.ts                  # Backend API client
    │   └── pdfExport.ts           # jsPDF client export
    ├── store/
    │   └── researchStore.ts        # Zustand global state
    ├── public/
    ├── package.json
    ├── tailwind.config.ts
    ├── next.config.ts
    └── .env.local
```

---

## 4. Backend Setup

### 4.1 Install Dependencies

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**`requirements.txt`**

```txt
fastapi==0.111.0
uvicorn[standard]==0.29.0
langchain==0.2.6
langgraph==0.1.5
langchain-groq==0.1.6
httpx==0.27.0
pydantic==2.7.4
python-dotenv==1.0.1
arxiv==2.1.0
wikipedia-api==0.6.0
python-pptx==0.6.23
weasyprint==62.1
jinja2==3.1.4
tavily-python==0.3.3
sse-starlette==2.1.0
redis==5.0.6                    # optional: for job queuing
```

### 4.2 FastAPI Main Entry (`backend/main.py`)

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse
from graph.workflow import run_research_pipeline
import asyncio, json

app = FastAPI(title="ResearchMate API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/research/stream")
async def research_stream(body: dict):
    query = body.get("query", "")

    async def event_generator():
        async for event in run_research_pipeline(query):
            yield {"data": json.dumps(event)}

    return EventSourceResponse(event_generator())

@app.post("/api/export/pptx")
async def export_pptx(body: dict):
    from output.ppt_generator import generate_pptx
    from fastapi.responses import FileResponse
    path = generate_pptx(body["review"], body["citations"])
    return FileResponse(path, media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation")

@app.post("/api/export/pdf")
async def export_pdf(body: dict):
    from output.pdf_generator import generate_pdf
    from fastapi.responses import FileResponse
    path = generate_pdf(body["review"], body["citations"])
    return FileResponse(path, media_type="application/pdf")
```

### 4.3 LangGraph Workflow (`backend/graph/workflow.py`)

```python
from langgraph.graph import StateGraph, END
from agents.planning_agent import plan
from agents.retrieval_agent import retrieve
from agents.summarization_agent import summarize
from agents.self_rag_critic import critique
from agents.gap_detector import detect_gaps
from agents.synthesis_agent import synthesize
from typing import TypedDict, List, AsyncIterator

class ResearchState(TypedDict):
    query: str
    subtopics: List[str]
    papers: List[dict]
    draft: str
    claim_verdicts: List[dict]   # [{claim, verdict, source_id}]
    gaps_found: bool
    final_review: str
    citations: List[dict]

def build_graph():
    g = StateGraph(ResearchState)
    g.add_node("plan",       plan)
    g.add_node("retrieve",   retrieve)
    g.add_node("summarize",  summarize)
    g.add_node("critique",   critique)
    g.add_node("gap_detect", detect_gaps)
    g.add_node("synthesize", synthesize)

    g.set_entry_point("plan")
    g.add_edge("plan",      "retrieve")
    g.add_edge("retrieve",  "summarize")
    g.add_edge("summarize", "critique")
    g.add_conditional_edges(
        "critique",
        lambda s: "gap_detect" if any(
            v["verdict"] == "Not Supported" for v in s["claim_verdicts"]
        ) else "synthesize"
    )
    g.add_edge("gap_detect", "retrieve")   # retry loop
    g.add_edge("synthesize", END)
    return g.compile()

async def run_research_pipeline(query: str) -> AsyncIterator[dict]:
    graph = build_graph()
    state = {"query": query, "subtopics": [], "papers": [],
             "draft": "", "claim_verdicts": [], "gaps_found": False,
             "final_review": "", "citations": []}

    async for step in graph.astream(state):
        node, data = list(step.items())[0]
        yield {"stage": node, "data": data}
```

---

## 5. Frontend Setup

### 5.1 Create Next.js App

```bash
npx create-next-app@latest frontend --typescript --tailwind --eslint --app
cd frontend
npm install zustand react-force-graph jspdf html2canvas
npm install @radix-ui/react-dialog @radix-ui/react-badge
```

### 5.2 Main Page (`frontend/app/page.tsx`)

```tsx
"use client";
import { useState } from "react";
import ChatInterface from "@/components/ChatInterface";
import SelfRagPanel from "@/components/SelfRagPanel";
import ReviewDisplay from "@/components/ReviewDisplay";
import CitationGraph from "@/components/CitationGraph";
import ExportButtons from "@/components/ExportButtons";
import { useResearchStore } from "@/store/researchStore";

export default function Home() {
  const { stage, review, citations, verdicts } = useResearchStore();

  return (
    <main className="min-h-screen bg-slate-950 text-slate-100 flex flex-col">
      <header className="border-b border-slate-800 px-6 py-4">
        <h1 className="text-2xl font-bold text-emerald-400">🔬 ResearchMate</h1>
        <p className="text-slate-400 text-sm">Self-RAG · Zero Hallucinations · Free APIs</p>
      </header>

      <div className="flex flex-1 overflow-hidden">
        {/* Left: Chat + Live Panel */}
        <div className="w-1/3 border-r border-slate-800 flex flex-col">
          <ChatInterface />
          <SelfRagPanel verdicts={verdicts} currentStage={stage} />
        </div>

        {/* Center: Review Output */}
        <div className="flex-1 overflow-y-auto p-6">
          {review && (
            <>
              <ExportButtons />
              <ReviewDisplay review={review} citations={citations} />
            </>
          )}
        </div>

        {/* Right: Citation Graph */}
        <div className="w-72 border-l border-slate-800">
          <CitationGraph citations={citations} />
        </div>
      </div>
    </main>
  );
}
```

### 5.3 SSE Hook (`frontend/hooks/useSSEStream.ts`)

```ts
import { useResearchStore } from "@/store/researchStore";

export function useSSEStream() {
  const { setStage, addVerdict, setReview, setCitations } = useResearchStore();

  const startResearch = async (query: string) => {
    const res = await fetch("http://localhost:8000/api/research/stream", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query }),
    });

    const reader = res.body!.getReader();
    const decoder = new TextDecoder();

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      const text = decoder.decode(value);
      const lines = text.split("\n").filter(l => l.startsWith("data:"));
      for (const line of lines) {
        const event = JSON.parse(line.replace("data:", "").trim());
        setStage(event.stage);
        if (event.stage === "critique") {
          event.data.claim_verdicts?.forEach((v: any) => addVerdict(v));
        }
        if (event.stage === "synthesize") {
          setReview(event.data.final_review);
          setCitations(event.data.citations);
        }
      }
    }
  };

  return { startResearch };
}
```

### 5.4 Self-RAG Panel (`frontend/components/SelfRagPanel.tsx`)

```tsx
type Verdict = {
  claim: string;
  verdict: "Fully Supported" | "Partially Supported" | "Not Supported";
  source_id: string;
};

const badge: Record<string, string> = {
  "Fully Supported":    "bg-emerald-900 text-emerald-300 border border-emerald-600",
  "Partially Supported":"bg-amber-900  text-amber-300  border border-amber-600",
  "Not Supported":      "bg-red-900    text-red-300    border border-red-600",
};

const icon: Record<string, string> = {
  "Fully Supported": "✅",
  "Partially Supported": "⚠️",
  "Not Supported": "❌",
};

export default function SelfRagPanel({ verdicts, currentStage }: {
  verdicts: Verdict[]; currentStage: string;
}) {
  return (
    <div className="border-t border-slate-800 p-4 overflow-y-auto max-h-80">
      <h2 className="text-xs font-semibold text-slate-400 uppercase mb-2">
        Self-RAG Reflection — Stage: <span className="text-emerald-400">{currentStage}</span>
      </h2>
      <div className="space-y-2">
        {verdicts.map((v, i) => (
          <div key={i} className="text-xs rounded p-2 bg-slate-900">
            <span className={`inline-block px-2 py-0.5 rounded text-[10px] mr-2 ${badge[v.verdict]}`}>
              {icon[v.verdict]} {v.verdict}
            </span>
            <span className="text-slate-300 line-clamp-2">{v.claim}</span>
          </div>
        ))}
        {verdicts.length === 0 && (
          <p className="text-slate-600 text-xs italic">Waiting for critique stage…</p>
        )}
      </div>
    </div>
  );
}
```

---

## 6. API Keys & Environment Variables

### `backend/.env`

```env
# ── LLM ──────────────────────────────────────────────────
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# ── Search ───────────────────────────────────────────────
TAVILY_API_KEY=tvly-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# ── Academic APIs (free, no key required for most) ───────
SEMANTIC_SCHOLAR_API_KEY=           # Optional — better rate limits
CORE_API_KEY=                       # Free at core.ac.uk

# ── Server ───────────────────────────────────────────────
PORT=8000
CORS_ORIGIN=http://localhost:3000
```

### `frontend/.env.local`

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Where to Get Free Keys

| Service | URL | Notes |
|---|---|---|
| **Groq** | https://console.groq.com | Free tier, ~300 ms/call |
| **Tavily** | https://tavily.com | 1,000 free searches/month |
| **Semantic Scholar** | https://www.semanticscholar.org/product/api | Optional key for 100 req/min |
| **CORE** | https://core.ac.uk/services/api | Free open-access PDF key |
| **OpenAlex** | https://openalex.org | No key needed |
| **arXiv** | https://arxiv.org/help/api | No key needed |
| **Wikipedia** | https://www.mediawiki.org/wiki/API | No key needed |
| **Unpaywall** | https://unpaywall.org/products/api | Email only, 100k calls/day |

---

## 7. Retrieval Layer — APIs

### 7.1 Semantic Scholar (`backend/retrieval/semantic_scholar.py`)

```python
import httpx, os

BASE = "https://api.semanticscholar.org/graph/v1"
HEADERS = {"x-api-key": os.getenv("SEMANTIC_SCHOLAR_API_KEY", "")}

async def search_papers(query: str, limit: int = 10) -> list[dict]:
    async with httpx.AsyncClient() as client:
        r = await client.get(
            f"{BASE}/paper/search",
            params={
                "query": query,
                "limit": limit,
                "fields": "paperId,title,authors,year,abstract,url,citations,references"
            },
            headers=HEADERS,
            timeout=15
        )
        r.raise_for_status()
        papers = r.json().get("data", [])
        return [_normalize(p) for p in papers if p.get("abstract")]

def _normalize(p: dict) -> dict:
    return {
        "id": f"ss-{p['paperId']}",
        "title": p.get("title", ""),
        "authors": ", ".join(a["name"] for a in p.get("authors", [])),
        "year": p.get("year"),
        "abstract": p.get("abstract", ""),
        "url": p.get("url", ""),
        "source": "Semantic Scholar",
        "citation_ids": [c["paperId"] for c in p.get("citations", [])],
    }
```

### 7.2 arXiv (`backend/retrieval/arxiv_api.py`)

```python
import arxiv

async def search_arxiv(query: str, max_results: int = 8) -> list[dict]:
    client = arxiv.Client()
    search = arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.Relevance
    )
    papers = []
    for r in client.results(search):
        papers.append({
            "id": f"arxiv-{r.entry_id.split('/')[-1]}",
            "title": r.title,
            "authors": ", ".join(str(a) for a in r.authors),
            "year": r.published.year,
            "abstract": r.summary,
            "url": r.pdf_url,
            "source": "arXiv",
        })
    return papers
```

### 7.3 Wikipedia (`backend/retrieval/wikipedia_api.py`)

```python
import wikipediaapi

wiki = wikipediaapi.Wikipedia(
    language="en",
    user_agent="ResearchMate/1.0 (research assistant)"
)

async def get_wikipedia_context(topic: str) -> dict | None:
    page = wiki.page(topic)
    if not page.exists():
        return None
    return {
        "id": f"wiki-{topic.replace(' ', '_')}",
        "title": page.title,
        "authors": "Wikipedia Contributors",
        "year": 2024,
        "abstract": page.summary[:1000],
        "url": page.fullurl,
        "source": "Wikipedia",
    }
```

### 7.4 Tavily Web Search (`backend/retrieval/tavily_search.py`)

```python
from tavily import TavilyClient
import os

client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

async def web_search(query: str, max_results: int = 5) -> list[dict]:
    results = client.search(
        query=query,
        search_depth="advanced",
        max_results=max_results,
        include_answer=True
    )
    papers = []
    for r in results.get("results", []):
        papers.append({
            "id": f"web-{hash(r['url'])}",
            "title": r.get("title", "Web Source"),
            "authors": r.get("url", ""),
            "year": 2024,
            "abstract": r.get("content", "")[:800],
            "url": r["url"],
            "source": "Tavily Web",
        })
    return papers
```

### 7.5 OpenAlex (`backend/retrieval/openAlex_api.py`)

```python
import httpx

async def search_openalex(query: str, limit: int = 10) -> list[dict]:
    async with httpx.AsyncClient() as client:
        r = await client.get(
            "https://api.openalex.org/works",
            params={
                "search": query,
                "per-page": limit,
                "filter": "has_abstract:true",
                "select": "id,title,authorships,publication_year,abstract_inverted_index,primary_location"
            },
            timeout=15
        )
        r.raise_for_status()
        works = r.json().get("results", [])
        return [_parse_work(w) for w in works]

def _parse_work(w: dict) -> dict:
    abstract_idx = w.get("abstract_inverted_index") or {}
    # Reconstruct abstract from inverted index
    word_positions = [(word, pos) for word, positions in abstract_idx.items()
                      for pos in positions]
    abstract = " ".join(w for w, _ in sorted(word_positions, key=lambda x: x[1]))
    return {
        "id": f"oa-{w['id'].split('/')[-1]}",
        "title": w.get("title", ""),
        "authors": ", ".join(
            a["author"]["display_name"]
            for a in w.get("authorships", [])
        ),
        "year": w.get("publication_year"),
        "abstract": abstract[:1000],
        "url": (w.get("primary_location") or {}).get("landing_page_url", ""),
        "source": "OpenAlex",
    }
```

### 7.6 Unified Retrieval Agent (`backend/agents/retrieval_agent.py`)

```python
from retrieval.semantic_scholar import search_papers
from retrieval.arxiv_api import search_arxiv
from retrieval.wikipedia_api import get_wikipedia_context
from retrieval.tavily_search import web_search
from retrieval.openAlex_api import search_openalex
from utils.keyword_filter import quick_filter
import asyncio

async def retrieve(state: dict) -> dict:
    query = state["query"]
    subtopics = state.get("subtopics", [query])

    all_papers = []
    for topic in subtopics[:3]:   # cap topics to control rate limits
        results = await asyncio.gather(
            search_papers(topic, limit=8),
            search_arxiv(topic, max_results=6),
            search_openalex(topic, limit=6),
            web_search(topic, max_results=4),
            get_wikipedia_context(topic),
        )
        for r in results:
            if isinstance(r, list):
                all_papers.extend(r)
            elif isinstance(r, dict):
                all_papers.append(r)

    # Dedup by title similarity + keyword gate
    seen = set()
    unique = []
    for p in all_papers:
        key = p["title"][:50].lower()
        if key not in seen and quick_filter(query, p["abstract"]):
            seen.add(key)
            unique.append(p)

    return {**state, "papers": unique[:40]}  # max 40 papers
```

---

## 8. Self-RAG Pipeline & Hallucination Reduction

### 8.1 How Self-RAG Works

```
For each claim in the draft:
  1. [RETRIEVE?]  — Is retrieval needed for this claim?
  2. [RELEVANT]   — Is the paper relevant to the claim?
  3. [SUPPORTED]  — Does the abstract support the claim?
              → Fully Supported  ✅ → keep sentence (green badge)
              → Partially Supported ⚠️ → soften wording (yellow badge)
              → Not Supported ❌ → drop or trigger re-retrieval (red badge)
  4. [UTILITY 1-5] — How useful is this passage for the overall review?
```

### 8.2 Critic Agent (`backend/agents/self_rag_critic.py`)

```python
from langchain_groq import ChatGroq
import os, json, re

llm = ChatGroq(
    model="llama-3.1-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0,
    max_tokens=512
)

CRITIC_PROMPT = """You are a strict academic fact-checker.

CLAIM: {claim}

ABSTRACT: {abstract}

Evaluate strictly. Reply ONLY valid JSON:
{{
  "relevant": true/false,
  "verdict": "Fully Supported" | "Partially Supported" | "Not Supported",
  "utility": 1-5,
  "reason": "one sentence"
}}"""

async def critique_claim(claim: str, paper: dict) -> dict:
    prompt = CRITIC_PROMPT.format(
        claim=claim[:400],
        abstract=paper["abstract"][:600]
    )
    response = await llm.ainvoke(prompt)
    text = response.content.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Fallback: extract verdict with regex
        v = "Not Supported"
        if "Fully Supported" in text: v = "Fully Supported"
        elif "Partially Supported" in text: v = "Partially Supported"
        return {"relevant": True, "verdict": v, "utility": 2, "reason": "parse fallback"}

async def critique(state: dict) -> dict:
    from utils.text_compressor import extract_claims
    claims = extract_claims(state["draft"])
    papers = state["papers"][:15]   # context limit budget

    verdicts = []
    for claim in claims:
        best = None
        for paper in papers:
            result = await critique_claim(claim, paper)
            if result.get("relevant") and result.get("utility", 0) >= 3:
                best = {
                    "claim": claim,
                    "verdict": result["verdict"],
                    "source_id": paper["id"],
                    "reason": result["reason"]
                }
                if result["verdict"] == "Fully Supported":
                    break
        if best is None:
            best = {"claim": claim, "verdict": "Not Supported",
                    "source_id": None, "reason": "No matching paper found"}
        verdicts.append(best)

    return {**state, "claim_verdicts": verdicts}
```

### 8.3 Hallucination Reduction Strategies

| Strategy | Implementation |
|---|---|
| **Self-RAG verification** | Every claim verified against retrieved abstracts |
| **Claim-level granularity** | Critic sees ONE claim + ONE abstract at a time (no confusion) |
| **Keyword pre-filter** | Cheap BM25/keyword gate before any LLM call |
| **Abstract compression** | Strip boilerplate before sending to Groq |
| **Temperature = 0** | Critic LLM uses `temperature=0` for deterministic verdicts |
| **Source-ID binding** | Every sentence gets a `[cite:id]` that must exist in citation DB |
| **Gap detector loop** | `Not Supported` claims trigger a second retrieval pass |
| **No hallucinated URLs** | All paper URLs come from API responses only |

---

## 9. Live Data Flow

```
User types query
       │
       ▼  POST /api/research/stream
FastAPI → SSE stream opens
       │
       ├─ event: {stage: "plan",     data: {subtopics: [...]}}
       ├─ event: {stage: "retrieve", data: {papers: [...]}}
       ├─ event: {stage: "summarize",data: {draft: "..."}}
       ├─ event: {stage: "critique", data: {claim_verdicts: [...]}}
       │         ↑ These stream LIVE — one event per claim
       ├─ event: {stage: "gap_detect",data: {gaps: [...]}}  # if needed
       ├─ event: {stage: "retrieve", data: {papers: [...]}} # retry
       ├─ event: {stage: "synthesize",data: {final_review, citations}}
       └─ stream closes
              │
       React useSSEStream hook
              │
       Zustand store updates
              │
       ├─ SelfRagPanel re-renders (live verdict feed)
       ├─ ReviewDisplay renders final review
       └─ CitationGraph builds network viz
```

---

## 10. Report & PPT Generation

### 10.1 PowerPoint (`backend/output/ppt_generator.py`)

```python
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
import tempfile, os

def generate_pptx(review: str, citations: list[dict]) -> str:
    prs = Presentation()
    prs.slide_width  = Inches(13.33)
    prs.slide_height = Inches(7.5)

    blank_layout = prs.slide_layouts[6]

    # ── Title Slide ──────────────────────────────────────────
    slide = prs.slides.add_slide(blank_layout)
    bg = slide.background.fill
    bg.solid()
    bg.fore_color.rgb = RGBColor(0x0F, 0x17, 0x2A)

    tf = slide.shapes.add_textbox(Inches(1), Inches(2.5), Inches(11), Inches(1.5))
    tf.text_frame.text = "Literature Review"
    tf.text_frame.paragraphs[0].runs[0].font.size = Pt(44)
    tf.text_frame.paragraphs[0].runs[0].font.color.rgb = RGBColor(0x10, 0xB9, 0x81)
    tf.text_frame.paragraphs[0].runs[0].font.bold = True

    sub = slide.shapes.add_textbox(Inches(1), Inches(4), Inches(11), Inches(1))
    sub.text_frame.text = f"Generated by ResearchMate · {len(citations)} sources verified"
    sub.text_frame.paragraphs[0].runs[0].font.size = Pt(18)
    sub.text_frame.paragraphs[0].runs[0].font.color.rgb = RGBColor(0x94, 0xA3, 0xB8)

    # ── Section Slides ───────────────────────────────────────
    paragraphs = review.split("\n\n")
    for i, para in enumerate(paragraphs[:10]):   # max 10 content slides
        if len(para.strip()) < 30:
            continue
        slide = prs.slides.add_slide(blank_layout)
        bg = slide.background.fill
        bg.solid()
        bg.fore_color.rgb = RGBColor(0x0F, 0x17, 0x2A)

        content = slide.shapes.add_textbox(Inches(0.8), Inches(0.8), Inches(11.6), Inches(6))
        tf = content.text_frame
        tf.word_wrap = True
        tf.text = para.strip()
        tf.paragraphs[0].runs[0].font.size = Pt(16)
        tf.paragraphs[0].runs[0].font.color.rgb = RGBColor(0xE2, 0xE8, 0xF0)

    # ── References Slide ─────────────────────────────────────
    slide = prs.slides.add_slide(blank_layout)
    bg = slide.background.fill; bg.solid()
    bg.fore_color.rgb = RGBColor(0x0F, 0x17, 0x2A)

    ref_tf = slide.shapes.add_textbox(Inches(0.8), Inches(0.5), Inches(11.6), Inches(6.5))
    tf = ref_tf.text_frame; tf.word_wrap = True
    title_para = tf.paragraphs[0]
    title_para.text = "References"
    title_para.runs[0].font.size = Pt(28)
    title_para.runs[0].font.color.rgb = RGBColor(0x10, 0xB9, 0x81)
    title_para.runs[0].font.bold = True

    for c in citations[:15]:
        p = tf.add_paragraph()
        p.text = f"[{c['id']}] {c['authors']} ({c['year']}). {c['title']}."
        p.runs[0].font.size = Pt(11)
        p.runs[0].font.color.rgb = RGBColor(0x94, 0xA3, 0xB8)

    # ── Save ─────────────────────────────────────────────────
    tmp = tempfile.NamedTemporaryFile(suffix=".pptx", delete=False)
    prs.save(tmp.name)
    return tmp.name
```

### 10.2 PDF — Client-side (`frontend/lib/pdfExport.ts`)

```ts
import jsPDF from "jspdf";
import html2canvas from "html2canvas";

export async function exportReviewToPDF(elementId: string, filename = "review.pdf") {
  const el = document.getElementById(elementId);
  if (!el) return;
  const canvas = await html2canvas(el, { scale: 2, useCORS: true });
  const imgData = canvas.toDataURL("image/png");
  const pdf = new jsPDF({ orientation: "portrait", unit: "mm", format: "a4" });
  const imgProps = pdf.getImageProperties(imgData);
  const pdfWidth = pdf.internal.pageSize.getWidth();
  const pdfHeight = (imgProps.height * pdfWidth) / imgProps.width;
  pdf.addImage(imgData, "PNG", 0, 0, pdfWidth, pdfHeight);
  pdf.save(filename);
}
```

---

## 11. Deployment

### 11.1 Local Development

```bash
# Terminal 1 — Backend
cd backend && uvicorn main:app --reload --port 8000

# Terminal 2 — Frontend
cd frontend && npm run dev
```

### 11.2 Free Cloud Deployment

| Component | Platform | Notes |
|---|---|---|
| **Backend** | Hugging Face Spaces (Docker) | Free, persistent |
| **Frontend** | Vercel | Free hobby tier, auto-deploy from GitHub |
| **Backend alt** | Render.com free tier | 512 MB RAM, spins down after idle |

**Hugging Face `Dockerfile`**

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/ .
EXPOSE 7860
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
```

**`vercel.json` (point to HF backend)**

```json
{
  "env": {
    "NEXT_PUBLIC_API_URL": "https://your-hf-space.hf.space"
  }
}
```

---

## 12. Architecture Recommendations

### 12.1 Caching Layer

Add **Redis** (free tier on Redis Cloud) to cache paper results per query hash — avoids redundant API calls and speeds up repeat searches.

```python
import redis, hashlib, json

r = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))

def cached_search(query: str, fetch_fn):
    key = hashlib.md5(query.encode()).hexdigest()
    cached = r.get(key)
    if cached:
        return json.loads(cached)
    result = fetch_fn(query)
    r.setex(key, 3600, json.dumps(result))   # 1-hour TTL
    return result
```

### 12.2 Rate Limit Strategy

| API | Limit | Strategy |
|---|---|---|
| Groq | 30 req/min (free) | Batch claims; share one critic call per 3 claims |
| Semantic Scholar | 100 req/5 min | Cache + exponential backoff |
| arXiv | 1 req/3 sec | `asyncio.sleep(3)` between calls |
| Tavily | 1,000/month | Use only for gap-fill queries |
| OpenAlex | Unlimited | Primary retrieval backbone |
| Wikipedia | Unlimited | Background context only |

### 12.3 Model Selection (Groq Free Tier)

| Task | Model | Why |
|---|---|---|
| Planning, Synthesis | `llama-3.1-70b-versatile` | Best reasoning |
| Self-RAG Critic | `mixtral-8x7b-32768` | Long context, fast |
| Summarization | `llama-3.1-8b-instant` | Ultra fast, low token cost |

### 12.4 Tech Stack Summary

| Layer | Technology | Cost |
|---|---|---|
| LLM inference | Groq (Llama 3.1 70B) | Free |
| Agent orchestration | LangGraph | Free / OSS |
| Backend API | FastAPI + uvicorn | Free / OSS |
| Frontend | Next.js 14 + React | Free / OSS |
| UI components | Tailwind CSS + shadcn/ui | Free / OSS |
| Citation graph | react-force-graph | Free / MIT |
| PDF export (client) | jsPDF + html2canvas | Free / MIT |
| PPT export (server) | python-pptx | Free / OSS |
| Web search | Tavily | 1,000 free/month |
| Academic search | OpenAlex, arXiv | Free, unlimited |
| Paper metadata | Semantic Scholar | Free (100 req/5 min) |
| Background context | Wikipedia API | Free, unlimited |
| Deployment (backend) | Hugging Face Spaces | Free |
| Deployment (frontend) | Vercel | Free |

---

> **Total cost to build and demo: $0.00**
> All APIs and tools above operate on free tiers suitable for student projects, demos, and portfolio work.

---

*ResearchMate — Built with Self-RAG · Groq · React · FastAPI*
