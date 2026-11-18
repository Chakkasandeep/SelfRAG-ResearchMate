import os
import re
import logging
from dataclasses import asdict, dataclass
from pathlib import Path
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
_GREETING_TOKENS = {"hai", "hello", "hey", "howdy", "greetings"}
_SMALLTALK_PATTERNS = (
    r"^(?:hi+|hai+|hello+|hey+|howdy|greetings)(?:\s+(?:there|how are you))?[.!?]*$",
    r"^(?:good morning|good afternoon|good evening|how are you)[.!?]*$",
    r"^(?:who are you|what are you|what can you do|what is researchmate)[?.!]*$",
)
_NEMO_INPUT_RAILS = None
logger = logging.getLogger(__name__)


def smalltalk_response(text: str) -> str | None:
    normalized = re.sub(r"\s+", " ", text.strip().lower())
    if any(re.fullmatch(pattern, normalized) for pattern in _SMALLTALK_PATTERNS):
        return (
            "Hi! I'm ResearchMate, an academic research assistant. "
            "Enter a research topic or question and I'll search sources, "
            "verify claims, and prepare a literature review."
        )
    return None


def _mask_pii(text: str) -> str:
    text = re.sub(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", "[REDACTED_EMAIL]", text, flags=re.I)
    text = re.sub(r"\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]\d{3}[-.\s]\d{4}\b", "[REDACTED_PHONE]", text)
    text = re.sub(r"\b(?:sk|tvly|gsk)[-_][A-Za-z0-9_-]{8,}\b", "[REDACTED_KEY]", text)
    return text


async def check_input(text: str, stage: str) -> RailResult:
    if _disabled():
        return RailResult("allow", "Guardrails disabled", metadata={"stage": stage})

    normalized = text.strip().lower()
    words = re.findall(r"[a-z]+", normalized)
    if not words:
        return RailResult(
            "block",
            "Please enter an academic research topic or question.",
            metadata={"stage": stage, "rule": "empty_input"},
        )

    greeting_only = len(words) <= 3 and (
        any(word in _GREETING_TOKENS for word in words)
        or any(re.fullmatch(r"hi+", word) for word in words)
    )
    if stage == "plan" and greeting_only:
        return RailResult(
            "block",
            "Please enter an academic research topic or question, not a greeting.",
            metadata={"stage": stage, "rule": "research_query_required"},
        )

    lowered = normalized
    for pattern in _INJECTION_PATTERNS:
        if re.search(pattern, lowered, flags=re.I):
            return RailResult(
                "block",
                "Prompt injection or instruction override detected.",
                metadata={"stage": stage, "rule": "self_check_input"},
            )

    api_key = os.getenv("GROQ_API_KEY", "").strip()
    if api_key and "change_this" not in api_key:
        try:
            nemo_rails = _get_nemo_input_rails()
            response = await nemo_rails.generate_async(
                messages=[
                    {
                        "role": "user",
                        "content": f"Stage: {stage}\nInput: {text}",
                    }
                ]
            )
        except Exception:
            logger.exception("NeMo input rail failed at stage %s", stage)
            return RailResult(
                "block",
                "Input safety check is unavailable; please try again.",
                metadata={"stage": stage, "rule": "nemo_input_rail_error"},
            )

        if response.get("role") == "exception":
            content = response.get("content", {})
            reason = content.get("message", "NeMo input rail blocked this input.") if isinstance(content, dict) else str(content)
            return RailResult(
                "block",
                reason,
                metadata={"stage": stage, "rule": "nemo_self_check_input"},
            )

    return RailResult("allow", "Input passed guardrails", metadata={"stage": stage})


def _get_nemo_input_rails():
    global _NEMO_INPUT_RAILS
    if _NEMO_INPUT_RAILS is None:
        os.environ["NEMOGUARDRAILS_LLM_FRAMEWORK"] = "langchain"
        from langchain_groq import ChatGroq
        from nemoguardrails import LLMRails, RailsConfig

        config_path = Path(__file__).parent / "input"
        config = RailsConfig.from_path(str(config_path))
        llm = ChatGroq(
            model="openai/gpt-oss-20b",
            api_key=os.getenv("GROQ_API_KEY"),
            temperature=0,
            max_tokens=128,
        )
        _NEMO_INPUT_RAILS = LLMRails(config, llm=llm)
    return _NEMO_INPUT_RAILS


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
