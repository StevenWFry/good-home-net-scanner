"""Device REST endpoints."""
from __future__ import annotations

import json
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..db.database import get_db
from ..db.models import Device, DeviceScanRecord, Port

router = APIRouter(prefix="/api/devices", tags=["devices"])


class DeviceOut(BaseModel):
    id: int
    ip: str
    mac: str | None
    hostname: str | None
    vendor: str | None
    os: str | None
    nickname: str | None
    icon_type: str
    tags: list[str]
    first_seen: str
    last_seen: str
    is_online: bool
    ports: list[dict]

    model_config = {"from_attributes": True}


class DevicePatch(BaseModel):
    nickname: str | None = None
    tags: list[str] | None = None
    icon_type: str | None = None


def _device_to_dict(device: Device) -> dict:
    tags = []
    if device.tags:
        try:
            tags = json.loads(device.tags)
        except Exception:
            tags = []
    ports = [
        {
            "id": p.id,
            "port": p.port,
            "protocol": p.protocol,
            "service": p.service,
            "version": (p.version or "").strip() or None,
            "state": p.state,
            "last_seen": p.last_seen.isoformat() + "Z" if p.last_seen else None,
        }
        for p in sorted(device.ports, key=lambda x: x.port)
    ]
    return {
        "id": device.id,
        "ip": device.ip,
        "mac": device.mac,
        "hostname": device.hostname,
        "vendor": device.vendor,
        "os": device.os,
        "nickname": device.nickname,
        "icon_type": device.icon_type or "device",
        "tags": tags,
        "first_seen": device.first_seen.isoformat() + "Z" if device.first_seen else None,
        "last_seen": device.last_seen.isoformat() + "Z" if device.last_seen else None,
        "is_online": device.is_online,
        "ports": ports,
    }


@router.get("")
def list_devices(db: Session = Depends(get_db)) -> list[dict]:
    devices = db.query(Device).order_by(Device.ip).all()
    return [_device_to_dict(d) for d in devices]


@router.get("/{device_id}")
def get_device(device_id: int, db: Session = Depends(get_db)) -> dict:
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    return _device_to_dict(device)


def _record_to_dict(r: DeviceScanRecord) -> dict:
    return {
        "id": r.id,
        "scan_id": r.scan_id,
        "scanned_at": r.scanned_at.isoformat() + "Z" if r.scanned_at else None,
        "is_online": r.is_online,
    }


@router.get("/{device_id}/history")
def get_device_history(device_id: int, db: Session = Depends(get_db)) -> list[dict]:
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    records = (
        db.query(DeviceScanRecord)
        .filter(DeviceScanRecord.device_id == device_id)
        .order_by(DeviceScanRecord.scanned_at.desc())
        .limit(50)
        .all()
    )
    return [_record_to_dict(r) for r in records]


@router.patch("/{device_id}")
def patch_device(
    device_id: int, patch: DevicePatch, db: Session = Depends(get_db)
) -> dict:
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    if patch.nickname is not None:
        device.nickname = patch.nickname
    if patch.tags is not None:
        device.tags = json.dumps(patch.tags)
    if patch.icon_type is not None:
        device.icon_type = patch.icon_type

    db.commit()
    db.refresh(device)
    return _device_to_dict(device)
