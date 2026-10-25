#!/usr/bin/env python3
"""Fonde le guide EPG in un unico XMLTV. Ordine = priorita': epg.lat ed
epgshare01 prima (le playlist usano i loro ID); le altre fonti riempiono
i buchi. Rytec incluso per l'ID ITFISH.it (Italian Fishing TV, come m3u4u)."""

import gzip
import re
import urllib.request
from pathlib import Path

SOURCES = [
    ("https://epg.lat/files/it.xml.gz", True),
    ("https://epgshare01.online/epgshare01/epg_ripper_IT1.xml.gz", False),
    ("https://epgshare01.online/epgshare01/epg_ripper_CH1.xml.gz", False),
    ([
        "https://www.open-epg.com/files/it.xml.gz",
        "https://www.open-epg.com/files/epg-it.xml.gz",
    ], False),
    ([
        "https://free-epg.de/api/epg/it.xml.gz",
    ], False),
    ([
        "https://free-epg.de/api/epg/rytec/it.xml.gz",
    ], False),
]

OUT_GZ = Path("epg.xml.gz")
OUT_CH = Path("channels.txt")


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
    raw = urllib.request.urlopen(req, timeout=180).read()
    try:
        return gzip.decompress(raw).decode("utf-8", "ignore")
    except OSError:
        return raw.decode("utf-8", "ignore")


def main():
    channels: list = []
    programmes: list = []
    names: list = []
    seen: set = set()

    def ingest(xml: str):
        n_ch = n_pg = 0
        for m in re.finditer(r'<channel\b[^>]*?\bid="([^"]+)"[^>]*>(.*?)</channel>', xml, re.S):
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
        print(f"  -> {n_ch} canali, {n_pg} programmi")

    for entry, _prio in SOURCES:
        urls = entry if isinstance(entry, list) else [entry]
        xml = None
        last_err = None
        for u in urls:
            try:
                xml = fetch(u)
                print(f"fonte OK: {u}")
                break
            except Exception as e:
                last_err = e
        if xml is None:
            print(f"WARN: fonte fallita ({last_err})")
            continue
        ingest(xml)

    head = ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<tv generator-info-name="simone8711/lista merge" '
            'generator-info-url="https://github.com/simone8711/lista">\n')
    body = head + "\n".join(channels) + "\n" + "\n".join(programmes) + "\n</tv>\n"
    OUT_GZ.write_bytes(gzip.compress(body.encode("utf-8"), compresslevel=6))
    OUT_CH.write_text("\n".join(sorted(names)) + "\n", encoding="utf-8")

    # ★ verifica finale: programmi presenti per i canali fishing
    for probe in ("ITFISH.it", "ItalianFishingTV.it"):
        n = len(re.findall(r'<programme[^>]*channel="' + re.escape(probe) + r'"', body))
        print(f"fishing {probe}: {n} programmi nel file")

    print(f"OK: epg.xml.gz = {OUT_GZ.stat().st_size // 1024} KB | "
          f"{len(channels)} canali, {len(programmes)} programmi")


if __name__ == "__main__":
    main()
    
