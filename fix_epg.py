#!/usr/bin/env python3
"""Corregge i tvg-id di lista_ita2.m3u e punta l'x-tvg-url all'EPG fuso.
Livelli: MAPPING esatto -> AUTO-MATCH fuzzy (soglia 0.65, suffissi HD/TV
rimossi) -> tvg-name di sistema ovunque manchi. Idempotente."""

import re
from pathlib import Path

M3U = Path("lista_ita2.m3u")
CH = Path("channels.txt")

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
    # DAZN / Eurosport
    "DAZN 1": "DAZN.1.it.it",
    "DAZN 1 Daddy": "DAZN.1.it.it",
    "Dazn": "DAZN.1.it.it",
    "Dazn 2": "DAZN.2.it.it",
    "Eurosport 1": "Eurosport.Italia.it",
    "Eurosport 1 Daddy": "Eurosport.Italia.it",
    "Eurosport 1 NTV": "Eurosport.Italia.it",
    "Eurosport 2": "Eurosport.2.Italia.it",
    "Eurosport 2 Daddy": "Eurosport.2.Italia.it",
    "Eurosport 2 NTV": "Eurosport.2.Italia.it",
    # Sky Calcio / Sky
    "Sky Calcio 251 Daddy": "Sky.Sport..251.it",
    "Sky Calcio 251 NTV": "Sky.Sport..251.it",
    "Sky Calcio 252 Daddy": "Sky.Sport..252.it",
    "Sky Calcio 252 NTV": "Sky.Sport..252.it",
    "Sky Calcio 253 Daddy": "Sky.Sport..253.it",
    "Sky Calcio 253 NTV": "Sky.Sport..253.it",
    "Sky TG24": "Sky.TG24.it",
    "Sky Meteo": "Sky.Meteo24.it",
    # RSI / svizzeri
    "RSI La 1": "RSI.La.1.ch",
    "RSI La 2": "RSI.LA.2.ch",
    # radio-TV e generalisti (ID verificati su epgshare01 IT1)
    "Radio 105": "Radio.105.it",
    "Radio 105 TV": "Radio.105.it",
    "RTL 102.5": "RTL.102.5.HD.it",
    "RTL 102.5 TV": "RTL.102.5.HD.it",
    "Deejay TV": "Deejay.TV.it",
    "R101": "R101tv.it",
    "R101 TV": "R101tv.it",
    "Radiofreccia": "RADIOFRECCIA.HD.it",
    "Radiofreccia TV": "RADIOFRECCIA.HD.it",
    "Virgin Radio": "Virgin.Radio.it",
    "Virgin Radio TV": "Virgin.Radio.it",
    "Radio Norba": "RADIONORBA.TV.it",
    "Radio Norba TV": "RADIONORBA.TV.it",
    "Radio Italia TV": "Radio.Italia.TV.HD.it",
    "Rai Radio 2": "RaiRadio2.it",
    "RMC": "RMC.it",
    "TG Norba 24": "TG.NORBA.24.it",
    "TRM h24": "TRM.h24.it",
    "San Marino RTV": "San.Marino.RTV.it",
    "Caccia e Pesca": "Caccia.e.PESCA.it",
    "Super!": "Super!.it",
    "Mediaset Extra": "Mediaset.Extra.it",
    "La 5": "La.5.it",
    "Italia 2": "Italia.2.it",
    "TGCOM 24": "TGCom.it",
    "La7d": "LA7D.it",
    "Cine34": "Cine34.it",
    "Giallo": "Giallo.TV.it",
    "Top Crime": "Top.Crime.it",
    "Motor Trend": "Motor.Trend.it",
    "MTV": "MTV.HD.it",
    "DMAX": "DMAX.it",
    "Warner TV": "Warner.TV.it",
    "Sportitalia": "Sportitalia.HD.it",
    "TV2000": "TV2000.ch",
    "Paramount+": "Paramount+.ch",
    "SuperTennis": "SuperTennis.HD.it",
    "27 Twentyseven": "27.Twentyseven.it",
    "27": "27.Twentyseven.it",
    # Italian Fishing TV: ID Rytec/iptv-epg.org (come su m3u4u)
    "Italian Fishing TV": "IT600001L6",    
}

