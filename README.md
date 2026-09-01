# Clarity Compass

Clarity Compass is a production-oriented, authenticated AI reflection and
decision journal. Users sign in with Google through Firebase Authentication,
hold multi-turn conversations with Gemini, and revisit a private history stored
under an owner-bound Cloud Firestore path. The application runs as one container
on Google Cloud Run.

## Architecture

```text
Browser
  └─ Firebase Google Sign-In → Firebase ID token
       └─ Cloud Run /api/*
            ├─ Firebase Admin: verify ID token
            ├─ Firestore: users/{verified_uid}/interactions/{id}
            └─ Gemini API: key injected from Secret Manager
```

The public Firebase web configuration contains no operational secret. The Gemini
API key is restricted to the Generative Language API and is injected into the
Cloud Run container from Secret Manager. The backend never accepts a user ID
from the browser; it derives the Firestore path exclusively from a verified
Firebase ID token.

## Threat summary

| Threat zone | Risk | Countermeasure |
|---|---|---|
| Input | Oversized or malformed prompts | Pydantic schema validation and 4,000-character limit |
| Identity | Forged or expired sessions | Firebase Admin token verification on every private API call |
| State | Cross-user reads/writes | Owner-bound paths derived from verified `uid`; deny-by-default rules |
| Model | Prompt injection | Fixed server-side system instruction; history treated as user data |
| Output | HTML/script injection | Browser renders model text with `textContent` only |
| Secrets | Gemini key disclosure | Secret Manager injection; no key in source or frontend |
| Reliability | Prompt saved without response | Firestore write occurs only after a successful Gemini response |

## Features

- Google Sign-In through Firebase Authentication.
- Three guided reflection modes: Clarity, Decision, and Wellbeing.
- Multi-turn Gemini context using the user's recent private interactions.
- User-isolated Firestore history with a responsive authenticated dashboard.
- Backend JWT validation, strict payload limits, safe text rendering, and clear
  retry feedback.
- Restricted Gemini API key delivered through Google Cloud Secret Manager.
- Quota-resilient Gemini continuity: the secret-backed AI Studio Developer API is
  primary, with a same-project Vertex AI fallback only on quota exhaustion.
- Per-user sliding-window abuse protection and bounded Gemini request timeouts.
- Request IDs, privacy-safe structured request logs, API no-store behavior, and
  hardened browser security headers.
- Data minimization: Firestore stores the reflection, response, mode, timestamp,
  and Gemini backend provenance but not the user's email address.
- Account owners can permanently clear their saved reflection history from the
  workspace; the backend derives the deletion path from the verified UID.

## Local development

Prerequisites: Python 3.12+, a Firebase-enabled Google Cloud project, a Firestore
Native database, and Application Default Credentials.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export GOOGLE_CLOUD_PROJECT="your-project-id"
export GEMINI_API_KEY="local-development-key"
export FIREBASE_API_KEY="your-public-firebase-web-key"
export FIREBASE_APP_ID="your-firebase-web-app-id"
export FIREBASE_MESSAGING_SENDER_ID="your-project-number"
uvicorn app.main:app --reload
```

Do not commit `.env` files or operational API keys.

## Google Cloud and Firebase setup

Enable the required services:

```bash
gcloud services enable \
  run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com \
  firebase.googleapis.com identitytoolkit.googleapis.com firestore.googleapis.com \
  secretmanager.googleapis.com generativelanguage.googleapis.com apikeys.googleapis.com \
  --project="YOUR_PROJECT_ID"
```

Initialize Firebase for the project, create a Firebase Web App, enable Google as
a Firebase Authentication provider, and add the final Cloud Run hostname to the
Firebase authorized domains list.

Create Firestore and deploy the owner-bound rules:

```bash
gcloud firestore databases create \
  --database='(default)' \
  --location=asia-south1 \
  --type=firestore-native \
  --project="YOUR_PROJECT_ID"

npx firebase-tools deploy --only firestore:rules --project="YOUR_PROJECT_ID"
```

The deployed rules are intentionally deny-by-default:

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /users/{userId}/interactions/{interactionId} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }
    match /{document=**} {
      allow read, write: if false;
    }
  }
}
```

## Secret Manager and runtime identity

Create a dedicated service account and grant only the permissions needed by the
runtime:

