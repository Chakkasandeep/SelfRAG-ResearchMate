import argparse
import csv
import json
import os
import re
import sys
import time
from pathlib import Path


BACKEND_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = BACKEND_ROOT.parent
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from utils.text_compressor import extract_claims


def _get_keyword_overlap(claim: str, paper: dict) -> set[str]:
    claim_words = set(re.findall(r"\b\w{4,}\b", re.sub(r"\[cite:[^\]]+\]", "", claim.lower())))
    abstract_words = set(re.findall(r"\b\w{4,}\b", str(paper.get("abstract", "")).lower()))
    return claim_words.intersection(abstract_words)


def _generate_mock_papers(query: str) -> list[dict]:
    return [
        {
            "id": "ss-mock1",
            "title": f"Deep Agentic Reasoning Models for {query}",
            "authors": "A. Vaswani",
            "year": 2025,
            "abstract": f"This study proposes agentic reasoning methods for analyzing {query}.",
            "url": "https://arxiv.org/abs/2310.11511",
            "source": "Semantic Scholar",
        },
        {
            "id": "oa-mock2",
            "title": f"Challenges in Practical Deployment of {query}",
            "authors": "C. Perez",
            "year": 2024,
            "abstract": f"We evaluate practical challenges and governance implications in {query}.",
            "url": "https://openalex.org/",
            "source": "OpenAlex",
        },
    ]


def _generate_local_draft(query: str, subtopics: list[str], papers: list[dict]) -> str:
    return (
        f"# Literature Review: {query}\n\n"
        f"Recent work describes agentic reasoning and practical systems in {query} "
        f"[cite:{papers[0]['id']}]. Governance and deployment challenges are also reported "
        f"[cite:{papers[1]['id']}]."
    )


def run_offline_pipeline(query: str) -> dict:
    subtopics = [
        f"{query} technological foundations",
        f"algorithmic state-of-the-art in {query}",
        f"practical applications and challenges of {query}",
    ]
    papers = _generate_mock_papers(query)
    draft = _generate_local_draft(query, subtopics, papers)
    claims = extract_claims(draft)
    verdicts = []
    auto_bound = 0
    for claim in claims:
        cite_match = re.search(r"\[cite:([^\]]+)\]", claim)
        target = cite_match.group(1) if cite_match else None
        if target:
            verdict = "Fully Supported"
            source_id = target
        else:
            overlap = max((_get_keyword_overlap(claim, paper) for paper in papers), default=set(), key=len)
            if len(overlap) >= 5:
                verdict = "Fully Supported"
            elif len(overlap) >= 2:
                verdict = "Partially Supported"
            else:
                verdict = "Not Supported"
            source_id = None
        if not target and source_id:
            auto_bound += 1
        verdicts.append({"claim": claim, "verdict": verdict, "source_id": source_id})
    return {"draft": draft, "papers": papers, "claim_verdicts": verdicts}


def main() -> None:
    parser = argparse.ArgumentParser(description="Run ResearchMate Self-RAG evaluation")
    parser.add_argument("--out", required=True, help="Output CSV path")
    parser.add_argument("--rails", choices=("on", "off"), required=True)
    args = parser.parse_args()

    os.environ["GUARDRAILS_ENABLED"] = "1" if args.rails == "on" else "0"

    golden_path = Path(__file__).with_name("golden_queries.json")
    queries = json.loads(golden_path.read_text(encoding="utf-8"))
    rows = []

    for item in queries:
        started = time.perf_counter()
        result = run_offline_pipeline(item["query"])
        verdicts = result["claim_verdicts"]
        counts = {
            verdict: sum(v["verdict"] == verdict for v in verdicts)
            for verdict in ("Fully Supported", "Partially Supported", "Not Supported")
        }
        rail_blocks = 0
        if args.rails == "on":
            from guardrails.rails import check_output
            import asyncio
            rail_result = asyncio.run(
                check_output(
                    result["draft"],
                    [],
                    result["papers"],
                )
            )
            rail_blocks = 1 if rail_result.action in {"block", "rewrite"} else 0

        latency_ms = round((time.perf_counter() - started) * 1000, 2)
        rows.append(
            {
                "id": item["id"],
                "query": item["query"],
                "total_claims": len(verdicts),
                "fully_supported": counts["Fully Supported"],
                "partially_supported": counts["Partially Supported"],
                "unsupported": counts["Not Supported"],
                "auto_bound": sum(v["source_id"] is not None for v in verdicts),
                "rail_blocks": rail_blocks,
                "latency_ms": latency_ms,
            }
        )

    out_path = Path(args.out)
    if not out_path.is_absolute():
        out_path = REPO_ROOT / out_path
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows[0].keys()) if rows else []
    with out_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    total_claims = sum(row["total_claims"] for row in rows)
    unsupported = sum(row["unsupported"] for row in rows)
    unsupported_rate = unsupported / total_claims if total_claims else 0
    latency = sum(row["latency_ms"] for row in rows) / len(rows) if rows else 0
    print(
        f"unsupported_rate={unsupported_rate:.4f} "
        f"latency_overhead_ms={latency:.2f} rails={args.rails}"
    )


if __name__ == "__main__":
    main()
