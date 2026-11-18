from backend.guardrails.retrieval_guard import filter_batch


def test_low_relevance_tavily_rejected():
    kept, rejected = filter_batch(
        [{"title": "Weather report", "abstract": "Rain and wind", "year": 2024}],
        "Tavily Web",
        "quantum annealing cryptography",
    )
    assert kept == []
    assert rejected[0]["reason"] == "low_relevance"


def test_duplicate_doi_one_kept_one_rejected():
    kept, rejected = filter_batch(
        [
            {"title": "Quantum Study", "abstract": "quantum annealing algorithms", "doi": "10/test", "year": 2024},
            {"title": "Another Quantum Study", "abstract": "quantum annealing algorithms", "doi": "10/test", "year": 2024},
        ],
        "arXiv",
        "quantum annealing",
    )
    assert len(kept) == 1
    assert rejected[0]["reason"] == "duplicate_doi"


def test_arxiv_query_keyword_accepted():
    kept, rejected = filter_batch(
        [{"title": "Quantum Annealing", "abstract": "Quantum annealing for cryptography", "year": 2024}],
        "arXiv",
        "quantum annealing",
    )
    assert len(kept) == 1
    assert rejected == []


def test_rejection_records_source_and_reason():
    _, rejected = filter_batch(
        [{"title": "", "abstract": "unrelated", "year": 2024}],
        "Tavily Web",
        "climate",
    )
    assert rejected[0]["source"] == "Tavily Web"
    assert rejected[0]["reason"] == "no_title"
