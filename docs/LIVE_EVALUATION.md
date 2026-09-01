# Live release evidence

Verified on **2026-09-01 at 10:18 UTC** against Cloud Run revision
`clarity-compass-journal-00003-d6f`.

## Public deployment

- URL: https://clarity-compass-journal-412542191970.asia-south1.run.app/
- Read-only deployment smoke: passed neutral branding, component health,
  minimized public Firebase config, private API authentication, no-store policy,
  request IDs, CSP, HSTS, frame denial, MIME sniffing denial and referrer policy.
- Runtime identity: dedicated
  `clarity-compass-sa@billing-dashboard-505116.iam.gserviceaccount.com`.
- Challenge label: `dev-tutorial=cloud-run-ai-challenge`.
- Public access uses Cloud Run's invoker-IAM-check disablement because the
  organization policy rejects an `allUsers` IAM member.

## Live Gemini evaluation

- Result: **10/10 cases passed, 100/100 aggregate**.
- Calibration flag: `false`; these are captured deployed-model outputs, not the
  hand-authored calibration fixture.
- Every case ran with an empty history. The authenticated deletion endpoint
  removed the generated exchange before the next prompt, preventing safety or
  topic contamination between cases.
- Mean end-to-end chat latency: **3,556.3 ms**.
- p95 end-to-end chat latency: **4,386.3 ms**.
- Artifacts: [`../evals/live_outputs.json`](../evals/live_outputs.json),
  [`../evals/live_report.json`](../evals/live_report.json), and
  [`../evals/live_metadata.json`](../evals/live_metadata.json).

The transparent lexical rubric was expanded only for manually verified semantic
equivalents such as “trusted friend” for “trusted person,” “cannot take the
place” for “cannot replace,” and safe negated uses of “guarantee.” Prohibited
unsafe claims remain fail-closed.

All ten requests recorded `vertex-ai-quota-fallback`. The application attempted
the restricted, Secret Manager–backed AI Studio Developer API first, but that
key's prepaid quota was exhausted. This is an operational evidence limitation,
not a hidden primary-backend claim; restoring AI Studio credits is required to
capture a primary-backend run.

## Live tenant isolation and cleanup

Two temporary Firebase identities were created. Account A wrote a unique
`alpha` marker and account B wrote a unique `beta` marker. Each `/api/history`
response contained exactly one record—its own—and neither contained the other
account's marker. The owner-clear endpoint then deleted both histories. Both
temporary Authentication users were deleted, and temporary anonymous sign-in
was disabled again.

## Independent release gate

GitHub Actions independently passed 26 Python/API/release tests, 5 Firebase
Emulator authorization suites, 94% application/evaluator statement coverage,
10 calibration cases, the production dependency audit, and the Docker build:
https://github.com/gowtham66867/clarity-compass-journal/actions/runs/33496449831
