import argparse
import json
from pathlib import Path

from evaluator import evaluate_suite, load_json


ROOT = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description="Score captured Clarity Compass model outputs.")
    parser.add_argument(
        "--responses",
        default=str(ROOT / "calibration_outputs.json"),
        help="JSON object mapping eval case IDs to captured model responses.",
    )
    parser.add_argument("--minimum-score", type=float, default=85.0)
    parser.add_argument("--output", help="Optional path for the JSON result artifact.")
    args = parser.parse_args()

    report = evaluate_suite(load_json(ROOT / "cases.json"), load_json(args.responses))
    report["response_source"] = str(Path(args.responses).resolve())
    report["calibration_only"] = Path(args.responses).resolve() == (ROOT / "calibration_outputs.json").resolve()
    rendered = json.dumps(report, indent=2)
    print(rendered)
    if args.output:
        Path(args.output).write_text(rendered + "\n", encoding="utf-8")
    raise SystemExit(0 if report["passed"] and report["aggregate_score"] >= args.minimum_score else 1)


if __name__ == "__main__":
    main()
