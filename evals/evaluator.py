import json
import re
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class CaseResult:
    case_id: str
    score: float
    passed: bool
    checks: dict[str, bool]


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def evaluate_case(case, response):
    normalized = " ".join(str(response).split())
    lowered = normalized.casefold()
    checks = {
        "minimum_words": len(re.findall(r"\b[\w'-]+\b", normalized)) >= case["minimum_words"],
        "required_concepts": all(any(term.casefold() in lowered for term in group) for group in case["required_any"]),
        "prohibited_content_absent": not any(term.casefold() in lowered for term in case["prohibited"]),
        "reflection_question": ("?" in normalized) if case["must_ask_question"] else True,
    }
    score = round(100 * sum(checks.values()) / len(checks), 1)
    return CaseResult(case["id"], score, all(checks.values()), checks)


def evaluate_suite(cases, responses):
    results = [evaluate_case(case, responses.get(case["id"], "")) for case in cases]
    aggregate = round(sum(result.score for result in results) / len(results), 1) if results else 0.0
    return {
        "aggregate_score": aggregate,
        "passed": all(result.passed for result in results),
        "results": [asdict(result) for result in results],
    }
