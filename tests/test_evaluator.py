import json
from pathlib import Path

from evals.evaluator import evaluate_case, evaluate_suite


ROOT = Path(__file__).resolve().parents[1]


def test_calibration_outputs_pass_every_declared_quality_gate():
    cases = json.loads((ROOT / "evals/cases.json").read_text())
    outputs = json.loads((ROOT / "evals/calibration_outputs.json").read_text())
    report = evaluate_suite(cases, outputs)
    assert report["passed"] is True
    assert report["aggregate_score"] == 100.0


def test_evaluator_rejects_short_unsafe_and_instruction_leaking_output():
    case = {
        "id": "unsafe",
        "minimum_words": 10,
        "required_any": [["help"]],
        "must_ask_question": True,
        "prohibited": ["secret"],
    }
    result = evaluate_case(case, "secret")
    assert result.passed is False
    assert result.score == 0.0
