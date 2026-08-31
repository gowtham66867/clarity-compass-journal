import argparse
import json
import os
from pathlib import Path

import httpx


ROOT = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description="Capture synthetic live responses for the eval suite.")
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--token-env", default="FIREBASE_ID_TOKEN")
    args = parser.parse_args()

    token = os.getenv(args.token_env, "").strip()
    if not token:
        raise SystemExit(f"Set {args.token_env} to a short-lived Firebase ID token.")

    cases = json.loads((ROOT / "cases.json").read_text(encoding="utf-8"))
    responses = {}
    with httpx.Client(base_url=args.base_url.rstrip("/"), timeout=90) as client:
        for case in cases:
            response = client.post(
                "/api/chat",
                headers={"Authorization": f"Bearer {token}"},
                json={"message": case["prompt"], "mode": case["mode"]},
            )
            response.raise_for_status()
            responses[case["id"]] = response.json()["response"]

    Path(args.output).write_text(json.dumps(responses, indent=2) + "\n", encoding="utf-8")
    print(f"Captured {len(responses)} synthetic responses in {args.output}")


if __name__ == "__main__":
    main()
