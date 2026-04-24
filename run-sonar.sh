#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SONAR_HOST_URL="${SONAR_HOST_URL:-http://localhost:9000}"
SONAR_TOKEN="${SONAR_TOKEN:-${1:-}}"

if [[ -z "${SONAR_TOKEN}" ]]; then
  echo "Uso:"
  echo "  SONAR_TOKEN=<tu_token> ./run-sonar.sh"
  echo "  o"
  echo "  ./run-sonar.sh <tu_token>"
  exit 1
fi

echo "Ejecutando SonarScanner en ${PROJECT_DIR}"
echo "Servidor SonarQube: ${SONAR_HOST_URL}"

docker run --rm --network host \
  -e SONAR_HOST_URL="${SONAR_HOST_URL}" \
  -e SONAR_TOKEN="${SONAR_TOKEN}" \
  -v "${PROJECT_DIR}:/usr/src" \
  sonarsource/sonar-scanner-cli
