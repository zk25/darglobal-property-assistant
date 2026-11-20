"""Tests for retrieval quality and the API (no OpenRouter key needed)."""

import os

os.environ.pop("OPENROUTER_API_KEY", None)  # exercise the retrieval-only path
os.environ["INCLUDE_SCRAPED"] = "0"  # test against the curated knowledge base so results are deterministic

import pytest
from fastapi.testclient import TestClient

from app.main import app, kb

client = TestClient(app)

# (question, a document id that should be in the top 3 results)
RETRIEVAL_CASES = [
    ("Which luxury brands has DarGlobal partnered with?", "darglobal/03-investor-relations"),
    ("Where are DarGlobal's sales offices?", "darglobal/03-investor-relations"),
    ("How many floors does Trump Tower Jeddah have?", "darglobal/project-trump-tower-jeddah"),
    ("When will The Astera by Aston Martin be completed?", "darglobal/project-the-astera-aston-martin"),
    ("Pagani residences in Dubai", "darglobal/project-da-vinci-tower-pagani"),
    ("lamborghini villas spain", "darglobal/project-spain-tierra-viva-lamborghini"),
    ("Golden visa UAE property investment amount", "darglobal/05-why-invest-residency"),
    ("Oman lifetime residency AIDA golf", "darglobal/project-aida-oman"),
    ("DarGlobal revenue and net profit HY 2026", "darglobal/press-2026-news"),
    ("Trump villas Simaisma price", "darglobal/press-2026-news"),
    ("What services does Wasalt offer?", "wasalt/01-overview"),
    ("Who owns Wasalt?", "wasalt/01-overview"),
    ("Is DarGlobal related to Wasalt?", "darglobal-wasalt-relationship"),
    ("What is the difference between DarGlobal and Wasalt?", "darglobal-wasalt-relationship"),
    ("Wasalt auction Infath licence", "wasalt/03-corporate-and-milestones"),
    ("How many users does Wasalt have?", "wasalt/04-growth-news-and-leadership"),
    ("Who is the CEO of DarGlobal?", "darglobal/02-about"),
]


@pytest.mark.parametrize("question,expected_doc", RETRIEVAL_CASES)
def test_retrieval_top3(question, expected_doc):
    top_docs = [c.doc_id for c, _ in kb.search(question, k=3)]
    assert expected_doc in top_docs, f"{question!r} -> {top_docs}"


# The suggested questions in the UI should retrieve exactly the right section first.
TOP1_CASES = [
    ("Which DarGlobal projects are in Dubai?", "projects-list"),
    ("Which luxury brands has DarGlobal partnered with?", "investor-relations"),
    ("What residency do I get if I buy property in Oman or the UAE?", "why-invest"),
    ("What services does Wasalt offer?", "wasalt/01-overview"),
    ("Tell me about Trump Tower Jeddah", "trump-tower-jeddah"),
    ("How do Wasalt property auctions work?", "wasalt/03-corporate"),
    ("What are DarGlobal's 2026 half-year results?", "press-2026-news"),
    ("How are DarGlobal and Wasalt related?", "relationship"),
    ("Who is the CEO of DarGlobal?", "history-and-listing"),
    ("Pagani residences in Dubai", "pagani"),
]


@pytest.mark.parametrize("question,expected_doc", TOP1_CASES)
def test_retrieval_top1(question, expected_doc):
    top = kb.search(question, k=1)[0][0].doc_id
    assert expected_doc in top, f"{question!r} -> {top}"


def test_every_document_has_a_source():
    for doc in kb.documents:
        assert doc.sources, f"{doc.doc_id} has no source URL"
        assert all(u.startswith("https://") for u in doc.sources)


def test_health():
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json()["knowledge_base"]["documents"] == len(kb.documents)


def test_index_page():
    r = client.get("/")
    assert r.status_code == 200 and "Property Assistant" in r.text


