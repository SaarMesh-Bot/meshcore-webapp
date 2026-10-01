# Meshcore Webapp by SaarMesh.de

Browser-App für **MeshCore-Companions** per **USB** (Web Serial), **Bluetooth LE** oder **TCP/WiFi**. Eine einzige HTML-Datei, keine Installation, kein Server – nur für TCP/WiFi wird zusätzlich die kleine [TCP-Bridge](#tcp--wifi-companions) benötigt.

**Live:** https://saarmesh-bot.github.io/meshcore-webapp/

## Funktionen

- **Live-Traffic** – alle empfangenen Pakete mit Typ, Route, Hop-Pfad (inkl. Pfad-Hash-Größe 1/2/3 Byte), SNR/RSSI, Region; Filter, Detailansicht mit Rohdaten, CSV/JSON-Export, Pakete/Minute
- **Chat** – Kanäle und Direktnachrichten, Zustellbestätigung mit Laufzeit, erneut senden, Antworten per `@[Name]`, Direktnachricht an Absender
- **Regionen** – Standard-Region des Geräts, Region **pro Kanal**, Anzeige der Region und Hash-Größe bei empfangenen Nachrichten
- **Karte** – alle Companions, Repeater, Room-Server und Sensoren mit Standort aus Adverts, Nachbar-Linien nach SNR, Paketpfad auf der Karte, eigene Position per Klick
- **Verbindung** – USB, Bluetooth LE oder TCP/WiFi (über die TCP-Bridge)
- **Adverts** – Zero-Hop und Flood
- **Kontakte** – speichern, löschen, teilen, Pfad zurücksetzen, Entfernung
- **Gerät** – Name, Position, TX-Leistung, Pfad-Hash-Größe, Batterie, Rauschpegel, Airtime, Paketstatistik, Neustart, Protokoll-Log

## Nutzung

1. Companion mit Firmware **„Companion USB“** (oder BLE) flashen.
2. Seite in **Chrome, Edge oder Opera** (Desktop) öffnen – entweder die Live-Version oben, lokal `index.html` oder über einen lokalen Server:
   ```
   python -m http.server 8000
   ```
   → `http://localhost:8000`
3. **„USB verbinden“**, **„BLE“** oder **„TCP/WiFi“** klicken und das Gerät wählen.

Firefox und Safari unterstützen Web Serial / Web Bluetooth nicht – TCP/WiFi über die Bridge funktioniert dort trotzdem.

## TCP / WiFi-Companions

Browser dürfen keine direkten TCP-Verbindungen öffnen. Für Companions mit **WiFi-Firmware** gibt es deshalb die **MeshCore TCP-Bridge** – ein kleines Programm ohne Installation, das auf dem eigenen PC läuft:

```
Webapp ──WebSocket──► TCP-Bridge (localhost:8765) ──TCP──► WiFi-Companion
```

1. Passende Datei unter **[Releases](https://github.com/SaarMesh-Bot/meshcore-webapp/releases/latest)** herunterladen:
   | System | Datei |
   |---|---|
   | Windows | `meshcore-tcp-bridge-windows-x64.exe` |
   | Mac (Apple Silicon / Intel) | `meshcore-tcp-bridge-macos-apple-silicon` / `…-macos-intel` |
   | Linux / Raspberry Pi | `…-linux-x64`, `…-linux-arm64`, `…-linux-armv7` |
2. Starten und das Fenster offen lassen.
   - **Windows:** Doppelklick. Erscheint „Windows hat den PC geschützt“: *Weitere Informationen → Trotzdem ausführen* (die Datei ist nicht kostenpflichtig signiert).
   - **macOS:** Im Terminal `chmod +x meshcore-tcp-bridge-macos-*` und `xattr -d com.apple.quarantine meshcore-tcp-bridge-macos-*`, dann `./meshcore-tcp-bridge-macos-…` starten.
   - **Linux:** `chmod +x meshcore-tcp-bridge-linux-*` und starten.
3. In der Webapp auf **„TCP/WiFi“** klicken, IP-Adresse und Port (Standard `5000`) des Companions eintragen.
4. Fragt der Browser nach Zugriff auf Geräte im lokalen Netzwerk: **Zulassen**.

**Sicherheit:** Die Bridge lauscht nur auf `127.0.0.1`, akzeptiert nur die offizielle Webapp (bzw. lokal geöffnete Dateien und `localhost`) und verbindet standardmäßig nur zu Adressen im lokalen Netz auf Port 5000. Ein Companion erlaubt immer nur eine Verbindung gleichzeitig.

Optionen (`meshcore-tcp-bridge -h`):

| Option | Bedeutung |
|---|---|
| `-ports 5000,5001` | weitere Ziel-Ports erlauben (`*` = alle) |
| `-listen 127.0.0.1:8765` | Adresse/Port der Bridge |
| `-allow-origin https://…` | eigene Webseite mit der Webapp zulassen |
| `-any-host` | auch Ziele außerhalb des lokalen Netzes erlauben |

Selbst bauen: `cd bridge && go build .` (Go ≥ 1.24).

Gehörte Knoten, Chatverläufe und Kanal-Regionen werden nur lokal im Browser gespeichert.

## Technik

- Reines HTML/CSS/JavaScript, [Leaflet](https://leafletjs.com/) für die Karte
- TCP-Bridge in Go ([coder/websocket](https://github.com/coder/websocket)), Builds per GitHub Actions
- Kartenkacheln: Esri (ohne API-Key); OSM/OpenTopoMap zusätzlich, wenn über http(s) ausgeliefert
- Companion-Protokoll gemäß [MeshCore companion_radio](https://github.com/meshcore-dev/MeshCore/tree/main/examples/companion_radio)

## Lizenz

MIT – siehe [LICENSE](LICENSE).

---
[SaarMesh.de](https://saarmesh.de) – MeshCore-Netz für die Region SaarLorLux
