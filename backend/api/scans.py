"""Scan control endpoints."""
from __future__ import annotations

import asyncio
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..db.database import get_db
from ..db.models import Device, DeviceScanRecord, Port, ScanHistory

router = APIRouter(prefix="/api/scan", tags=["scan"])

# Shared scan state (single-process model is fine for a local tool)
_scan_state: dict[str, Any] = {
    "status": "idle",  # idle | running | done | error
    "phase": None,
    "current": 0,
    "total": 0,
    "device": None,
    "scan_id": None,
    "error": None,
}

# WebSocket broadcast function — injected at startup by main.py
_broadcast_fn = None


def set_broadcast(fn) -> None:
    global _broadcast_fn
    _broadcast_fn = fn


def get_scan_state() -> dict:
    return dict(_scan_state)


async def _broadcast(msg: dict) -> None:
    if _broadcast_fn:
        await _broadcast_fn(msg)


async def run_scan(subnet: str | None = None) -> None:
    """Full scan pipeline: discover → vendor → port scan."""
    from ..scanner.discover import discover_hosts
    from ..scanner.ports import scan_device, _infer_icon
    from ..scanner.vendor import get_vendor
    from ..db.database import SessionLocal

    db = SessionLocal()
    scan = ScanHistory(started_at=datetime.utcnow(), status="running")
    db.add(scan)
    db.commit()
    db.refresh(scan)

    _scan_state["status"] = "running"
    _scan_state["scan_id"] = scan.id
    _scan_state["error"] = None

    try:
        # Phase 1: Discovery
        _scan_state["phase"] = "discover"
        _scan_state["current"] = 0
        _scan_state["total"] = 0
        await _broadcast({**_scan_state, "message": "Starting network discovery..."})

        loop = asyncio.get_running_loop()

        def discover_progress(phase, current, total, device_ip):
            _scan_state["phase"] = phase
            _scan_state["current"] = current
            _scan_state["total"] = total
            _scan_state["device"] = device_ip
            asyncio.run_coroutine_threadsafe(_broadcast(dict(_scan_state)), loop)

        hosts = await discover_hosts(subnet=subnet, progress_cb=discover_progress)

        # Mark all devices offline first
        db.query(Device).update({"is_online": False})
        db.commit()

        total_hosts = len(hosts)

        # Phase 2: Vendor + device upsert
        _scan_state["phase"] = "vendor"
        _scan_state["total"] = total_hosts
        await _broadcast({**_scan_state, "message": f"Found {total_hosts} hosts, looking up vendors..."})

        for i, host in enumerate(hosts):
            vendor = await get_vendor(host.mac)
            _scan_state["current"] = i + 1
            _scan_state["device"] = host.ip
            await _broadcast({**_scan_state})

            device = db.query(Device).filter(Device.ip == host.ip).first()
            if device:
                device.mac = host.mac or device.mac
                device.hostname = host.hostname or device.hostname
                device.vendor = vendor or device.vendor
                device.is_online = True
                device.last_seen = datetime.utcnow()
            else:
                device = Device(
                    ip=host.ip,
                    mac=host.mac,
                    hostname=host.hostname,
                    vendor=vendor,
                    is_online=True,
                    first_seen=datetime.utcnow(),
                    last_seen=datetime.utcnow(),
                )
                db.add(device)
            db.commit()

        # Phase 3: Port scanning
        _scan_state["phase"] = "portscan"
        _scan_state["current"] = 0
        _scan_state["total"] = total_hosts
        await _broadcast({**_scan_state, "message": "Scanning ports..."})

        for i, host in enumerate(hosts):
            _scan_state["current"] = i + 1
            _scan_state["device"] = host.ip
            await _broadcast({**_scan_state})

            result = await scan_device(host.ip)

            device = db.query(Device).filter(Device.ip == host.ip).first()
            if not device:
                continue

            if result.os:
                device.os = result.os

            # Update ports: delete old, insert fresh
            db.query(Port).filter(Port.device_id == device.id).delete()
            for p in result.ports:
                if p.state == "open":
                    db.add(
                        Port(
                            device_id=device.id,
                            port=p.port,
                            protocol=p.protocol,
                            service=p.service,
                            version=p.version,
                            state=p.state,
                            last_seen=datetime.utcnow(),
                        )
                    )

            # Infer icon type
            device.icon_type = _infer_icon(device.vendor, device.hostname, result.ports)
            db.commit()

        # Write presence record for every known device
        all_devices = db.query(Device).all()
        now = datetime.utcnow()
        for device in all_devices:
            db.add(DeviceScanRecord(
                device_id=device.id,
                scan_id=scan.id,
                scanned_at=now,
                is_online=device.is_online,
            ))
        db.commit()

        devices_found = db.query(Device).filter(Device.is_online == True).count()
        scan.finished_at = datetime.utcnow()
        scan.devices_found = devices_found
        scan.status = "done"
        db.commit()

        _scan_state["status"] = "done"
        _scan_state["phase"] = "done"
        _scan_state["current"] = total_hosts
        _scan_state["total"] = total_hosts
        await _broadcast({**_scan_state, "message": f"Scan complete. {devices_found} devices online."})

    except Exception as exc:
        _scan_state["status"] = "error"
        _scan_state["error"] = str(exc)
        scan.status = "error"
        scan.error_msg = str(exc)
        scan.finished_at = datetime.utcnow()
        db.commit()
        await _broadcast({**_scan_state, "message": f"Scan error: {exc}"})
        raise
    finally:
        db.close()


@router.post("")
async def start_scan(db: Session = Depends(get_db)) -> dict:
    if _scan_state["status"] == "running":
        return {"status": "already_running"}
    # Fire and forget
    asyncio.create_task(run_scan())
    return {"status": "started"}


@router.get("/status")
def scan_status() -> dict:
    return get_scan_state()