```bash
gcloud iam service-accounts create clarity-compass-sa \
  --display-name="Clarity Compass Cloud Run" \
  --project="YOUR_PROJECT_ID"

gcloud projects add-iam-policy-binding "YOUR_PROJECT_ID" \
  --member="serviceAccount:clarity-compass-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/datastore.user"

gcloud projects add-iam-policy-binding "YOUR_PROJECT_ID" \
  --member="serviceAccount:clarity-compass-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/firebaseauth.viewer"

gcloud projects add-iam-policy-binding "YOUR_PROJECT_ID" \
  --member="serviceAccount:clarity-compass-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/aiplatform.user"
```

Create a Gemini API key in Google AI Studio or Google Cloud API Keys, restrict it
to `generativelanguage.googleapis.com`, and add it to Secret Manager:

```bash
gcloud secrets create GEMINI_API_KEY \
  --replication-policy="automatic" \
  --project="YOUR_PROJECT_ID"

printf '%s' 'YOUR_RESTRICTED_GEMINI_KEY' | \
  gcloud secrets versions add GEMINI_API_KEY \
    --data-file=- \
    --project="YOUR_PROJECT_ID"

gcloud secrets add-iam-policy-binding GEMINI_API_KEY \
  --member="serviceAccount:clarity-compass-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor" \
  --project="YOUR_PROJECT_ID"
```

## Cloud Run deployment

```bash
gcloud run deploy clarity-compass-journal \
  --source=. \
  --region=asia-south1 \
  --allow-unauthenticated \
  --service-account="clarity-compass-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
  --set-secrets="GEMINI_API_KEY=GEMINI_API_KEY:latest" \
  --set-env-vars="GOOGLE_CLOUD_PROJECT=YOUR_PROJECT_ID,GEMINI_MODEL=gemini-3.6-flash,FIREBASE_API_KEY=YOUR_PUBLIC_WEB_KEY,FIREBASE_APP_ID=YOUR_FIREBASE_APP_ID,FIREBASE_MESSAGING_SENDER_ID=YOUR_PROJECT_NUMBER" \
  --labels="dev-tutorial=cloud-run-ai-challenge" \
  --project="YOUR_PROJECT_ID"
```

Public access permits the browser to load the sign-in page. All user data and AI
endpoints remain protected by backend Firebase ID-token verification.

## Verification checklist

1. Load `/api/health` and confirm all configured components report healthy.
2. Confirm `/api/history` returns HTTP 401 without a Firebase ID token.
3. Sign in with Google and submit a reflection in each mode.
4. Refresh, sign in again, and confirm the saved history returns.
5. Confirm Firestore documents are stored only under the signed-in user's UID.
6. Sign in with a second account and verify it cannot see the first account's
   history.
7. Confirm the Cloud Run service has the label
   `dev-tutorial=cloud-run-ai-challenge`.
8. Confirm no Gemini API key appears in the page source, repository, or network
   responses.

Run the read-only public deployment smoke gate and retain its JSON output as
submission evidence:

```bash
.venv/bin/python scripts/verify_deployment.py "https://YOUR_SERVICE_URL"
```

## Test and evaluation harness

Install the development dependencies and run the complete deterministic gate:

```bash
python3.11 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
npm ci
PYTHON_BIN=.venv/bin/python scripts/release_gate.sh
scripts/verify_container.sh
```

The gate covers authenticated API behavior, tenant isolation, multi-turn context,
Gemini quota fallback, failure atomicity, input validation, release security
contracts, ten-case response-evaluator calibration, compilation, coverage,
dependency audit, diff whitespace, and executable Firebase Emulator tests for
owner-only Firestore access. Firebase CLI 15 requires Java 21. See
[`docs/TEST_PLAN.md`](docs/TEST_PLAN.md) for detailed manual and automated cases
and [`docs/EVALUATION_REPORT.md`](docs/EVALUATION_REPORT.md) for the
evidence-based rating and remaining release gaps.

Every push and pull request runs the same gate in GitHub Actions and also builds
the production Docker image. Local rendered-page evidence is recorded in
[`docs/BROWSER_QA.md`](docs/BROWSER_QA.md).

## Campaign

Built for the Cloud Run Build & Deploy Social Challenge. Demo posts should include
`#AccelerateAIwithCloudRun`.
