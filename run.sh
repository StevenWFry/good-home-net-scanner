#!/usr/bin/env bash
# Run with sudo so nmap can do ARP scanning and OS detection.
# Alternative: sudo setcap cap_net_raw,cap_net_admin+eip $(which nmap)
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

PYTHON="$SCRIPT_DIR/.venv/bin/python"
if [ ! -f "$PYTHON" ]; then
  echo "Virtual environment not found. Run: python3 -m venv .venv && .venv/bin/pip install -r requirements.txt"
  exit 1
fi

exec sudo -E env PATH="$SCRIPT_DIR/.venv/bin:$PATH" "$PYTHON" -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
