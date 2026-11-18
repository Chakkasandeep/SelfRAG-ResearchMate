import os
import re

from utils.keyword_filter import quick_filter
from .rails import RailResult


TRUSTED_SOURCES = {"arxiv", "semantic_scholar", "semantic scholar", "openalex"}
MEDIUM_SOURCES = {"wikipedia"}
STRICT_SOURCES = {"tavily", "tavily web"}


def _disabled() -> bool:
    return os.getenv("GUARDRAILS_ENABLED", "1").strip().lower() in {"0", "false", "off", "no"}


def _source_key(source: str) -> str:
    return (source or "").strip().lower().replace("-", "_")


def _doi(item: dict) -> str:
    return str(item.get("doi") or item.get("DOI") or "").strip().lower()


def filter_one(item: dict, source: str, query: str) -> RailResult:
    if _disabled():
        return RailResult("allow", "Guardrails disabled", metadata={"source": source})
    if not isinstance(item, dict):
        return RailResult(
            "block",
            "missing_metadata",
            metadata={"source": source, "title": ""},
        )

    title = str(item.get("title") or "").strip()
    if not title:
        return RailResult(
            "block",
            "no_title",
            metadata={"source": source, "title": ""},
        )

    abstract = str(item.get("abstract") or "").strip()
    if not abstract:
        return RailResult(
            "block",
            "missing_metadata",
            metadata={"source": source, "title": title},
        )

    source_key = _source_key(source)
    searchable = f"{title} {abstract}"
    relevant = quick_filter(query, searchable)

    if source_key in STRICT_SOURCES and not relevant:
        return RailResult(
            "block",
            "low_relevance",
            metadata={"source": source, "title": title},
        )

    if source_key not in TRUSTED_SOURCES | MEDIUM_SOURCES | STRICT_SOURCES:
        if not relevant:
            return RailResult(
                "block",
                "untrusted_source",
                metadata={"source": source, "title": title},
            )

    if not relevant and source_key in MEDIUM_SOURCES:
        return RailResult(
            "block",
            "low_relevance",
            metadata={"source": source, "title": title},
        )

    if not item.get("year"):
        return RailResult(
            "allow",
            "missing metadata: year optional; item downranked",
            metadata={"source": source, "title": title, "downranked": True},
        )

    return RailResult(
        "allow",
        "Retrieval item passed guardrails",
        metadata={"source": source, "title": title},
    )


def filter_batch(
    items: list[dict], source: str, query: str
) -> tuple[list[dict], list[dict]]:
    kept: list[dict] = []
    rejected: list[dict] = []
    seen_dois: set[str] = set()
    seen_titles: set[str] = set()

    for item in items:
        if not isinstance(item, dict):
            rejected.append(
                {
                    "source": source,
                    "reason": "missing_metadata",
                    "title": "",
                }
            )
            continue

        doi = _doi(item)
        title_signature = str(item.get("title") or "").lower()[:55].strip()
        if doi and doi in seen_dois:
            rejected.append(
                {
                    "source": source,
                    "reason": "duplicate_doi",
                    "title": item.get("title", ""),
                }
            )
            continue
        if title_signature and title_signature in seen_titles:
            rejected.append(
                {
                    "source": source,
                    "reason": "duplicate_title",
                    "title": item.get("title", ""),
                }
            )
            continue

        result = filter_one(item, source, query)
        if result.action == "allow":
            kept.append(item)
            if doi:
                seen_dois.add(doi)
            if title_signature:
                seen_titles.add(title_signature)
        else:
            rejected.append(
                {
                    "source": source,
                    "reason": result.reason,
                    "title": item.get("title", ""),
                }
            )

    return kept, rejected
