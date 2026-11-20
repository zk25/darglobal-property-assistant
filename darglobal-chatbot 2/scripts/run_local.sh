#!/usr/bin/env bash
# Run the app on this computer with the key from .env: http://127.0.0.1:7860
set -euo pipefail
cd "$(dirname "$0")/.."
[ -d .venv ] || { echo "Run  bash scripts/pipeline.sh  first."; exit 1; }
# shellcheck disable=SC1091
source .venv/bin/activate
[ -f .env ] && { set -a; source .env; set +a; }
echo "Open http://127.0.0.1:7860  (Ctrl+C to stop)"
exec uvicorn app.main:app --port 7860 --reload
