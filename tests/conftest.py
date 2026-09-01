import os
from dataclasses import dataclass
from datetime import datetime, timezone

import pytest


os.environ.setdefault("GOOGLE_CLOUD_PROJECT", "test-project")
os.environ.setdefault("FIREBASE_API_KEY", "test-public-firebase-key")
os.environ.setdefault("FIREBASE_APP_ID", "test-app-id")
os.environ.setdefault("FIREBASE_MESSAGING_SENDER_ID", "123456")
os.environ.setdefault("GEMINI_API_KEY", "test-secret-present")

from fastapi.testclient import TestClient

import app.main as main


@dataclass
class FakeSnapshot:
    id: str
    payload: dict

    def to_dict(self):
        return dict(self.payload)


class FakeDocument:
    def __init__(self, database, path):
        self.database = database
        self.path = path
        self.id = path[-1]

    def collection(self, name):
        return FakeCollection(self.database, self.path + (name,))

    def set(self, payload):
        self.database.records[self.path] = dict(payload)

    def delete(self):
        self.database.records.pop(self.path, None)


class FakeQuery:
    def __init__(self, database, path, descending=False, limit_value=None):
        self.database = database
        self.path = path
        self.descending = descending
        self.limit_value = limit_value

    def order_by(self, _field, direction=None):
        descending = str(direction).upper().endswith("DESCENDING")
        return FakeQuery(self.database, self.path, descending, self.limit_value)

    def limit(self, value):
        return FakeQuery(self.database, self.path, self.descending, value)

    def stream(self):
        rows = [
            FakeSnapshot(path[-1], payload)
            for path, payload in self.database.records.items()
            if path[:-1] == self.path
        ]
        rows.sort(
            key=lambda item: item.payload.get("created_at", datetime.min.replace(tzinfo=timezone.utc)),
            reverse=self.descending,
        )
        return rows[: self.limit_value] if self.limit_value is not None else rows


class FakeCollection(FakeQuery):
    def document(self, document_id=None):
        if document_id is None:
            self.database.sequence += 1
            document_id = f"generated-{self.database.sequence}"
        return FakeDocument(self.database, self.path + (document_id,))


class FakeFirestore:
    def __init__(self):
        self.records = {}
        self.sequence = 0

    def collection(self, name):
        return FakeCollection(self, (name,))

    def seed(self, uid, document_id, **payload):
        self.records[("users", uid, "interactions", document_id)] = payload

    def interactions_for(self, uid):
        return {
            path[-1]: payload
            for path, payload in self.records.items()
            if path[:-1] == ("users", uid, "interactions")
        }


class FakeResult:
    def __init__(self, text):
        self.text = text


class FakeModels:
    def __init__(self, outcomes=None):
        self.outcomes = list(outcomes or [FakeResult("A useful response. What is your next step?")])
        self.calls = []

    def generate_content(self, **kwargs):
        self.calls.append(kwargs)
        outcome = self.outcomes.pop(0)
        if isinstance(outcome, Exception):
            raise outcome
        return outcome


class FakeGemini:
    def __init__(self, outcomes=None):
        self.models = FakeModels(outcomes)


@pytest.fixture
def fake_firestore(monkeypatch):
    database = FakeFirestore()
    monkeypatch.setattr(main, "get_db", lambda: database)
    return database


@pytest.fixture
def gemini_clients(monkeypatch):
    developer = FakeGemini()
    vertex = FakeGemini()
    monkeypatch.setattr(main, "get_gemini", lambda: developer)
    monkeypatch.setattr(main, "get_vertex_gemini", lambda: vertex)
    return developer, vertex


@pytest.fixture(autouse=True)
def fake_firebase(monkeypatch):
    identities = {
        "token-a": {"uid": "user-a", "email": "a@example.test", "name": "User A"},
        "token-b": {"uid": "user-b", "email": "b@example.test", "name": "User B"},
    }

    def verify_id_token(token, check_revoked=False):
        assert check_revoked is True
        if token not in identities:
            raise ValueError("invalid token")
        return identities[token]

    monkeypatch.setattr(main.auth, "verify_id_token", verify_id_token)


@pytest.fixture
def client(fake_firestore, gemini_clients):
    return TestClient(main.app)


@pytest.fixture
def auth_a():
    return {"Authorization": "Bearer token-a"}


@pytest.fixture
def auth_b():
    return {"Authorization": "Bearer token-b"}