XTVG = '#EXTM3U x-tvg-url="https://raw.githubusercontent.com/simone8711/lista/main/epg.xml.gz"'


def norm(s: str) -> str:
    s = s.lower().strip()
    s = re.sub(r"[^\w\s]", " ", s, flags=re.UNICODE)
    s = re.sub(r"\s+", " ", s).strip()
    s = re.sub(r"\b(hd|tv)$", "", s).strip()
    s = re.sub(r"\s+", " ", s).strip()
    return s


def display_name(line: str) -> str:
    return line.rsplit(",", 1)[-1].strip()


def load_epg_index():
    idx = {}
    if not CH.exists():
        return idx
    for ln in CH.read_text(encoding="utf-8").splitlines():
        if " | " not in ln:
            continue
        cid, name = ln.split(" | ", 1)
        idx[norm(name)] = (cid.strip(), name.strip())
    return idx


def auto_match(name: str, idx: dict):
    n = norm(name)
    if not n:
        return None
    if n in idx:
        return idx[n]
    words = set(n.split())
    best, best_score = None, 0.0
    for k, v in idx.items():
        kw = set(k.split())
        if not kw:
            continue
        score = len(words & kw) / max(len(words), len(kw))
        if score > best_score:
            best, best_score = v, score
    return best if best_score >= 0.65 else None


def main():
    text = M3U.read_text(encoding="utf-8")
    lines = text.split("\n")
    idx = load_epg_index()
    fixed = auto = 0
    uncovered = []

    for i, ln in enumerate(lines):
        if ln.startswith("#EXTM3U"):
            lines[i] = XTVG
            break

    for i, ln in enumerate(lines):
        if not ln.startswith("#EXTINF"):
            continue
        m = re.search(r'tvg-name="([^"]+)"', ln)
        name = m.group(1) if m else display_name(ln)
        hit = MAPPING.get(name) or None
        if hit:
            if f'tvg-id="{hit}"' not in ln:
                lines[i] = (re.sub(r'tvg-id="[^"]*"', f'tvg-id="{hit}"', ln, count=1)
                            if 'tvg-id="' in ln
                            else ln.replace("#EXTINF:-1 ", f'#EXTINF:-1 tvg-id="{hit}" ', 1))
                fixed += 1
            if 'tvg-name="' not in lines[i]:
                base = re.sub(r"\s+(NTV|Daddy)$", "", name)
                lines[i] = lines[i].replace("#EXTINF:-1 ", f'#EXTINF:-1 tvg-name="{base}" ', 1)
            continue
        am = auto_match(name, idx)
        if am:
            cid, disp = am
            new_ln = ln
            if 'tvg-id="' in new_ln:
                new_ln = re.sub(r'tvg-id="[^"]*"', f'tvg-id="{cid}"', new_ln, count=1)
            else:
                new_ln = new_ln.replace("#EXTINF:-1 ", f'#EXTINF:-1 tvg-id="{cid}" ', 1)
            if 'tvg-name="' in new_ln:
                new_ln = re.sub(r'tvg-name="[^"]*"', f'tvg-name="{disp}"', new_ln, count=1)
            else:
                new_ln = new_ln.replace("#EXTINF:-1 ", f'#EXTINF:-1 tvg-name="{disp}" ', 1)
            lines[i] = new_ln
            auto += 1
        else:
            uncovered.append(name)
            if 'tvg-name="' not in lines[i]:
                lines[i] = lines[i].replace("#EXTINF:-1 ", f'#EXTINF:-1 tvg-name="{name}" ', 1)

    M3U.write_text("\n".join(lines), encoding="utf-8")
    print(f"mappa: {fixed} | auto-match: {auto} | scoperti: {len(uncovered)}")
    for u in uncovered[:40]:
        print("  scoperto:", u)


if __name__ == "__main__":
    main()
    
