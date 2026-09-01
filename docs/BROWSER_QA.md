# Browser QA evidence

**Environment:** public Cloud Run revision `clarity-compass-journal-00003-d6f`

**Browser surface:** Chromium-based in-app browser

**Data used:** public landing page only; no account, token or reflection submitted

## Verified observations

| Check | Result | Evidence |
|---|---|---|
| Neutral brand | Pass | Document title and accessible home link are `Clarity Compass`; brand mark is `C`. |
| Semantic landmark | Pass | Rendered accessibility tree exposes banner, main region and one visible landing-page level-one heading. |
| Primary action | Pass | `Continue with Google` is exposed as a button with an accessible text name. |
| Form labelling | Pass | No visible input/textarea/select lacked an associated label or accessible name. |
| Duplicate IDs | Pass | DOM audit returned no duplicate IDs. |
| Missing image alternatives | Pass | DOM audit returned zero images without `alt`; the decorative hero is CSS. |
| Desktop overflow | Pass | No horizontal overflow at 1440×900. |
| Mobile overflow | Pass | No horizontal overflow at 390×844; sign-in remains visible and the hero stays within the viewport. |
| Browser runtime | Pass | No warning or error entries were recorded after loading and mobile reload. |

## Submission screenshots

- [Desktop Cloud Run landing page](screenshots/clarity-compass-cloud-run-desktop.png)
- [Mobile Cloud Run landing page](screenshots/clarity-compass-cloud-run-mobile.png)

## Still requiring authenticated browser evidence

- Google popup completion with the final neutral Cloud Run authorized domain.
- Keyboard traversal and visible focus through mode selection, history and sign-out.
- Authenticated dashboard behavior at mobile width.
- Automated WCAG scanning and Firefox/WebKit coverage.

Two-account isolation is verified through the deployed authenticated API and
recorded separately in [`LIVE_EVALUATION.md`](LIVE_EVALUATION.md).
