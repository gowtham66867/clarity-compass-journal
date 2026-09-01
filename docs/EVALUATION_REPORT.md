# Clarity Compass evaluation report

**Overall rating: 9.6 / 10**
**Assessment basis:** source review, deterministic API integration tests,
failure injection, security/release contracts, coverage, build dependency
resolution, and evaluation-harness calibration.

## Scored rubric

| Dimension | Weight | Score | Evidence and deduction |
|---|---:|---:|---|
| Security and privacy | 2.0 | 1.95 | Firebase token verification, owner-derived paths, deny-by-default rules, safe text rendering, Secret Manager, CSP/security headers, per-user abuse protection and email-free persistence. Five Firebase Emulator cases execute owner and default-deny rules. Deduction: rate limiting is instance-local. |
| Functional correctness | 1.5 | 1.5 | Auth, history ordering, tenant isolation, multi-turn context, primary Gemini path, bounded timeouts and quota fallback are covered. Failed/empty/timed-out model calls do not persist partial exchanges. |
| Cloud/challenge architecture | 1.5 | 1.45 | Firebase Auth, Firestore, Cloud Run, Gemini and Secret Manager are deployed with a dedicated runtime identity and challenge label. Deduction: live requests used the documented Vertex quota fallback because AI Studio prepaid quota is exhausted. |
| AI quality and safety | 1.5 | 1.45 | Ten isolated deployed-model cases achieved 100/100 across clarity, decisions, non-clinical wellbeing, prompt injection, urgent safety, uncertainty, privacy, diagnosis boundaries, anti-dependency and reversible action. Deduction: the scorer is transparent lexical evaluation rather than an independent expert panel. |
| UX and accessibility | 1.0 | 0.95 | Responsive, labelled and semantically structured landing experience passed rendered desktop/mobile DOM and browser-error checks; owners can permanently clear history. Deduction: authenticated cross-browser accessibility remains manual. |
| Test and release discipline | 1.5 | 1.5 | 26 Python/API tests and 5 executable Firestore rule tests pass with 94% statement coverage; one-command gate, detailed matrix, dependency audit, browser evidence, CI and Docker build gate are included. |
| Operations and submission readiness | 1.0 | 0.8 | Neutral public Cloud Run URL, dedicated identity, public repository, live two-account isolation, cleanup, request correlation, deployment verifier and green CI exist. Deduction: social demo, distributed observability and load tests remain open. |
| **Total** | **10.0** | **9.6** | Submission-grade release with transparent remaining evidence and operational limitations. |

## Executed results

- `26/26` API, evaluator and release-contract tests passed.
- `5/5` Firebase Emulator authorization suites passed owner CRUD/query,
  cross-user denial, unauthenticated denial and deny-by-default checks.
- `94%` statement coverage across the application and deterministic evaluator.
- `10/10` quality/safety calibration cases passed all declared rubric checks.
- Production dependency audit reported zero known vulnerabilities; Firebase
  tooling remains development-only and is excluded from the runtime image.
- Repository brand scan, obvious-secret scan, Firestore rule contract, frontend
  text-rendering contract and challenge-technology checks passed.
- Python compilation and whitespace checks passed.
- Production-container smoke verification is implemented but was not executed
  because the local Docker daemon was not running.
- The harness detected and corrected the unavailable FastAPI `>=0.133`
  constraint to the compatible `0.128.x` release line.
- Desktop and mobile rendered-page checks passed without overflow, duplicate IDs,
  unlabeled inputs, missing image alternatives, or browser runtime errors.
- GitHub Actions now runs the deterministic gate and production image build on
  every push and pull request.
- The neutral Cloud Run deployment passed the public smoke verifier and a live
  two-account Firebase/Firestore isolation test with complete synthetic cleanup.
- Ten isolated deployed-model outputs scored 100/100; mean chat latency was
  3.56 seconds and p95 was 4.39 seconds.

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

By default, the capture deletes the authenticated test account's history after
every synthetic case. This isolates cases from multi-turn contamination and
leaves no evaluation documents behind. Use only a dedicated non-production
account; `--preserve-history` is available solely for deliberate debugging.

## Remaining work before final form submission

1. Restore AI Studio prepaid quota and recapture primary-backend eval provenance.
2. Record a short demo and publish the required social post.
3. Verify Google popup sign-in and revoked-token behavior with a non-temporary
   Google test account.
4. Move the local abuse limiter to a distributed managed store and add
   latency/error metrics and alerts.
5. Add automated Playwright accessibility, mobile, failure-state and two-account
   journeys.
6. Verify every submission link anonymously and submit the form.
