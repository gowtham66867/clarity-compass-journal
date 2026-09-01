import asyncio
from datetime import datetime, timedelta, timezone

from conftest import FakeGemini, FakeResult

import app.main as main


def test_root_and_public_config_use_neutral_brand(client):
    page = client.get("/")
    assert page.status_code == 200
    assert "Clarity Compass" in page.text
    assert "Texmed" not in page.text

    config = client.get("/api/config")
    assert config.status_code == 200
    assert config.json()["firebase"]["projectId"] == "test-project"
    assert "GEMINI_API_KEY" not in config.text


def test_security_headers_request_ids_and_api_no_store(client):
    first = client.get("/")
    second = client.get("/api/health")
    assert first.headers["x-content-type-options"] == "nosniff"
    assert first.headers["x-frame-options"] == "DENY"
    assert first.headers["strict-transport-security"].startswith("max-age=")
    assert "default-src 'self'" in first.headers["content-security-policy"]
    assert second.headers["cache-control"] == "no-store"
    assert first.headers["x-request-id"] != second.headers["x-request-id"]


def test_health_reports_required_components(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "firebase_auth": True,
        "firestore": True,
        "gemini_secret_configured": True,
    }


def test_private_routes_require_a_well_formed_valid_token(client):
    assert client.get("/api/history").status_code == 401
    assert client.get("/api/history", headers={"Authorization": "Basic x"}).status_code == 401
    assert client.get("/api/history", headers={"Authorization": "Bearer bad"}).status_code == 401
    assert client.delete("/api/history").status_code == 401


def test_clear_history_deletes_only_the_verified_users_documents(
    client, auth_a, fake_firestore
):
    fake_firestore.seed("user-a", "a-1", prompt="A")
    fake_firestore.seed("user-a", "a-2", prompt="A2")
    fake_firestore.seed("user-b", "b-1", prompt="B")

    response = client.delete("/api/history", headers=auth_a)

    assert response.status_code == 200
    assert response.json() == {"deleted": 2}
    assert fake_firestore.interactions_for("user-a") == {}
    assert set(fake_firestore.interactions_for("user-b")) == {"b-1"}


def test_me_returns_only_verified_identity_claims(client, auth_a):
    response = client.get("/api/me", headers=auth_a)
    assert response.status_code == 200
    assert response.json() == {"uid": "user-a", "email": "a@example.test", "name": "User A"}


def test_history_is_sorted_and_strictly_tenant_isolated(client, auth_a, fake_firestore):
    now = datetime.now(timezone.utc)
    fake_firestore.seed("user-a", "old", prompt="old", response="one", mode="clarity", created_at=now - timedelta(days=1))
    fake_firestore.seed("user-a", "new", prompt="new", response="two", mode="decision", created_at=now)
    fake_firestore.seed("user-b", "private", prompt="other user", response="secret", mode="clarity", created_at=now)

    response = client.get("/api/history", headers=auth_a)
    assert response.status_code == 200
    assert [item["id"] for item in response.json()] == ["new", "old"]
    assert "other user" not in response.text


def test_successful_chat_uses_verified_uid_and_records_backend(client, auth_a, fake_firestore, gemini_clients):
    developer, vertex = gemini_clients
    developer.models.outcomes = [FakeResult("List the assumptions, then choose one experiment. What will you test?")]

    response = client.post("/api/chat", headers=auth_a, json={"message": "I have two options", "mode": "decision"})

    assert response.status_code == 200
    assert response.json()["mode"] == "decision"
    saved = next(iter(fake_firestore.interactions_for("user-a").values()))
    assert "user_email" not in saved
    assert saved["gemini_backend"] == "ai-studio-developer-api"
    assert not fake_firestore.interactions_for("user-b")
    assert len(developer.models.calls) == 1
    assert len(vertex.models.calls) == 0
    instruction = developer.models.calls[0]["config"].system_instruction
    assert "trade-offs" in instruction
    assert "Do not diagnose" in instruction


def test_multiturn_context_uses_only_recent_private_history(client, auth_a, fake_firestore, gemini_clients):
    now = datetime.now(timezone.utc)
    for index in range(10):
        fake_firestore.seed(
            "user-a",
            f"a-{index}",
            prompt=f"prompt-{index}",
            response=f"response-{index}",
            mode="clarity",
            created_at=now + timedelta(minutes=index),
        )
    fake_firestore.seed("user-b", "b-1", prompt="never include", response="private", mode="clarity", created_at=now)

    response = client.post("/api/chat", headers=auth_a, json={"message": "current", "mode": "clarity"})
    assert response.status_code == 200
    contents = gemini_clients[0].models.calls[0]["contents"]
    serialized = " ".join(part.text for content in contents for part in content.parts)
    assert "prompt-0" not in serialized and "prompt-1" not in serialized
    assert "prompt-2" in serialized and "prompt-9" in serialized and "current" in serialized
    assert "never include" not in serialized


