# Good Home Network Scanner

A local network scanner with a web UI. Discovers devices on your LAN, looks up vendor names from MAC addresses, and runs a port/OS scan per device — all accessible from a browser.

## Requirements

- Linux (uses ARP scanning via nmap)
- Python 3.10+
- Node.js 18+
- nmap

## Installation

### 1. Install nmap

**Fedora/RHEL:**
```bash
sudo dnf install -y nmap
```

**Debian/Ubuntu:**
```bash
sudo apt install -y nmap
```

### 2. Clone the repo

```bash
git clone https://github.com/StevenWFry/good-home-net-scanner.git
cd good-home-net-scanner
```

### 3. Set up the Python virtual environment

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

### 4. Install frontend dependencies

```bash
cd frontend && npm install && cd ..
```

## Running

### Development mode (two terminals)

**Terminal 1 — backend** (requires sudo for ARP scanning and OS detection):
```bash
./run.sh
```

**Terminal 2 — frontend dev server** (proxies `/api` and `/ws` to the backend):
```bash
cd frontend && npm run dev
```

Then open [http://localhost:5173](http://localhost:5173).

### Production mode (single process)

Build the frontend once, then the backend serves everything:

```bash
cd frontend && npm run build && cd ..
./run.sh
```

Then open [http://localhost:8000](http://localhost:8000).

## Why does it need sudo?

nmap requires raw socket access to perform ARP host discovery and OS fingerprinting. `run.sh` handles this automatically. If you prefer not to run the whole process as root, you can grant nmap the needed capabilities instead:

```bash
sudo setcap cap_net_raw,cap_net_admin+eip $(which nmap)
```

After that you can run `./run.sh` without sudo (remove the `sudo -E` from the script).

## Data

Device info is stored in a SQLite database (`scanner.db`) created in the project directory. You can move it by setting the `DB_PATH` environment variable.
