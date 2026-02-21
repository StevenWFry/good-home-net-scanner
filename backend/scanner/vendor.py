"""MAC address → vendor name lookup using local OUI database."""
from __future__ import annotations

import asyncio
from mac_vendor_lookup import MacLookup, InvalidMacError

_mac_lookup: MacLookup | None = None
_loaded = False


async def _ensure_loaded() -> None:
    global _mac_lookup, _loaded
    if _loaded:
        return
    loop = asyncio.get_running_loop()
    _mac_lookup = MacLookup()
    # load_all() is blocking — run in thread pool
    await loop.run_in_executor(None, _mac_lookup.load_all)
    _loaded = True


async def get_vendor(mac: str | None) -> str | None:
    if not mac:
        return None
    await _ensure_loaded()
    assert _mac_lookup is not None
    try:
        return await asyncio.get_running_loop().run_in_executor(
            None, _mac_lookup.lookup, mac
        )
    except (InvalidMacError, KeyError, Exception):
        return None
