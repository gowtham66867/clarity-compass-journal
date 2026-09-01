"""Read-only smoke verification for a deployed Clarity Compass service."""

import argparse
import json
import sys

import httpx


REQUIRED_HEADERS = {
    "content-security-policy": "frame-ancestors 'none'",
    "x-content-type-options": "nosniff",
    "x-frame-options": "DENY",
    "referrer-policy": "strict-origin-when-cross-origin",
    "strict-transport-security": "max-age=31536000",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def verify(base_url: str) -> dict:
    checks = {}
    with httpx.Client(base_url=base_url.rstrip("/"), timeout=30, follow_redirects=True) as client:
        shell = client.get("/")
        require(shell.status_code == 200, f"public shell returned {shell.status_code}")
        require("Clarity Compass" in shell.text, "neutral product brand is missing")
        require("texmed" not in shell.text.casefold(), "previous work-related brand is exposed")
        checks["public_neutral_shell"] = True

        for header, expected in REQUIRED_HEADERS.items():
            require(expected in shell.headers.get(header, ""), f"missing or invalid {header}")
        require(bool(shell.headers.get("x-request-id")), "missing request correlation header")
        checks["security_headers"] = True

        health = client.get("/api/health")
        require(health.status_code == 200, f"health endpoint returned {health.status_code}")
        payload = health.json()
        require(payload.get("status") == "ok", "health status is not ok")
        for component in ("firebase_auth", "firestore", "gemini_secret_configured"):
            require(payload.get(component) is True, f"health component failed: {component}")
        checks["configured_components"] = True

        config = client.get("/api/config")
        require(config.status_code == 200, f"public config returned {config.status_code}")
        serialized_config = json.dumps(config.json())
        require("GEMINI" not in serialized_config.upper(), "Gemini secret metadata leaked")
        require("PRIVATE KEY" not in serialized_config.upper(), "private key leaked")
        checks["public_config_minimized"] = True

        private = client.get("/api/history")
        require(private.status_code == 401, f"private history returned {private.status_code}")
        require(private.headers.get("cache-control") == "no-store", "private API can be cached")
        checks["private_api_requires_firebase"] = True

    return {"base_url": base_url.rstrip("/"), "passed": True, "checks": checks}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("base_url")
    args = parser.parse_args()
    try:
        print(json.dumps(verify(args.base_url), indent=2))
    except (AssertionError, httpx.HTTPError) as exc:
        print(json.dumps({"base_url": args.base_url, "passed": False, "error": str(exc)}, indent=2))
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
