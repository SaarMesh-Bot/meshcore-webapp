# Meshcore Webapp by SaarMesh.de

Browser-App für **MeshCore-Companions**, die per **USB** (Web Serial) oder **Bluetooth LE** am PC hängen. Eine einzige HTML-Datei, keine Installation, kein Server.

**Live:** https://saarmesh-bot.github.io/meshcore-webapp/

## Funktionen

- **Live-Traffic** – alle empfangenen Pakete mit Typ, Route, Hop-Pfad (inkl. Pfad-Hash-Größe 1/2/3 Byte), SNR/RSSI, Region; Filter, Detailansicht mit Rohdaten, CSV/JSON-Export, Pakete/Minute
- **Chat** – Kanäle und Direktnachrichten, Zustellbestätigung mit Laufzeit, erneut senden, Antworten per `@[Name]`, Direktnachricht an Absender
- **Regionen** – Standard-Region des Geräts, Region **pro Kanal**, Anzeige der Region und Hash-Größe bei empfangenen Nachrichten
- **Karte** – alle Companions, Repeater, Room-Server und Sensoren mit Standort aus Adverts, Nachbar-Linien nach SNR, Paketpfad auf der Karte, eigene Position per Klick
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
3. **„USB verbinden“** bzw. **„BLE“** klicken und das Gerät wählen.

Firefox und Safari unterstützen Web Serial / Web Bluetooth nicht.

Gehörte Knoten, Chatverläufe und Kanal-Regionen werden nur lokal im Browser gespeichert.

## Technik

- Reines HTML/CSS/JavaScript, [Leaflet](https://leafletjs.com/) für die Karte
- Kartenkacheln: Esri (ohne API-Key); OSM/OpenTopoMap zusätzlich, wenn über http(s) ausgeliefert
- Companion-Protokoll gemäß [MeshCore companion_radio](https://github.com/meshcore-dev/MeshCore/tree/main/examples/companion_radio)

## Lizenz

MIT – siehe [LICENSE](LICENSE).

---
[SaarMesh.de](https://saarmesh.de) – MeshCore-Netz für die Region SaarLorLux
