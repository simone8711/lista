#!/usr/bin/env python3
"""Fonde le guide EPG in un unico XMLTV: epg.lat (Italia Sky/DAZN/Eurosport)
+ epgshare01 IT (lacune italiane) + epgshare01 CH (RSI e svizzeri).
Su collisioni vince la fonte piu' in alto. Scrive anche channels.txt
(id|nome di tutti i canali) per completare le mappe tvg-id."""

import gzip
import re
import urllib.request
from pathlib import Path

SOURCES = [
    ("https://epg.lat/files/it.xml.gz", True),
    ("https://epgshare01.online/epgshare01/epg_ripper_IT1.xml.gz", False),
    ("https://epgshare01.online/epgshare01/epg_ripper_CH1.xml.gz", False),
]

OUT_GZ = Path("epg.xml.gz")
OUT_CH = Path("channels.txt")


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
    raw = urllib.request.urlopen(req, timeout=180).read()
    return gzip.decompress(raw).decode("utf-8", "ignore")


def main():
    channels: list = []
    programmes: list = []
    names: list = []
    seen: set = set()

    for url, _prio in SOURCES:
        try:
            xml = fetch(url)
        except Exception as e:
            print(f"WARN: {url} fallito: {e}")
            continue
        n_ch = n_pg = 0
        for m in re.finditer(r'<channel id="([^"]+)"[^>]*>(.*?)</channel>', xml, re.S):
            cid, body = m.group(1), m.group(0)
            if cid in seen:
                continue
            seen.add(cid)
            channels.append(body)
            nm = re.search(r'<display-name[^>]*>([^<]+)</display-name>', body)
            names.append(f"{cid} | {nm.group(1).strip() if nm else '?'}")
            n_ch += 1
        for m in re.finditer(r'(<programme\b[^>]*>.*?</programme>)', xml, re.S):
            block = m.group(1)
            cm = re.search(r'channel="([^"]+)"', block[:block.find(">") + 1])
            if not cm or cm.group(1) not in seen:
                continue
            programmes.append(block)
            n_pg += 1
        print(f"{url.split('/')[2]}{url[url.rfind('/'):]}: {n_ch} canali, {n_pg} programmi")

    head = ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<tv generator-info-name="simone8711/lista merge" '
            'generator-info-url="https://github.com/simone8711/lista">\n')
    body = head + "\n".join(channels) + "\n" + "\n".join(programmes) + "\n</tv>\n"

    OUT_GZ.write_bytes(gzip.compress(body.encode("utf-8"), compresslevel=6))
    OUT_CH.write_text("\n".join(sorted(names)) + "\n", encoding="utf-8")
    print(f"OK: epg.xml.gz = {OUT_GZ.stat().st_size // 1024} KB | "
          f"{len(channels)} canali, {len(programmes)} programmi | channels.txt aggiornato")


if __name__ == "__main__":
    main()
