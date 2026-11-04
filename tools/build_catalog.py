#!/usr/bin/env python3
"""Baut catalog.json – öffentlich bekannte MeshCore-Kanäle und Regionen.

Quelle: live.saarmesh.de (CoreScope der SaarMesh-Community),
        https://live.saarmesh.de/verzeichnis/channels.json – stündlich aus den
        dort mitgehörten Paketen erzeugt, enthält nur Hashtag-Kanäle und Public.
Bis 22.10.2026 kam das Verzeichnis vom EU MeshCore Analyzer (meshcore-analyzer.eu);
der damalige Bestand bleibt als Grundstock erhalten und wird mit den aktuellen
Daten aus live.saarmesh.de zusammengeführt (Regionen vereinigt, Nachrichtenzahl
= Maximum), damit Nutzer außerhalb der Region nichts verlieren.

Die Webapp lädt das Verzeichnis aus dem Repo (täglich per GitHub Actions).

Format:
  channels: [{n: Name, s: Schlüssel-Hex (nur wenn nicht aus "#name" ableitbar),
              r: [gesehene Regionen], m: gesehene Nachrichten}]
  regions:  [alle bekannten Regionsnamen]
  stale:    {since, reason} – nur solange die Quelle nicht erreichbar ist; die
            Kanäle bleiben dann auf dem letzten Stand und die Webapp weist darauf hin.
"""
import datetime, hashlib, json, sys, urllib.error, urllib.request

SRC = "https://live.saarmesh.de/verzeichnis/channels.json"
SOURCE_PAGE = "https://live.saarmesh.de"


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "meshcore-webapp-catalog (+https://github.com/SaarMesh-Bot/meshcore-webapp)"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


def now():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load(out):
    try:
        with open(out, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def mark_stale(out, reason):
    """Quelle nicht erreichbar: alte Datei behalten, einmalig einen Vermerk setzen."""
    print(f"::warning::Verzeichnis-Quelle nicht erreichbar ({reason}) – alte catalog.json bleibt erhalten")
    old = load(out)
    if not old or not isinstance(old.get("channels"), list):
        sys.exit("Keine brauchbare alte catalog.json vorhanden")
    if old.get("stale") and old.get("source") == SOURCE_PAGE:
        print(f"Vermerk besteht schon seit {old['stale'].get('since')} – keine Änderung")
        return
    old["stale"] = {"since": now(), "reason": reason}
    old["source"] = SOURCE_PAGE
    with open(out, "w", encoding="utf-8") as f:
        json.dump(old, f, ensure_ascii=False, separators=(",", ":"))
    print("Vermerk 'stale' gesetzt")


def secret_of(e):
    """Schlüssel eines Eintrags (abgeleitet bei '#name' ohne 's')."""
    n = e.get("n") or ""
    if e.get("s"):
        return e["s"].lower()
    return hashlib.sha256(n.encode()).hexdigest()[:32] if n.startswith("#") else None


def norm(r):
    r = (r or "").strip().lower().lstrip("#")
    return r if r and r != "null" else None


def main(out):
    try:
        data = fetch(SRC)
    except urllib.error.HTTPError as e:
        return mark_stale(out, f"HTTP {e.code}")
    except (urllib.error.URLError, TimeoutError, ValueError) as e:
        return mark_stale(out, type(e).__name__)
    old = load(out) or {}
    chans, regions = {}, set()

    def add(e, fresh):
        name = (e.get("n") or "").strip()
        sec = secret_of(dict(e, n=name))
        if not name or not sec or len(sec) != 32:
            return
        rs = {x for x in map(norm, e.get("r") or []) if x}
        regions.update(rs)
        key = name.lower() + ":" + sec
        cur = chans.get(key)
        if cur is None:
            cur = chans[key] = {"n": name, "r": set(), "m": 0}
            derived = hashlib.sha256(name.encode()).hexdigest()[:32] if name.startswith("#") else None
            if derived != sec:
                cur["s"] = sec
        cur["r"] |= rs
        cur["m"] = max(cur["m"], int(e.get("m") or 0))

    for e in old.get("channels") or []:          # Grundstock (u. a. meshcore-analyzer.eu)
        add(e, False)
    n_new = 0
    for e in data.get("channels") or []:         # aktuell von live.saarmesh.de
        name = (e.get("n") or "").strip()
        if not (name.startswith("#") or e.get("s")):
            continue
        n_new += 1
        add(e, True)
    if n_new < 10:
        sys.exit(f"Quelle liefert nur {n_new} Kanäle – Abbruch, alte Datei bleibt erhalten")
    regions.update(x for x in map(norm, old.get("regions") or []) if x)
    regions.update(x for x in map(norm, data.get("regions") or []) if x)

    lst = []
    for c in chans.values():
        e = {"n": c["n"]}
        if c.get("s"):
            e["s"] = c["s"]
        if c["r"]:
            e["r"] = sorted(c["r"])
        e["m"] = c["m"]
        lst.append(e)
    lst.sort(key=lambda e: (-e["m"], e["n"]))
    cat = {
        "v": 1,
        "updated": now(),
        "source": SOURCE_PAGE,
        "channels": lst,
        "regions": sorted(regions),
    }
    if old:
        cmp = {k: v for k, v in old.items() if k != "updated"}
        if cmp == {k: v for k, v in cat.items() if k != "updated"}:
            print("Keine inhaltliche Änderung – Datei bleibt unverändert")
            return
    with open(out, "w", encoding="utf-8") as f:
        json.dump(cat, f, ensure_ascii=False, separators=(",", ":"))
    print(f"{len(lst)} Kanäle ({n_new} aktuell von live.saarmesh.de), {len(regions)} Regionen -> {out}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "catalog.json")
