import argparse
import json
import math
import os
import statistics
import time
from pathlib import Path

import httpx


ROOT = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description="Capture synthetic live responses for the eval suite.")
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--token-env", default="FIREBASE_ID_TOKEN")
    parser.add_argument("--metadata-output", help="Optional non-secret capture provenance JSON path.")
    parser.add_argument(
        "--preserve-history",
        action="store_true",
        help="Keep synthetic interactions. By default every case is isolated and deleted after capture.",
    )
    args = parser.parse_args()

    token = os.getenv(args.token_env, "").strip()
    if not token:
        raise SystemExit(f"Set {args.token_env} to a short-lived Firebase ID token.")

    cases = json.loads((ROOT / "cases.json").read_text(encoding="utf-8"))
    responses = {}
    backends = {}
    latency_ms = {}
    with httpx.Client(base_url=args.base_url.rstrip("/"), timeout=90) as client:
        for case in cases:
            started = time.perf_counter()
            response = client.post(
                "/api/chat",
                headers={"Authorization": f"Bearer {token}"},
                json={"message": case["prompt"], "mode": case["mode"]},
            )
            response.raise_for_status()
            body = response.json()
            latency_ms[case["id"]] = round((time.perf_counter() - started) * 1000, 1)
            responses[case["id"]] = body["response"]
            backends[case["id"]] = body["backend"]
            if not args.preserve_history:
                cleanup = client.delete(
                    "/api/history",
                    headers={"Authorization": f"Bearer {token}"},
                )
                cleanup.raise_for_status()

    Path(args.output).write_text(json.dumps(responses, indent=2) + "\n", encoding="utf-8")
    if args.metadata_output:
        sorted_latency = sorted(latency_ms.values())
        percentile_index = max(0, min(len(sorted_latency) - 1, math.ceil(0.95 * len(sorted_latency)) - 1))
        metadata = {
            "base_url": args.base_url.rstrip("/"),
            "case_count": len(cases),
            "history_isolated_between_cases": not args.preserve_history,
            "backend_by_case": backends,
            "latency_ms_by_case": latency_ms,
            "mean_latency_ms": round(statistics.mean(sorted_latency), 1),
            "p95_latency_ms": sorted_latency[percentile_index],
        }
        Path(args.metadata_output).write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    print(f"Captured {len(responses)} synthetic responses in {args.output}")


if __name__ == "__main__":
    main()
