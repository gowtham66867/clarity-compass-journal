# Browser QA evidence

**Environment:** local production-style FastAPI server  
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
| Desktop overflow | Pass | No horizontal overflow at 1280×720. |
| Mobile overflow | Pass | No horizontal overflow at 390×844; sign-in remains visible and the hero stays within the viewport. |
| Browser runtime | Pass | No warning or error entries were recorded after loading and mobile reload. |

## Still requiring authenticated browser evidence

- Google popup completion with the final neutral Cloud Run authorized domain.
- Keyboard traversal and visible focus through mode selection, history and sign-out.
- Authenticated dashboard behavior at mobile width.
- Two-account history isolation in the deployed Firebase project.
- Automated WCAG scanning and Firefox/WebKit coverage.
