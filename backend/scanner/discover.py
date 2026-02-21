"""ARP + ICMP ping sweep to discover live hosts on the local network."""
from __future__ import annotations

import asyncio
import re
import subprocess
from dataclasses import dataclass, field
from typing import AsyncIterator

import nmap


@dataclass
class DiscoveredHost:
    ip: str
    mac: str | None = None
    hostname: str | None = None


def _detect_subnet() -> str:
    """Auto-detect local subnet from 'ip route'."""
    try:
        out = subprocess.check_output(["ip", "route"], text=True)
        for line in out.splitlines():
            # Look for lines like: 192.168.1.0/24 dev eth0 proto kernel ...
            m = re.search(r"(\d+\.\d+\.\d+\.\d+/\d+)\s+dev\s+\w+\s+proto kernel", line)
            if m:
                subnet = m.group(1)
                # Skip loopback-style tiny subnets
                if not subnet.startswith("127."):
                    return subnet
    except Exception:
        pass
    return "192.168.1.0/24"


async def discover_hosts(
    subnet: str | None = None,
    progress_cb=None,
) -> list[DiscoveredHost]:
    """Run nmap -sn ARP sweep; return list of discovered hosts.

    progress_cb(phase, current, total, device_ip) is called for each host found.
    """
    target = subnet or _detect_subnet()
    loop = asyncio.get_running_loop()

    def _scan() -> list[DiscoveredHost]:
        nm = nmap.PortScanner()
        nm.scan(hosts=target, arguments="-sn --send-ip -T4")
        results: list[DiscoveredHost] = []
        hosts = nm.all_hosts()
        total = len(hosts)
        for i, host in enumerate(hosts):
            host_data = nm[host]
            mac = None
            if "addresses" in host_data:
                mac = host_data["addresses"].get("mac")
            hostname = None
            if "hostnames" in host_data and host_data["hostnames"]:
                for h in host_data["hostnames"]:
                    if h.get("name"):
                        hostname = h["name"]
                        break
            results.append(DiscoveredHost(ip=host, mac=mac, hostname=hostname))
            if progress_cb:
                progress_cb("discover", i + 1, total or 1, host)
        return results

    return await loop.run_in_executor(None, _scan)
