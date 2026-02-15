#!/usr/bin/env bash
set -euo pipefail


# Directory of the repo (absolute path = no ambiguity)
# PUT YOUR OWN PATH HERE BELOW
REPO_DIR="/Users/firstlast/repo"
cd "$REPO_DIR"

# Activate venv (absolute path = no ambiguity)
source "$REPO_DIR/venv/bin/activate"

# Optional: ensure Playwright browsers exist (usually not needed every run)
# python -m playwright install chromium >/dev/null 2>&1 || true

# Run
python script_v2.py