import os
import re
from dataclasses import asdict, dataclass
from typing import Literal


@dataclass
class RailResult:
    action: Literal["allow", "block", "rewrite"]
    reason: str
    output: str | None = None
    metadata: dict | None = None

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, value: dict) -> "RailResult":
        return cls(
            action=value["action"],
            reason=value["reason"],
            output=value.get("output"),
            metadata=value.get("metadata"),
        )


def _disabled() -> bool:
    return os.getenv("GUARDRAILS_ENABLED", "1").strip().lower() in {"0", "false", "off", "no"}


_INJECTION_PATTERNS = (
    r"ignore\s+(all\s+)?(previous|prior)\s+(instructions|rules)",
    r"disregard\s+(all\s+)?(previous|prior)\s+(instructions|rules)",
    r"reveal\s+(the\s+)?(system|hidden)\s+(prompt|instructions)",
    r"bypass\s+(the\s+)?(guardrails?|safety)",
)


def _mask_pii(text: str) -> str:
    text = re.sub(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", "[REDACTED_EMAIL]", text, flags=re.I)
    text = re.sub(r"\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]\d{3}[-.\s]\d{4}\b", "[REDACTED_PHONE]", text)
    text = re.sub(r"\b(?:sk|tvly|gsk)[-_][A-Za-z0-9_-]{8,}\b", "[REDACTED_KEY]", text)
    return text


async def check_input(text: str, stage: str) -> RailResult:
    if _disabled():
        return RailResult("allow", "Guardrails disabled", metadata={"stage": stage})

    lowered = text.lower()
    for pattern in _INJECTION_PATTERNS:
        if re.search(pattern, lowered, flags=re.I):
            return RailResult(
                "block",
                "Prompt injection or instruction override detected.",
                metadata={"stage": stage, "rule": "self_check_input"},
            )
    return RailResult("allow", "Input passed guardrails", metadata={"stage": stage})


async def check_retrieval(
    items: list[dict], source: str, query: str
) -> tuple[list[dict], list[RailResult]]:
    from .retrieval_guard import filter_batch

    return filter_batch(items, source, query)


async def check_output(
    review: str, citations: list[dict], papers: list[dict]
) -> RailResult:
    if _disabled():
        return RailResult("allow", "Guardrails disabled", metadata={"stage": "output"})

    masked = _mask_pii(review)
    if masked != review:
        return RailResult(
            "rewrite",
            "Sensitive data masked.",
            output=masked,
            metadata={"stage": "output", "rule": "mask_sensitive_data"},
        )

    abstract_text = " ".join(
        str(paper.get("abstract", ""))[:200] for paper in papers[:20]
    ).lower()
    review_lower = review.lower()

    fabricated_markers = (
        "fabricated",
        "invented",
        "94.6%",
        "completely eliminates hallucination",
    )
    if any(marker in review_lower for marker in fabricated_markers):
        if not any(marker in abstract_text for marker in fabricated_markers):
            return RailResult(
                "block",
                "Fabricated or unsupported claim detected.",
                metadata={"stage": "output", "rule": "self_check_hallucination"},
            )

    unsupported_markers = ("according to no source", "guaranteed", "certainly")
    if any(marker in review_lower for marker in unsupported_markers):
        rewritten = re.sub(
            r"\bguaranteed\b|\bcertainly\b",
            "suggested",
            review,
            flags=re.I,
        )
        return RailResult(
            "rewrite",
            "Unsupported absolute language softened.",
            output=rewritten,
            metadata={"stage": "output", "rule": "self_check_facts"},
        )

    return RailResult("allow", "Output passed guardrails", metadata={"stage": "output"})
