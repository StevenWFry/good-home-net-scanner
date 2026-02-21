# Good Home Network Scanner

## Overview
Local home network scanner web app — no data sharing, no login, runs entirely locally.

## Stack
- **Backend**: Python + FastAPI + SQLite (SQLAlchemy)
- **Frontend**: React + Vite + TailwindCSS
- **Scanning**: `nmap` via `python-nmap` (requires root or setcap)
- **MAC vendor**: `mac-vendor-lookup` (local OUI database)
- **Real-time**: WebSockets for live scan progress

## Development
```bash
# Terminal 1 — Backend (needs root for nmap)
./run.sh
# or: sudo uvicorn backend.main:app --reload

# Terminal 2 — Frontend dev server
cd frontend && npm install && npm run dev
```

Open http://localhost:5173 in dev mode (Vite proxies /api and /ws to port 8000).

## Production
```bash
cd frontend && npm run build
./run.sh   # FastAPI serves the built frontend at /
```

## nmap Privileges
`nmap -sn` (ARP sweep) and `-O` (OS detection) require root.

Option A: run with sudo (run.sh does this).
Option B: `sudo setcap cap_net_raw,cap_net_admin+eip $(which nmap)`

## Project Structure
```
backend/
  main.py          FastAPI app, WebSocket, mounts frontend static
  scanner/
    discover.py    ARP+ping sweep (nmap -sn)
    ports.py       Port/service/OS scan (nmap -sV -O)
    vendor.py      MAC → vendor name
  db/
    database.py    SQLite engine + session
    models.py      Device, Port, ScanHistory
  api/
    devices.py     GET/PATCH /api/devices
    scans.py       POST /api/scan, GET /api/scan/status
frontend/
  src/
    components/    DeviceCard, DeviceGrid, ScanButton, ScanProgress
    pages/         Dashboard, DeviceDetail
    lib/           api.js, useWebSocket.js
```
