#!/usr/bin/env bash
# Full local pipeline: install -> scrape -> test -> run with the real model -> (optional) Docker build.
# Usage: bash scripts/pipeline.sh            (MAX_PAGES=60 bash scripts/pipeline.sh to crawl more)
set -euo pipefail
cd "$(dirname "$0")/.."

step() { printf '\n\033[1;34m==> %s\033[0m\n' "$*"; }
warn() { printf '\033[1;33m%s\033[0m\n' "$*"; }
ok()   { printf '\033[1;32m%s\033[0m\n' "$*"; }

step "1/6  Python environment"
python3 -m venv .venv
# shellcheck disable=SC1091
source .venv/bin/activate
pip install -q --upgrade pip
pip install -q -r requirements-dev.txt
ok "Dependencies installed in .venv"

step "2/6  Keys (.env)"
if [ ! -f .env ]; then
  cp .env.example .env
  warn "Created .env. Open it, paste your OpenRouter key after OPENROUTER_API_KEY=, save, and run this script again."
  exit 1
fi
set -a; source .env; set +a
if [ -z "${OPENROUTER_API_KEY:-}" ]; then
  warn "OPENROUTER_API_KEY is empty in .env. Paste your key there, save, and run this script again."
  exit 1
fi
ok "OpenRouter key found in .env (it stays on this computer)"

step "3/6  Scraping darglobal.co.uk and wasalt.sa"
if python scraper/scrape.py --max-pages "${MAX_PAGES:-40}"; then
  ok "Scraped pages saved to data/scraped/ (details in data/scraped/manifest.json)"
else
  warn "No pages were scraped; continuing with the curated data in data/."
fi

step "4/6  Tests"
python -m pytest -q

step "5/6  Live check with the real model"
PORT_LOCAL="${PORT_LOCAL:-7861}"
uvicorn app.main:app --port "$PORT_LOCAL" > .pipeline-server.log 2>&1 &
SERVER_PID=$!
trap 'kill "$SERVER_PID" 2>/dev/null || true' EXIT
for _ in $(seq 1 30); do
  curl -sf "http://127.0.0.1:$PORT_LOCAL/api/health" > /dev/null && break
  sleep 1
done
echo "Health: $(curl -s "http://127.0.0.1:$PORT_LOCAL/api/health")"
RESPONSE=$(curl -s -X POST "http://127.0.0.1:$PORT_LOCAL/api/chat" \
  -H 'Content-Type: application/json' \
  -d '{"message":"Which luxury brands has DarGlobal partnered with?"}')
if ! python - "$RESPONSE" <<'PY'
import json, sys
data = json.loads(sys.argv[1])
print("\nAnswer:\n" + data["answer"])
print("\nMode:", data["mode"], "| Model:", data.get("model"))
if data["mode"] != "llm":
    print("\n\033[1;33mThe model did not answer. Reason from the server log:\033[0m")
    sys.exit(2)
PY
then
  grep -i "LLM unavailable" .pipeline-server.log | tail -3 || true
  warn "Check the key in .env, and that your OpenRouter privacy settings allow free models."
  exit 1
fi
ok "The model is answering."

step "6/6  Docker build (optional)"
if command -v docker > /dev/null 2>&1 && docker info > /dev/null 2>&1; then
  docker build -t property-assistant .
  ok "Docker image built: docker run -p 7860:7860 --env-file .env property-assistant"
else
  warn "Docker isn't running here, so the image build was skipped. Hugging Face builds it for you on deploy."
fi

printf '\n'
ok "Pipeline complete."
echo "Try it on this computer:  bash scripts/run_local.sh"
echo "Deploy to Hugging Face:   python scripts/deploy_hf.py"
