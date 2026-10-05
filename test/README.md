# Tests

Die Tests laufen mit [Playwright](https://playwright.dev/python/) in Chromium gegen eine **simulierte MeshCore-Companion** (`sim.js`). Der Simulator ersetzt die TCP-Bridge durch einen Fake-WebSocket und beantwortet die Companion-Befehle (Kontakte, Kanäle, Login, Status, CLI, Telemetrie, Trace, Discovery, anonyme Anfragen, Regionen …). Es wird also keine Hardware gebraucht.

```bash
pip install playwright && python -m playwright install chromium
cd test && npm install          # Leaflet und QR-Bibliotheken lokal für die Tests
./run_tests.sh                  # Hauptversion
MCW_PAGE=beta/index.html ./run_tests.sh   # Beta
```

Bei jedem Push prüft die GitHub Action `Tests` beide Versionen und die TCP-Bridge (`go test`).
