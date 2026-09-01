#!/bin/sh
set -eu

ROOT="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
cd "$ROOT"

PYTHON_BIN="${PYTHON_BIN:-python3}" scripts/test_all.sh
npm run test:rules
npm audit --omit=dev --audit-level=high

echo "PASS: complete deterministic release gate, including executable Firestore rules"
