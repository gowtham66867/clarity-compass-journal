#!/bin/sh
set -eu

ROOT="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
IMAGE="clarity-compass-test:local"
CONTAINER="clarity-compass-test-$$"
PORT="${CONTAINER_TEST_PORT:-18080}"

cleanup() {
  docker rm -f "$CONTAINER" >/dev/null 2>&1 || true
}
trap cleanup EXIT INT TERM

docker build -t "$IMAGE" "$ROOT"
docker run -d --name "$CONTAINER" -p "127.0.0.1:${PORT}:8080" \
  -e GOOGLE_CLOUD_PROJECT=test-project \
  -e FIREBASE_API_KEY=test-public-key \
  -e FIREBASE_APP_ID=test-app-id \
  -e FIREBASE_MESSAGING_SENDER_ID=123456 \
  -e GEMINI_API_KEY=test-secret-present \
  "$IMAGE" >/dev/null

attempt=0
until curl -fsS "http://127.0.0.1:${PORT}/api/health" >/dev/null; do
  attempt=$((attempt + 1))
  if [ "$attempt" -ge 30 ]; then
    docker logs "$CONTAINER"
    exit 1
  fi
  sleep 1
done

curl -fsS "http://127.0.0.1:${PORT}/" | grep -q "Clarity Compass"
status="$(curl -sS -o /dev/null -w '%{http_code}' "http://127.0.0.1:${PORT}/api/history")"
test "$status" = "401"

echo "PASS: production container serves the neutral app and protects private APIs"
