# Meshcore Webapp by SaarMesh.de

Browser-App für **MeshCore-Companions** per **USB** (Web Serial), **Bluetooth LE** oder **TCP/WiFi**. Eine einzige HTML-Datei, keine Installation, kein Server – nur für TCP/WiFi wird zusätzlich die kleine [TCP-Bridge](#tcp--wifi-companions) benötigt.

**Live:** https://saarmesh-bot.github.io/meshcore-webapp/

[![Unterstützen auf Ko-fi](https://img.shields.io/badge/Ko--fi-SaarMesh_unterst%C3%BCtzen-FF5E5B?logo=ko-fi&logoColor=white)](https://ko-fi.com/saarmesh)

## Funktionen

- **Live-Traffic** – alle empfangenen Pakete mit Typ, Route, Hop-Pfad (inkl. Pfad-Hash-Größe 1/2/3 Byte), SNR/RSSI, Region; Filter, Detailansicht mit Rohdaten, CSV/JSON-Export, Pakete/Minute
- **Chat** – Kanäle und Direktnachrichten, Zustellbestätigung mit Laufzeit, erneut senden, Antworten per `@[Name]`, Direktnachricht an Absender
- **Regionen** – Standard-Region des Geräts, Region **pro Kanal**, Anzeige der Region und Hash-Größe bei empfangenen Nachrichten
- **Öffentliches Verzeichnis** – erkennt öffentliche Kanäle und Regionsnamen im Live-Traffic, liest unbekannte öffentliche Kanäle mit („Entdeckt“), Kanäle mit einem Klick zum Gerät hinzufügen
- **Karte** – alle Companions, Repeater, Room-Server und Sensoren mit Standort aus Adverts, Nachbar-Linien nach SNR, Paketpfad auf der Karte, eigene Position per Klick
- **Verbindung** – USB, Bluetooth LE oder TCP/WiFi (über die TCP-Bridge)
- **Adverts** – Zero-Hop und Flood
- **Kontakte** – speichern, löschen, teilen, Pfad zurücksetzen, Entfernung
- **Repeater-Admin** – Fernverwaltung von Repeatern und Room-Servern: Login mit Admin- oder Gast-Passwort, Status (Akku, Laufzeit, Uhr, Rauschen, Airtime, Paketzähler), Nachbarn mit SNR (auch auf der Karte), Zugriffsliste, Einstellungen als Formular, Uhr synchronisieren, Adverts, Neustart und ein Terminal für alle CLI-Befehle
- **Telemetrie** – von Repeatern, Sensoren, Kontakten und dem eigenen Gerät (Spannung, Temperatur, Luftfeuchte, Luftdruck, GPS u. a.), Verlauf mit Diagrammen und CSV-Export, optional automatisch in großen Abständen, Freigaben für die eigene Telemetrie
- **Netz-Tools** – Trace-Route mit SNR pro Strecke (auch auf der Karte), Repeater in der Nähe per Zero-Hop-Suche mit SNR hin/zurück
- **Mobil** – eigene Handy-Ansicht mit Reiterleiste unten; auf Android per Bluetooth oder TCP/WiFi, auf iOS per TCP/WiFi
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

> **Wo stelle ich die Adresse meiner Node ein?** In der **Webapp**, nicht in der Bridge. Die Bridge braucht keine Einstellungen – sie reicht nur die Verbindung durch. IP-Adresse und Port gibst du im Dialog „TCP/WiFi“ an; die Webapp merkt sich die Angaben.
>
> **IP-Adresse herausfinden:** in der Geräteliste deines Routers (z. B. FritzBox: *Heimnetz → Netzwerk*) oder – bei Geräten mit Display – direkt auf der Node. Am besten der Node im Router eine feste IP geben.
>
> **Voraussetzungen:** Auf der Node läuft die **WiFi-Companion-Firmware**, Node und PC sind im selben Netz. Die Bridge erlaubt ab v1.0.2 die Ports **5000–5005**. Nutzt die Node einen anderen Port, die Bridge mit `-ports <port>` starten (Windows: `meshcore-tcp-bridge-windows-x64.exe -ports 5000-5005,6000`).

**Sicherheit:** Die Bridge lauscht nur auf `127.0.0.1`, akzeptiert nur die offizielle Webapp (bzw. lokal geöffnete Dateien und `localhost`) und verbindet standardmäßig nur zu Adressen im lokalen Netz auf den Ports 5000–5005. Ein Companion erlaubt immer nur eine Verbindung gleichzeitig.

Optionen (`meshcore-tcp-bridge -h`):

| Option | Bedeutung |
|---|---|
| `-ports 5000-5005` | erlaubte Ziel-Ports, einzeln oder als Bereich, komma-getrennt (`*` = alle) |
| `-listen 127.0.0.1:8765` | Adresse/Port der Bridge |
| `-allow-origin https://…` | eigene Webseite mit der Webapp zulassen |
| `-any-host` | auch Ziele außerhalb des lokalen Netzes erlauben |

### Mehrere Apps gleichzeitig (meshcore-tcp-mux)

Ein Companion erlaubt nur eine TCP-Verbindung. Sollen Webapp, Handy-App und andere Clients gleichzeitig verbunden sein, hilft der [meshcore-tcp-mux](https://github.com/compumike/meshcore-tcp-mux). Er verbindet sich als einziger mit der Node und verteilt die Verbindung an mehrere Clients.

- In der Webapp unter **„TCP/WiFi“** die **IP des Rechners mit dem Mux** und einen **Port des Mux** eintragen, nicht IP und Port der Node.
- **Empfohlen:** ein eigener Port nur für die Webapp, z. B. `5003` (im Mux `--listen-dedicated-client-port 5003`). Dann hält der Mux Nachrichten vor, die eingehen, während die Webapp geschlossen ist.
- Alternativ der gemeinsame Port `5001`. Dort kommen nur Nachrichten an, solange die Webapp verbunden ist.
- Die Mux-Ports liegen im Standardbereich 5000–5005 der Bridge, `-ports` ist also nicht nötig. Läuft der Mux außerhalb des lokalen Netzes (z. B. über Tailscale), die Bridge mit `-any-host` starten.

Der Mux verteilt Live-Traffic und Adverts an alle Clients und setzt die Region pro Kanal nur für die eigene Nachricht. Einstellungen wie Name, Kanäle und Standard-Region gelten aber für alle Clients gemeinsam.

Selbst bauen: `cd bridge && go build .` (Go ≥ 1.24).

Gehörte Knoten, Chatverläufe und Kanal-Regionen werden nur lokal im Browser gespeichert.

## Öffentliches Verzeichnis

Die Webapp kann öffentliche Kanäle und Regionen erkennen, ähnlich wie die App KiekR:

- **Kanäle:** Für jedes empfangene Kanalpaket (`GRP_TXT`) werden die eigenen Kanäle und die öffentlich bekannten Kanäle durchprobiert. Passt der Schlüssel (HMAC-Prüfung), wird die Nachricht entschlüsselt und angezeigt. Unbekannte öffentliche Kanäle erscheinen im Chat unter **„Entdeckt · nur mitlesen“** und lassen sich mit einem Klick zum Gerät hinzufügen.
- **Regionen:** Region-Codes (`T-FLOOD`) werden erst gegen die eigenen Regionen und dann gegen alle bekannten Regionsnamen geprüft. Treffer aus dem Verzeichnis sind mit **≈** markiert – Region-Codes sind nur 16 Bit lang, bei rund 2000 Namen kann ein Treffer zufällig falsch sein.
- **Kanal hinzufügen:** Im Chat über **＋** – Namen aus dem Verzeichnis werden vorgeschlagen, Hashtag-Kanäle (`#name`) brauchen keinen Schlüssel.

Die Daten stammen vom [EU MeshCore Analyzer](https://meshcore-analyzer.eu) und werden täglich per GitHub Actions als `catalog.json` ins Repo übernommen (`tools/build_catalog.py`). Die Webapp lädt nur diese Datei herunter – es werden keine Daten hochgeladen. Abschaltbar unter *Gerät → Öffentliches Verzeichnis*.

## Technik

- Reines HTML/CSS/JavaScript, [Leaflet](https://leafletjs.com/) für die Karte
- TCP-Bridge in Go ([coder/websocket](https://github.com/coder/websocket)), Builds per GitHub Actions
- Kartenkacheln: Esri (ohne API-Key); OSM/OpenTopoMap zusätzlich, wenn über http(s) ausgeliefert
- Companion-Protokoll gemäß [MeshCore companion_radio](https://github.com/meshcore-dev/MeshCore/tree/main/examples/companion_radio)

## SaarMesh unterstützen ☕

Die Webapp ist kostenlos und quelloffen. Sie entsteht im Umfeld von **[SaarMesh](https://saarmesh.de)**, dem MeshCore-Netz für die Region SaarLorLux – mit Repeatern, Live-Karte ([live.saarmesh.de](https://live.saarmesh.de)), Bot und Server, die privat betrieben werden.

Wenn dir die Webapp hilft und du das Projekt unterstützen möchtest (Hardware, Repeater-Standorte, Serverkosten), freuen wir uns über einen Kaffee:

**[☕ ko-fi.com/saarmesh](https://ko-fi.com/saarmesh)**

Genauso willkommen: Fehler melden, Ideen einbringen oder einen eigenen Repeater ins Netz stellen.

## Lizenz

MIT – siehe [LICENSE](LICENSE).

---
[SaarMesh.de](https://saarmesh.de) – MeshCore-Netz für die Region SaarLorLux
