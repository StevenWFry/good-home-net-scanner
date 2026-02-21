"""Per-device port scanning, service detection, and OS fingerprinting."""
from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Callable

import nmap


@dataclass
class PortInfo:
    port: int
    protocol: str
    service: str | None
    version: str | None
    state: str


@dataclass
class ScanResult:
    ip: str
    os: str | None
    ports: list[PortInfo] = field(default_factory=list)


def _infer_icon(vendor: str | None, hostname: str | None, ports: list[PortInfo]) -> str:
    """Heuristic icon type from vendor name, hostname, and open ports."""
    vendor_l = (vendor or "").lower()
    hostname_l = (hostname or "").lower()
    open_ports = {p.port for p in ports if p.state == "open"}

    # Router / gateway heuristics
    if any(k in vendor_l for k in ("cisco", "netgear", "ubiquiti", "asus", "tp-link", "linksys", "zyxel", "dlink", "d-link")):
        return "router"
    if any(k in hostname_l for k in ("router", "gateway", "gw", "fw", "firewall")):
        return "router"
    if {80, 443, 8080} & open_ports and 22 not in open_ports:
        if any(k in vendor_l for k in ("router", "modem")):
            return "router"

    # Apple devices
    if "apple" in vendor_l:
        if any(k in hostname_l for k in ("iphone", "ipad")):
            return "phone"
        if any(k in hostname_l for k in ("macbook", "imac", "mac")):
            return "laptop"
        return "laptop"

    # Phone / tablet
    if any(k in vendor_l for k in ("samsung", "huawei", "xiaomi", "oneplus", "google", "motorola")):
        return "phone"
    if any(k in hostname_l for k in ("phone", "android", "iphone", "ipad", "tablet")):
        return "phone"

    # TV / media
    if any(k in vendor_l for k in ("roku", "amazon", "nvidia", "sonos", "logitech media")):
        return "tv"
    if any(k in hostname_l for k in ("tv", "firetv", "appletv", "chromecast", "shield", "roku", "kodi")):
        return "tv"
    if 8008 in open_ports or 8009 in open_ports:  # Chromecast
        return "tv"

    # Printer
    if any(k in vendor_l for k in ("hp", "epson", "canon", "brother", "xerox", "lexmark", "ricoh")):
        return "printer"
    if any(k in hostname_l for k in ("printer", "print")):
        return "printer"
    if 9100 in open_ports or 631 in open_ports:  # IPP / JetDirect
        return "printer"

    # Server / NAS
    if 22 in open_ports and (80 in open_ports or 443 in open_ports):
        return "server"
    if any(k in hostname_l for k in ("server", "nas", "synology", "qnap", "pi", "raspberry")):
        return "server"

    # Laptop / PC
    if any(k in vendor_l for k in ("intel", "realtek", "dell", "lenovo", "hewlett")):
        return "laptop"

    return "device"


async def scan_device(
    ip: str,
    progress_cb: Callable | None = None,
) -> ScanResult:
    """Run nmap -sV --top-ports 100 -O against a single IP."""
    loop = asyncio.get_running_loop()

    def _scan() -> ScanResult:
        nm = nmap.PortScanner()
        try:
            nm.scan(hosts=ip, arguments="-sV --top-ports 100 -O -T4 --host-timeout 60s")
        except Exception as exc:
            return ScanResult(ip=ip, os=None, ports=[])

        if ip not in nm.all_hosts():
            return ScanResult(ip=ip, os=None, ports=[])

        host = nm[ip]
        ports: list[PortInfo] = []
        for proto in host.all_protocols():
            for port_num, pdata in host[proto].items():
                ports.append(
                    PortInfo(
                        port=port_num,
                        protocol=proto,
                        service=pdata.get("name") or None,
                        version=(pdata.get("version") or "") + " " + (pdata.get("product") or ""),
                        state=pdata.get("state", "open"),
                    )
                )

        # OS detection
        os_name: str | None = None
        if "osmatch" in host and host["osmatch"]:
            os_name = host["osmatch"][0].get("name")

        if progress_cb:
            progress_cb("portscan", 1, 1, ip)

        return ScanResult(ip=ip, os=os_name, ports=ports)

    return await loop.run_in_executor(None, _scan)
