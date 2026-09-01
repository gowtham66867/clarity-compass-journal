#!/bin/sh
set -eu

ROOT="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
cd "$ROOT"

PYTHON_BIN="${PYTHON_BIN:-python3}"

"$PYTHON_BIN" -m pytest --cov=app --cov=evals.evaluator --cov-report=term-missing --cov-fail-under=85
"$PYTHON_BIN" evals/run_evals.py --minimum-score 85
"$PYTHON_BIN" -m compileall -q app evals tests
git diff --check

echo "PASS: API, security, isolation, failure-path, release-contract, and eval calibration gates"
echo "INFO: run 'npm run test:rules' for the Firestore Emulator authorization gate"
