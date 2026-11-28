"""Tests for specific bugs: cut-off streams, provider errors, greetings, rate limits, named projects."""

import asyncio
import json
import os

os.environ.pop("OPENROUTER_API_KEY", None)
os.environ["INCLUDE_SCRAPED"] = "0"

import httpx
import pytest
from fastapi.testclient import TestClient

from app import main
from app.llm import LLMError, OpenRouterClient

client = TestClient(main.app)


@pytest.fixture(autouse=True)
def clean_state():
    main._requests.clear()
    main._all_requests.clear()
    main._cache.clear()
    yield
    main._requests.clear()
    main._all_requests.clear()
    main._cache.clear()


def fake_llm(handler) -> OpenRouterClient:
    """A real client whose network calls are answered by `handler` instead of OpenRouter."""
    llm = OpenRouterClient("test-key", ["test/model:free"])
    llm._client = lambda: httpx.AsyncClient(transport=httpx.MockTransport(handler), headers=llm.headers)
    return llm


def sse_body(*events) -> bytes:
    return "".join(f"data: {e if isinstance(e, str) else json.dumps(e)}\n\n" for e in events).encode()


def delta(text, finish=None):
    return {"choices": [{"delta": {"content": text}, "finish_reason": finish}]}


def stream_chat(message):
    with client.stream("POST", "/api/chat/stream", json={"message": message}) as r:
        assert r.status_code == 200
        body = "".join(r.iter_text())
    last = body.strip().split("\n\n")[-1]
    assert last.startswith("event: done")
    return json.loads(last.split("data: ", 1)[1])


@pytest.mark.parametrize("events", [
    [delta("DG1 is in ")],                                                    # connection just ends
    [delta("DG1 is in "), {"error": {"message": "provider crashed"}}, "[DONE]"],
    [delta("DG1 is in "), {"error": "provider crashed"}],                     # error as plain text
    [delta("DG1 is in ", "length"), "[DONE]"],                                # hit the length limit
])
def test_cut_off_answer_is_marked_and_not_cached(monkeypatch, events):
    monkeypatch.setattr(main, "llm", fake_llm(lambda req: httpx.Response(200, content=sse_body(*events))))
    done = stream_chat("Where is DG1?")
    assert done["answer"].startswith("DG1 is in")
    assert main.CUT_OFF_NOTE in done["answer"]
    assert not main._cache


@pytest.mark.parametrize("events", [
    [delta("DG1 is in Business Bay."), "[DONE]"],
    [delta("DG1 is in Business Bay.", "stop")],
])
def test_complete_answer_is_cached(monkeypatch, events):
    monkeypatch.setattr(main, "llm", fake_llm(lambda req: httpx.Response(200, content=sse_body(*events))))
    done = stream_chat("Where is DG1?")
    assert done["answer"] == "DG1 is in Business Bay." and done["mode"] == "llm"
    assert len(main._cache) == 1


@pytest.mark.parametrize("error", ["quota exceeded", {"message": "quota exceeded"}])
def test_provider_error_in_either_format_falls_back(monkeypatch, error):
    def handler(request):
        if request.url.path.endswith("/models"):
            return httpx.Response(200, json={"data": []})
        return httpx.Response(200, json={"error": error})
    monkeypatch.setattr(main, "llm", fake_llm(handler))
    r = client.post("/api/chat", json={"message": "Where is DG1?"})
    assert r.status_code == 200 and r.json()["mode"] == "retrieval"
    with pytest.raises(LLMError, match="quota exceeded"):
        asyncio.run(main.llm.chat([{"role": "user", "content": "hi"}]))


@pytest.mark.parametrize("message", ["hi", "Hello!", "good morning", "thanks", "Thank you so much", "مرحبا", "السلام عليكم", "شكرا"])
def test_greetings_get_a_greeting(message):
    body = client.post("/api/chat", json={"message": message}).json()
    assert body["sources"] == [] and body["follow_ups"]
    assert "don't have information" not in body["answer"]
    assert stream_chat(message)["answer"] == body["answer"]


@pytest.mark.parametrize("message", ["Hi, which projects are in Dubai?", "Thanks. What is DG1?", "highlights of DG1"])
def test_question_with_a_greeting_is_still_answered(message):
    assert main.small_talk(message) is None


def test_arabic_without_a_model_explains_what_to_do():
    body = client.post("/api/chat", json={"message": "ما هي مشاريعكم؟"}).json()
    assert "English" in body["answer"] and "+971 800 40409" in body["answer"]


def test_named_project_comes_first():
    body = client.post("/api/chat", json={"message": "What amenities does Neptune have?"}).json()
    assert body["answer"].startswith("**Neptune")
    assert "AIDA" not in body["answer"]
    assert "[1]" in body["answer"] and "neptune" in body["sources"][0]["url"]


def test_fallback_citations_point_to_the_section_shown():
    hits = main.kb.search("What amenities does Neptune have?", k=6)
    answer, sources = main.attach_sources(main.retrieval_answer("What amenities does Neptune have?", hits), hits)
    neptune = next(c for c, _ in hits if c.heading.startswith("Neptune"))
    assert sources[0].url == neptune.url


def test_follow_up_with_it_stays_on_the_same_project():
    history = [{"role": "user", "content": "Tell me about Neptune"}, {"role": "assistant", "content": "Villas in Riyadh."}]
    body = client.post("/api/chat", json={"message": "When will it be completed?", "history": history}).json()
    assert body["answer"].startswith("**Neptune") and "December 2027" in body["answer"]


def test_faking_the_address_does_not_bypass_the_overall_limit(monkeypatch):
    monkeypatch.setattr(main, "GLOBAL_LIMIT_PER_MIN", 5)
    codes = [client.post("/api/chat", json={"message": "hi"}, headers={"X-Forwarded-For": f"10.0.0.{i}"}).status_code
             for i in range(8)]
    assert codes == [200] * 5 + [429] * 3


def test_per_visitor_limit(monkeypatch):
    monkeypatch.setattr(main, "RATE_LIMIT_PER_MIN", 2)
    codes = [client.post("/api/chat", json={"message": "hi"}).status_code for _ in range(3)]
    assert codes == [200, 200, 429]
