"""MAC address → vendor name lookup using local OUI database."""
from __future__ import annotations

import asyncio
from mac_vendor_lookup import MacLookup, InvalidMacError

_lookup = MacLookup().async_lookup
_loaded = False


async def _ensure_loaded() -> None:
    global _loaded
    if _loaded:
        return
    await _lookup.load_vendors()
    _loaded = True


async def get_vendor(mac: str | None) -> str | None:
    if not mac:
        return None
    await _ensure_loaded()
    try:
        return await _lookup.lookup(mac)
    except (InvalidMacError, KeyError, Exception):
        return None
