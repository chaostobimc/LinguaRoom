#!/usr/bin/env bash
# LinguaRoom convenience starter:
#   1. installs backend deps into a venv
#   2. installs + builds the frontend
#   3. runs the backend (which serves the built frontend from /)
set -e

cd "$(dirname "$0")"

echo "== Backend: venv + deps =="
cd backend
python3 -m venv .venv
# shellcheck disable=SC1091
source .venv/bin/activate
pip install --upgrade pip >/dev/null
pip install -r requirements.txt

# Optional: AI translation deps (deepseek4free dsk is bundled in
# backend/vendor/dsk — only needed when DEEPSEEK_TOKEN is set).
pip install -r requirements-ai.txt || echo "AI deps skipped (translation will be off until installed + token set)."

echo "== Frontend: install + build =="
cd ../frontend
npm install
npm run build

echo "== Starting LinguaRoom on http://localhost:8000 =="
cd ../backend
source .venv/bin/activate
exec uvicorn main:app --host 0.0.0.0 --port 8000
