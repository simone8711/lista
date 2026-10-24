#!/usr/bin/env python3
"""Fonde le guide EPG in un unico XMLTV: epg.lat (Italia, Sky/DAZN/Eurosport)
+ epgshare01 (riempie le lacune: Paramount, Sportitalia, TV locali).
Su collisioni vince epg.lat. Output: epg.xml + epg.xml.gz nel repo."""

import gzip
import re
import urllib.request
from pathlib import Path

SOURCES = [
    ("https://epg.lat/files/it.xml.gz", True),       # priorita'
    ("https://epgshare01.online/epgshare01/epg_ripper_IT1.xml.gz", False),
]

OUT_GZ = Path("epg.xml.gz")


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
    raw = urllib.request.urlopen(req, timeout=180).read()
    return gzip.decompress(raw).decode("utf-8", "ignore")


def main():
    channels: list = []
    programmes: list = []
    seen: set = set()
    stats = []

    for url, _prio in SOURCES:
        xml = fetch(url)
        n_ch = n_pg = 0
        for m in re.finditer(r'<channel id="([^"]+)"[^>]*>.*?</channel>', xml, re.S):
            cid, block = m.group(1), m.group(0)
            if cid in seen:
                continue
            seen.add(cid)
            channels.append(block)
            n_ch += 1
        for m in re.finditer(r'(<programme\b[^>]*>.*?</programme>)', xml, re.S):
            block = m.group(1)
            cm = re.search(r'channel="([^"]+)"', block[:block.find(">") + 1])
            if not cm or cm.group(1) not in seen:
                continue
            programmes.append(block)
            n_pg += 1
        stats.append(f"{url.split('/')[2]}: {n_ch} canali, {n_pg} programmi")
        print(" | ".join(stats[-1:]))

    head = ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<tv generator-info-name="simone8711/epg merge" '
            'generator-info-url="https://github.com/simone8711/epg">\n')
    body = head + "\n".join(channels) + "\n" + "\n".join(programmes) + "\n</tv>\n"

    OUT_GZ.write_bytes(gzip.compress(body.encode("utf-8"), compresslevel=6))
    print(f"OK: epg.xml.gz = {OUT_GZ.stat().st_size // 1024} KB | "
          f"totale {len(channels)} canali, {len(programmes)} programmi")


if __name__ == "__main__":
    main()
