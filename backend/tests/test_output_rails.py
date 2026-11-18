import asyncio
import os

from fastapi.testclient import TestClient
import pytest

from backend.guardrails.rails import check_output


def test_fabricated_claim_blocks():
    os.environ["GUARDRAILS_ENABLED"] = "1"
    result = asyncio.run(
        check_output(
            "This is a completely eliminates hallucination result with a 94.6% guarantee.",
            [],
            [],
        )
    )
    assert result.action == "block"


def test_unsupported_claim_rewrites_or_blocks():
    os.environ["GUARDRAILS_ENABLED"] = "1"
    result = asyncio.run(check_output("This outcome is guaranteed and certainly true.", [], []))
    assert result.action in {"rewrite", "block"}


def test_clean_review_allowed():
    os.environ["GUARDRAILS_ENABLED"] = "1"
    result = asyncio.run(
        check_output(
            "The study describes one measured relationship.",
            [{"id": "paper-1"}],
            [{"id": "paper-1", "abstract": "A measured relationship was observed."}],
        )
    )
    assert result.action == "allow"


def test_blocked_export_returns_conflict(monkeypatch):
    try:
        import backend.main as main
    except ModuleNotFoundError as exc:
        pytest.skip(f"Optional backend dependency unavailable: {exc.name}")

    main._last_output_rail_status = {
        "blocked": True,
        "stage": "output",
        "reason": "Fabricated claim",
    }
    client = TestClient(main.app)
    response = client.post(
        "/api/export/pdf",
        json={"review": "blocked", "citations": []},
    )
    assert response.status_code == 409
