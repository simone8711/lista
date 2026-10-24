#!/usr/bin/env python3
"""Corregge i tvg-id di lista_ita2.m3u nel namespace epg.lat e aggiorna
l'x-tvg-url. Idempotente: rigira quante volte vuoi, tocca solo cio' che
non va. I generalisti (Rai/Mediaset/La7...) hanno gia' ID coincidenti:
li lasciamo in pace. Mappa: canali sportivi + le poche correzioni."""


import re
from pathlib import Path

M3U = Path("lista_ita2.m3u")

MAPPING = {
    # Sky Sport (vavoo + Daddy + NTV)
    "Sky Sport 24": "Sky.Sport.24.it",
    "Sky Sport 24 Daddy": "Sky.Sport.24.it",
    "Sky Sport 24 NTV": "Sky.Sport.24.it",
    "Sky Sport Uno": "Sky.Sport.Uno.it",
    "Sky Sport Uno Daddy": "Sky.Sport.Uno.it",
    "Sky Sport Uno NTV": "Sky.Sport.Uno.it",
    "Sky Sport Calcio": "Sky.Sport.Calcio.it",
    "Sky Sport Calcio Daddy": "Sky.Sport.Calcio.it",
    "Sky Sport Calcio NTV": "Sky.Sport.Calcio.it",
    "Sky Sport Tennis": "Sky.Sport.Tennis.it",
    "Sky Sport Tennis Daddy": "Sky.Sport.Tennis.it",
    "Sky Sport Tennis NTV": "Sky.Sport.Tennis.it",
    "Sky Sport Arena": "Sky.Sport.Arena.it",
    "Sky Sport Arena Daddy": "Sky.Sport.Arena.it",
    "Sky Sport Arena NTV": "Sky.Sport.Arena.it",
    "Sky Sport Basket": "Sky.Sport.NBA.it",
    "Sky Sport Basket Daddy": "Sky.Sport.NBA.it",
    "Sky Sport Basket NTV": "Sky.Sport.NBA.it",
    "Sky Sport Max": "Sky.Sport.Max.it",
    "Sky Sport Max Daddy": "Sky.Sport.Max.it",
    "Sky Sport Max NTV": "Sky.Sport.Max.it",
    "Sky Sport F1": "Sky.Sport.F1.it",
    "Sky Sport F1 Daddy": "Sky.Sport.F1.it",
    "Sky Sport F1 NTV": "Sky.Sport.F1.it",
    "Sky Sport MotoGP": "Sky.Sport.MotoGP.it",
    "Sky Sport MotoGP Daddy": "Sky.Sport.MotoGP.it",
    "Sky Sport MotoGP NTV": "Sky.Sport.MotoGP.it",
    "Sky Sport Golf": "Sky.Sport.Golf.it",
    "Sky Sport Golf Daddy": "Sky.Sport.Golf.it",
    "Sky Sport Golf NTV": "Sky.Sport.Golf.it",
    "Sky Sport Serie A": "Sky.Sport.Calcio.it",
    # DAZN
    "DAZN 1": "DAZN.1.it.it",
    "DAZN 1 Daddy": "DAZN.1.it.it",
    "Dazn": "DAZN.1.it.it",
    "Dazn 2": "DAZN.2.it.it",
    # Eurosport
    "Eurosport 1": "Eurosport.Italia.it",
    "Eurosport 1 Daddy": "Eurosport.Italia.it",
    "Eurosport 1 NTV": "Eurosport.Italia.it",
    "Eurosport 2": "Eurosport.2.Italia.it",
    "Eurosport 2 Daddy": "Eurosport.2.Italia.it",
    "Eurosport 2 NTV": "Eurosport.2.Italia.it",
    # Sky Calcio / altri
    "Sky Calcio 251 Daddy": "Sky.Sport..251.it",
    "Sky Calcio 251 NTV": "Sky.Sport..251.it",
    "Sky Calcio 252 Daddy": "Sky.Sport..252.it",
    "Sky Calcio 252 NTV": "Sky.Sport..252.it",
    "Sky Calcio 253 Daddy": "Sky.Sport..253.it",
    "Sky Calcio 253 NTV": "Sky.Sport..253.it",
    "Sky TG24": "Sky.TG24.it",
    # correzioni generalisti
    "SuperTennis": "SuperTennis.HD.it",
    "27 Twentyseven": "27.Twentyseven.it",
    "27": "27.Twentyseven.it",
}

XTVG = '#EXTM3U x-tvg-url="https://raw.githubusercontent.com/simone8711/epg/main/epg.xml.gz"'


def main():
    text = M3U.read_text(encoding="utf-8")
    lines = text.split("\n")
    fixed = 0

    # header: forza x-tvg-url epg.lat
    for i, ln in enumerate(lines):
        if ln.startswith("#EXTM3U"):
            lines[i] = XTVG
            break

    for i, ln in enumerate(lines):
        if not ln.startswith("#EXTINF"):
            continue
        m = re.search(r'tvg-name="([^"]+)"', ln)
        if not m:
            continue
        name = m.group(1)
        new_id = MAPPING.get(name)
        if not new_id:
            continue
        if f'tvg-id="{new_id}"' in ln:
            continue
        if 'tvg-id="' in ln:
            lines[i] = re.sub(r'tvg-id="[^"]*"', f'tvg-id="{new_id}"', ln, count=1)
        else:
            lines[i] = ln.replace("#EXTINF:-1 ", f'#EXTINF:-1 tvg-id="{new_id}" ', 1)
        fixed += 1

    M3U.write_text("\n".join(lines), encoding="utf-8")
    print(f"tvg-id corretti: {fixed} | x-tvg-url: epg.lat")


if __name__ == "__main__":
    main()
