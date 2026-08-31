# Clarity Compass evaluation report

**Overall rating: 8.0 / 10**  
**Assessment basis:** source review, deterministic API integration tests,
failure injection, security/release contracts, coverage, build dependency
resolution, and evaluation-harness calibration.

## Scored rubric

| Dimension | Weight | Score | Evidence and deduction |
|---|---:|---:|---|
| Security and privacy | 2.0 | 1.6 | Firebase token verification, owner-derived paths, deny-by-default rules, safe text rendering and Secret Manager. Deduction: no automated Firebase Emulator rule test, rate limiting or security-header gate. |
| Functional correctness | 1.5 | 1.35 | Auth, history ordering, tenant isolation, multi-turn context, primary Gemini path and quota fallback are covered. Failed/empty model calls do not persist partial exchanges. |
| Cloud/challenge architecture | 1.5 | 1.35 | Firebase Auth, Firestore, Cloud Run, Gemini and Secret Manager are implemented with a dedicated runtime identity. Deduction: neutral rebrand is not yet deployed because cloud reauthentication is pending. |
| AI quality and safety | 1.5 | 1.1 | Six explicit eval cases cover clarity, decisions, non-clinical wellbeing, prompt injection, urgent safety and uncertainty. Deduction: the 100/100 calibration score validates the evaluator only; a captured live Gemini run is still required. |
| UX and accessibility | 1.0 | 0.8 | Responsive, clear authenticated workflow, labelled controls, status region and safe rendering. Deduction: no automated browser accessibility or cross-browser suite. |
| Test and release discipline | 1.5 | 1.4 | 18 automated tests pass with 91% statement coverage; one-command release gate and detailed test matrix added. Harness caught an invalid FastAPI version constraint. |
| Operations and submission readiness | 1.0 | 0.4 | Public repository and submission copy exist. Deduction: neutral Cloud Run URL, social post, live two-account isolation evidence, observability and load tests remain open. |
| **Total** | **10.0** | **8.0** | Strong production-oriented prototype; not yet a fully evidenced public release. |

## Executed results

- `18/18` API, evaluator and release-contract tests passed.
- `91%` statement coverage across the application and deterministic evaluator.
- `6/6` quality/safety calibration cases passed all declared rubric checks.
- Repository brand scan, obvious-secret scan, Firestore rule contract, frontend
  text-rendering contract and challenge-technology checks passed.
- Python compilation and whitespace checks passed.
- Production-container smoke verification is implemented but was not executed
  because the local Docker daemon was not running.
- The harness detected and corrected the unavailable FastAPI `>=0.133`
  constraint to the compatible `0.128.x` release line.

## Interpretation of the evaluation score

The calibration fixture deliberately contains responses that satisfy the rubric.
Its 100/100 result proves the scorer and thresholds are wired correctly; it is
not evidence that the deployed model achieves 100/100. A real model score must
be generated from synthetic live outputs:

```bash
export FIREBASE_ID_TOKEN="short-lived-test-token"
.venv/bin/python evals/capture_live.py \
  --base-url="https://YOUR-NEUTRAL-CLOUD-RUN-URL" \
  --output=/tmp/clarity-compass-live-responses.json
.venv/bin/python evals/run_evals.py \
  --responses=/tmp/clarity-compass-live-responses.json
```

The capture writes six synthetic exchanges to the authenticated test account's
Firestore history. Use a dedicated non-production account and remove the test
documents afterward.

## Highest-value work needed for 9/10

1. Deploy the neutral service and record Cloud Run/Firebase/Secret Manager IAM
   evidence.
2. Run the six live Gemini eval cases and achieve at least 85/100 with every
   safety-critical case passing.
3. Add Firebase Emulator tests for Firestore rules and revoked-token behavior.
4. Add rate limiting, security headers, structured request IDs, latency/error
   metrics and alerts.
5. Add automated Playwright accessibility, mobile, failure-state and two-account
   journeys.
6. Publish the required social demo and verify every submission link anonymously.
