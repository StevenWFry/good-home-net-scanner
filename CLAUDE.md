# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Backend (root required for nmap ARP scan + OS detection)
./run.sh                              # sudo uvicorn with .venv, port 8000, --reload
# or manually:
sudo .venv/bin/uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

# Frontend dev server (proxies /api and /ws to :8000)
cd frontend && npm run dev            # port 5173

# Frontend production build (FastAPI then serves it at /)
cd frontend && npm run build

# Python dependency management (system has no pip; always use venv)
.venv/bin/pip install -r requirements.txt
```

**Prerequisites:** `sudo dnf install -y nmap` — nmap is not bundled and must be installed separately.

## Architecture

The app is a single FastAPI process that handles REST, WebSockets, and (in production) static file serving for the built React frontend.

### Scan pipeline (`backend/api/scans.py` → `run_scan()`)
Scans run as a single `asyncio.Task`. The three phases run sequentially:
1. **Discover** — `scanner/discover.py` runs `nmap -sn` in a `ThreadPoolExecutor`. A progress callback fires per host; it uses `asyncio.run_coroutine_threadsafe(coro, loop)` to broadcast back to the event loop (the loop is captured before entering the executor).
2. **Vendor** — `scanner/vendor.py` calls `mac-vendor-lookup` (local OUI DB, no network) per discovered MAC.
3. **Port scan** — `scanner/ports.py` runs `nmap -sV --top-ports 100 -O` per device in a `ThreadPoolExecutor`. Ports are fully replaced in the DB on each scan.

Live progress is broadcast to all connected WebSocket clients via `ConnectionManager` in `main.py`. The broadcast function is injected into `scans.py` at startup via `set_broadcast()`.

### State
- Scan state is a plain in-process dict (`_scan_state` in `scans.py`) — appropriate for a single-process local tool.
- SQLite DB (`scanner.db` in CWD, overridable via `DB_PATH` env var). Devices are upserted by IP address. All devices are marked offline at the start of each scan, then re-marked online as they're found.

### asyncio / threading rule
All blocking nmap calls run in `ThreadPoolExecutor` via `run_in_executor`. Use `asyncio.get_running_loop()` (not `get_event_loop()`) in async contexts. To schedule coroutines from inside a thread, use `asyncio.run_coroutine_threadsafe(coro, loop)` with the loop captured before entering the executor.

### Frontend
Vite proxies `/api` and `/ws` to `:8000` in dev. In production, FastAPI mounts `frontend/dist` as static files. The `useWebSocket` hook auto-reconnects every 3 seconds on close. Device icon type is inferred by `_infer_icon()` in `ports.py` from vendor name, hostname patterns, and open port numbers, and can be overridden per-device via `PATCH /api/devices/{id}`.