def test_quota_exhaustion_falls_back_to_vertex_and_records_it(client, auth_a, fake_firestore, monkeypatch):
    developer = FakeGemini([RuntimeError("429 RESOURCE_EXHAUSTED")])
    vertex = FakeGemini([FakeResult("Fallback response. What is the next small action?")])
    monkeypatch.setattr(main, "get_gemini", lambda: developer)
    monkeypatch.setattr(main, "get_vertex_gemini", lambda: vertex)

    response = client.post("/api/chat", headers=auth_a, json={"message": "Help", "mode": "clarity"})
    assert response.status_code == 200
    saved = next(iter(fake_firestore.interactions_for("user-a").values()))
    assert saved["gemini_backend"] == "vertex-ai-quota-fallback"
    assert len(vertex.models.calls) == 1


def test_non_quota_model_error_fails_closed_without_write(client, auth_a, fake_firestore, monkeypatch):
    developer = FakeGemini([RuntimeError("invalid request")])
    vertex = FakeGemini()
    monkeypatch.setattr(main, "get_gemini", lambda: developer)
    monkeypatch.setattr(main, "get_vertex_gemini", lambda: vertex)

    response = client.post("/api/chat", headers=auth_a, json={"message": "Help", "mode": "clarity"})
    assert response.status_code == 502
    assert not fake_firestore.interactions_for("user-a")
    assert not vertex.models.calls


def test_failed_or_empty_fallback_never_persists_partial_exchange(client, auth_a, fake_firestore, monkeypatch):
    monkeypatch.setattr(main, "get_gemini", lambda: FakeGemini([RuntimeError("429 RESOURCE_EXHAUSTED")]))
    monkeypatch.setattr(main, "get_vertex_gemini", lambda: FakeGemini([FakeResult("")]))
    response = client.post("/api/chat", headers=auth_a, json={"message": "Help", "mode": "clarity"})
    assert response.status_code == 502
    assert not fake_firestore.interactions_for("user-a")


def test_gemini_timeout_fails_closed_without_persistence(client, auth_a, fake_firestore, monkeypatch):
    async def timed_out(*_args, **_kwargs):
        raise asyncio.TimeoutError()

    monkeypatch.setattr(main, "generate_with_timeout", timed_out)
    response = client.post("/api/chat", headers=auth_a, json={"message": "Help", "mode": "clarity"})
    assert response.status_code == 502
    assert not fake_firestore.interactions_for("user-a")


def test_per_user_rate_limit_returns_retry_after(client, auth_a, fake_firestore, monkeypatch):
    limiter = main.SlidingWindowRateLimiter(limit=1, window_seconds=60, clock=lambda: 100.0)
    monkeypatch.setattr(main, "chat_limiter", limiter)
    first = client.post("/api/chat", headers=auth_a, json={"message": "First", "mode": "clarity"})
    second = client.post("/api/chat", headers=auth_a, json={"message": "Second", "mode": "clarity"})
    assert first.status_code == 200
    assert second.status_code == 429
    assert int(second.headers["retry-after"]) >= 1
    assert len(fake_firestore.interactions_for("user-a")) == 1


def test_sliding_window_releases_expired_events():
    now = [0.0]
    limiter = main.SlidingWindowRateLimiter(limit=1, window_seconds=10, clock=lambda: now[0])
    assert limiter.check("user-a") == (True, 0)
    assert limiter.check("user-a")[0] is False
    assert limiter.check("user-b") == (True, 0)
    now[0] = 11.0
    assert limiter.check("user-a") == (True, 0)


def test_chat_schema_rejects_invalid_inputs_and_identity_injection(client, auth_a):
    assert client.post("/api/chat", headers=auth_a, json={"message": "x" * 4001, "mode": "clarity"}).status_code == 422
    assert client.post("/api/chat", headers=auth_a, json={"message": "x", "mode": "unknown"}).status_code == 422
    assert client.post("/api/chat", headers=auth_a, json={"message": "x", "mode": "clarity", "uid": "user-b"}).status_code == 422
    assert client.post("/api/chat", headers=auth_a, json={"message": "   ", "mode": "clarity"}).status_code == 400
