# Ideathon Prototype Submission

## Working prototype

https://clarity-compass-journal-412542191970.asia-south1.run.app/

## Public repository

https://github.com/gowtham66867/clarity-compass-journal

## Demo social post draft

I built **Clarity Compass**, a private AI reflection and decision-support
workspace running on Google Cloud Run.

Users authenticate securely with Google through Firebase Authentication, explore
ideas with the Gemini API across multiple turns, and return to a private history
stored in user-isolated Cloud Firestore paths. The Gemini API key never reaches
the browser—it is restricted and delivered to the Cloud Run runtime through
Google Cloud Secret Manager.

I also added three focused modes—Clarity, Decision, and Wellbeing—plus backend
Firebase token verification, deny-by-default Firestore rules, safe text rendering,
strict prompt validation, and a dedicated least-privilege service account.

The public repository includes a one-command release gate with 25 API/security
tests, five executable Firebase Emulator authorization tests, ten synthetic AI
quality and safety evaluations, 93% application/evaluator coverage, dependency
auditing, and a production Docker build in GitHub Actions.

Live demo: https://clarity-compass-journal-412542191970.asia-south1.run.app/

#AccelerateAIwithCloudRun #GeminiAPI #Firebase #Firestore #GoogleCloud

## Brief description for the submission form

Clarity Compass is a secure, personalized AI reflection and decision-support
application deployed on Google Cloud Run. Users sign in with Google using Firebase
Authentication, choose a Clarity, Decision, or Wellbeing mode, and hold multi-turn
conversations with Gemini 3.6 Flash. Every completed exchange is persisted under
an owner-isolated `users/{uid}/interactions` path in Cloud Firestore, enabling a
private history that is available across sessions. The Cloud Run backend verifies
Firebase ID tokens on every private API request and derives the Firestore path only
from the verified UID. The restricted Gemini API key is stored in Google Cloud
Secret Manager and injected only into the dedicated least-privilege runtime service
account. Deny-by-default Firestore rules, strict input limits, safe text rendering,
and reliable error/retry states harden the deployment. The public evaluation
harness adds API isolation tests, executable Firebase Emulator rule checks, and
ten synthetic Gemini quality and safety cases.

## Services to select

- User authentication via Firebase
- Multi-turn interaction with the Gemini API
- User-isolated Firestore document storage
- Secure API key retrieval via Google Cloud Secret Manager
