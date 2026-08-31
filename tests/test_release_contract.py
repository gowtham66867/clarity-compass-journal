import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TRACKED_TEXT = [
    ROOT / "README.md",
    ROOT / "SUBMISSION.md",
    ROOT / "app/main.py",
    ROOT / "app/static/index.html",
    ROOT / "app/static/app.js",
    ROOT / "firestore.rules",
]


def test_no_previous_work_brand_remains_in_submission_assets():
    combined = "\n".join(path.read_text(encoding="utf-8") for path in TRACKED_TEXT)
    assert "texmed" not in combined.casefold()


def test_repository_contains_no_obvious_private_key_or_google_api_key():
    combined = "\n".join(path.read_text(encoding="utf-8") for path in TRACKED_TEXT)
    assert "-----BEGIN PRIVATE KEY-----" not in combined
    assert re.search(r"AIza[0-9A-Za-z_-]{30,}", combined) is None


def test_firestore_rules_are_owner_bound_and_deny_everything_else():
    rules = (ROOT / "firestore.rules").read_text(encoding="utf-8")
    assert "request.auth.uid == userId" in rules
    assert "match /{document=**}" in rules
    assert "allow read, write: if false" in rules


def test_model_output_is_rendered_as_text_not_html():
    frontend = (ROOT / "app/static/app.js").read_text(encoding="utf-8")
    assert "content.textContent = text" in frontend
    assert "content.innerHTML = text" not in frontend


def test_challenge_technologies_and_label_are_documented():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    for required in ("Firebase Authentication", "Cloud Firestore", "Secret Manager", "Gemini", "Cloud Run"):
        assert required in readme
    assert "dev-tutorial=cloud-run-ai-challenge" in readme