def test_chat_retrieval_only_mode():
    r = client.post("/api/chat", json={"message": "Tell me about Trump Tower Jeddah"})
    assert r.status_code == 200
    body = r.json()
    assert body["mode"] == "retrieval"
    assert "unavailable" not in body["answer"].lower()
    assert "Jeddah" in body["answer"]
    assert any("trump-tower-jeddah" in s["url"] for s in body["sources"])


def test_follow_up_uses_previous_question():
    history = [
        {"role": "user", "content": "Tell me about Trump Tower Jeddah"},
        {"role": "assistant", "content": "It is a 47-floor seafront tower in Jeddah."},
    ]
    r = client.post("/api/chat", json={"message": "When will it be completed?", "history": history})
    assert any("trump-tower-jeddah" in s["url"] for s in r.json()["sources"])


def test_new_topic_is_not_treated_as_follow_up():
    history = [
        {"role": "user", "content": "Where does DarGlobal have sales offices?"},
        {"role": "assistant", "content": "New York, London, Marbella, Athens, Dubai, Jeddah, Riyadh, Muscat and Doha."},
    ]
    r = client.post("/api/chat", json={"message": "What services does Wasalt offer?", "history": history})
    assert r.json()["sources"][0]["site"] == "Wasalt"


def test_bhk_and_flat_wording_finds_dubai_apartments():
    top = [c.doc_id for c, _ in kb.search("dubai 2 bhk flats", k=3)]
    assert "darglobal/project-dubai-residences" in top


def test_fallback_answer_lists_two_bedroom_projects():
    body = client.post("/api/chat", json={"message": "tell me about the dubai 2 bhk flats"}).json()
    assert "2-" in body["answer"] and "bedroom" in body["answer"]
    assert body["sources"][0]["url"].startswith("https://darglobal.co.uk/")


def test_citations_match_source_list():
    from app.main import attach_sources
    hits = kb.search("DG1 Business Bay")
    answer, sources = attach_sources("DG1 is in Business Bay [3]. It has studios [3][1].", hits)
    assert "[1]" in answer and len(sources) == 2
    assert answer.startswith("DG1 is in Business Bay [1]")


def test_stream_endpoint_falls_back_without_key():
    with client.stream("POST", "/api/chat/stream", json={"message": "What services does Wasalt offer?"}) as r:
        assert r.status_code == 200
        body = "".join(r.iter_text())
    assert "event: delta" in body and "event: done" in body
    assert "Buy" in body


def test_think_filter_strips_reasoning_split_across_chunks():
    from app.llm import ThinkFilter
    f = ThinkFilter()
    out = "".join(f.feed(p) for p in ["<thi", "nk>planning...</th", "ink>\n\nDG1 is in ", "Business Bay."]) + f.flush()
    assert out == "DG1 is in Business Bay."


def test_projects_endpoint():
    projects = client.get("/api/projects").json()["projects"]
    assert len(projects) >= 15
    required = {"id", "name", "city", "country", "lat", "lng", "type", "status", "url", "highlights"}
    for p in projects:
        assert required <= p.keys(), p["id"]
        assert p["url"].startswith("https://darglobal.co.uk/")
        assert -90 <= p["lat"] <= 90 and -180 <= p["lng"] <= 180


def test_answer_links_named_projects():
    from app.main import projects_in
    assert projects_in("**DG1** and **W Residences Downtown Dubai** both offer 2-bedroom units.") == ["dg1", "w-residences"]
    assert projects_in("Wasalt lists properties for sale and rent.") == []


def test_chat_validation():
    assert client.post("/api/chat", json={"message": ""}).status_code == 422
    assert client.post("/api/chat", json={"message": "x" * 1001}).status_code == 422


def test_unknown_question_gives_contact_details():
    r = client.post("/api/chat", json={"message": "qwertyuiop zxcvbnm"})
    assert r.status_code == 200
    assert "+971 800 40409" in r.json()["answer"]
