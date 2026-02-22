"""Auto-scan schedule configuration — GET/PUT /api/schedule."""
from __future__ import annotations

import asyncio

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..db.database import get_db
from ..db.models import ScheduleConfig

_scheduler: AsyncIOScheduler | None = None
JOB_ID = "auto_scan"


def set_scheduler(s: AsyncIOScheduler) -> None:
    global _scheduler
    _scheduler = s


async def _scheduled_scan() -> None:
    from .scans import _scan_state, run_scan
    if _scan_state["status"] != "running":
        asyncio.create_task(run_scan())


def _apply_schedule(cfg: ScheduleConfig) -> None:
    if _scheduler is None:
        return
    if _scheduler.get_job(JOB_ID):
        _scheduler.remove_job(JOB_ID)
    if cfg.enabled:
        _scheduler.add_job(
            _scheduled_scan,
            "interval",
            minutes=cfg.interval_minutes,
            id=JOB_ID,
        )


def _cfg_response(cfg: ScheduleConfig) -> dict:
    job = _scheduler.get_job(JOB_ID) if _scheduler else None
    next_run = job.next_run_time.isoformat() if job else None
    return {
        "enabled": cfg.enabled,
        "interval_minutes": cfg.interval_minutes,
        "next_run_at": next_run,
    }


router = APIRouter(prefix="/api/schedule", tags=["schedule"])


class ScheduleBody(BaseModel):
    enabled: bool
    interval_minutes: int


@router.get("")
def get_schedule(db: Session = Depends(get_db)):
    cfg = db.query(ScheduleConfig).first()
    if not cfg:
        cfg = ScheduleConfig()
    return _cfg_response(cfg)


@router.put("")
def put_schedule(body: ScheduleBody, db: Session = Depends(get_db)):
    cfg = db.query(ScheduleConfig).first()
    if not cfg:
        cfg = ScheduleConfig(id=1)
        db.add(cfg)
    cfg.enabled = body.enabled
    cfg.interval_minutes = max(1, body.interval_minutes)
    db.commit()
    _apply_schedule(cfg)
    return _cfg_response(cfg)
