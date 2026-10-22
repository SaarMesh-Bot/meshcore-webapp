#!/usr/bin/env python3
"""Baut catalog.json – öffentlich bekannte MeshCore-Kanäle und Regionen.

Quelle: EU MeshCore Analyzer (https://meshcore-analyzer.eu, /api/channels).
Die Webapp kann das Verzeichnis nicht direkt abfragen (kein CORS), daher wird
täglich per GitHub Actions eine kompakte Kopie im Repo abgelegt.

Format:
  channels: [{n: Name, s: Schlüssel-Hex (nur wenn nicht aus "#name" ableitbar),
              r: [im Verzeichnis gesehene Regionen], m: gesehene Nachrichten}]
  regions:  [alle bekannten Regionsnamen]
  stale:    {since, reason} – nur solange die Quelle nicht erreichbar ist; die
            Kanäle bleiben dann auf dem letzten Stand und die Webapp weist darauf hin.
"""
import datetime, hashlib, json, sys, urllib.error, urllib.request

SRC = "https://meshcore-analyzer.eu/api/channels"


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
    if old.get("stale"):
        print(f"Vermerk besteht schon seit {old['stale'].get('since')} – keine Änderung")
        return
    old["stale"] = {"since": now(), "reason": reason}
    with open(out, "w", encoding="utf-8") as f:
        json.dump(old, f, ensure_ascii=False, separators=(",", ":"))
    print("Vermerk 'stale' gesetzt")


def main(out):
    try:
        data = fetch(SRC)
    except urllib.error.HTTPError as e:
        return mark_stale(out, f"HTTP {e.code}")
    except (urllib.error.URLError, TimeoutError, ValueError) as e:
        return mark_stale(out, type(e).__name__)
    chans, regions = {}, set()
    for c in data.get("channels", []):
        name = (c.get("name") or "").strip()
        sec = (c.get("secretHex") or "").lower()
        if not name or len(sec) != 32 or c.get("encrypted"):
            continue
        scopes = sorted({s.strip().lower().lstrip("#") for s in (c.get("scopes") or []) if s and s.strip()})
        regions.update(scopes)
        entry = {"n": name}
        derived = hashlib.sha256(name.encode()).hexdigest()[:32] if name.startswith("#") else None
        if derived != sec:
            entry["s"] = sec
        if scopes:
            entry["r"] = scopes
        entry["m"] = int(c.get("messageCount") or 0)
        key = name.lower() + ":" + sec
        if key not in chans or chans[key]["m"] < entry["m"]:
            chans[key] = entry
    lst = sorted(chans.values(), key=lambda e: (-e["m"], e["n"]))
    if len(lst) < 10:
        sys.exit(f"Verzeichnis liefert nur {len(lst)} Kanäle – Abbruch, alte Datei bleibt erhalten")
    cat = {
        "v": 1,
        "updated": now(),
        "source": "https://meshcore-analyzer.eu",
        "channels": lst,
        "regions": sorted(regions),
    }
    old = load(out)
    if old is not None:
        old.pop("updated", None)
        if old == {k: v for k, v in cat.items() if k != "updated"}:
            print("Keine inhaltliche Änderung – Datei bleibt unverändert")
            return
    with open(out, "w", encoding="utf-8") as f:
        json.dump(cat, f, ensure_ascii=False, separators=(",", ":"))
    print(f"{len(lst)} Kanäle, {len(regions)} Regionen -> {out}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "catalog.json")
