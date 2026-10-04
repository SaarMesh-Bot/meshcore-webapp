// MeshCore TCP-Bridge – Meshcore Webapp by SaarMesh.de
//
// Browser können keine rohen TCP-Verbindungen öffnen. Diese kleine Brücke läuft
// auf dem eigenen PC, nimmt WebSocket-Verbindungen der Webapp an und reicht die
// Daten 1:1 per TCP an einen MeshCore-Companion mit WiFi-Firmware weiter.
//
//	Browser ──WebSocket──► Bridge (localhost) ──TCP──► WiFi-Companion
package main

import (
	"bufio"
	"context"
	"encoding/json"
	"errors"
	"flag"
	"fmt"
	"log"
	"net"
	"net/http"
	"net/url"
	"os"
	"strconv"
	"strings"
	"time"

	"github.com/coder/websocket"
)

var version = "dev"

const defaultOrigin = "https://saarmesh-bot.github.io"

var (
	listenAddr   = flag.String("listen", "127.0.0.1:8765", "Adresse, auf der die Bridge lauscht")
	allowedPorts = flag.String("ports", "5000-5005", "Erlaubte Ziel-Ports, komma-getrennt, auch Bereiche wie 5000-5005 (\"*\" = alle)")
	anyHost      = flag.Bool("any-host", false, "Auch öffentliche Ziel-Adressen erlauben (Standard: nur lokales Netz)")
	extraOrigins = flag.String("allow-origin", "", "Zusätzlich erlaubte Webseiten-Origins, komma-getrennt (z. B. https://meine-seite.de)")
	showVersion  = flag.Bool("version", false, "Version anzeigen")
)

func main() {
	flag.Parse()
	if *showVersion {
		fmt.Println("meshcore-tcp-bridge", version)
		return
	}
	log.SetFlags(log.Ltime)

	mux := http.NewServeMux()
	mux.HandleFunc("/", handleStatus)
	mux.HandleFunc("/info", handleInfo)
	mux.HandleFunc("/ws", handleWS)

	fmt.Println("==============================================")
	fmt.Println(" MeshCore TCP-Bridge", version)
	fmt.Println(" Meshcore Webapp by SaarMesh.de")
	fmt.Println("==============================================")
	fmt.Printf(" Lauscht auf:     ws://%s/ws\n", *listenAddr)
	fmt.Printf(" Erlaubte Ports:  %s\n", *allowedPorts)
	if *anyHost {
		fmt.Println(" Ziele:           alle Adressen (-any-host)")
	} else {
		fmt.Println(" Ziele:           nur lokales Netz")
	}
	fmt.Println()
	fmt.Println(" So geht's weiter:")
	fmt.Println("  1. Dieses Fenster offen lassen.")
	fmt.Println("  2. In der Webapp auf „TCP/WiFi“ klicken.")
	fmt.Println("  3. Dort IP-Adresse und Port deiner Node eintragen")
	fmt.Println("     (z. B. 192.168.178.50, Port 5000).")
	fmt.Println()
	fmt.Println(" Die Adresse der Node wird in der Webapp eingetragen,")
	fmt.Println(" nicht hier. Beenden mit Strg+C.")
	fmt.Println("==============================================")

	srv := &http.Server{Addr: *listenAddr, Handler: mux, ReadHeaderTimeout: 10 * time.Second}
	if err := srv.ListenAndServe(); err != nil {
		fmt.Println()
		fmt.Println("FEHLER:", err)
		if strings.Contains(err.Error(), "address already in use") || strings.Contains(err.Error(), "Only one usage") {
			fmt.Println("Die Bridge läuft vermutlich schon (oder ein anderes Programm nutzt den Port).")
		}
		waitForEnter()
		os.Exit(1)
	}
}

func waitForEnter() {
	fmt.Println("Enter drücken zum Beenden …")
	_, _ = bufio.NewReader(os.Stdin).ReadString('\n')
}

// ---------- HTTP-Endpunkte ----------

func handleStatus(w http.ResponseWriter, r *http.Request) {
	if r.URL.Path != "/" {
		http.NotFound(w, r)
		return
	}
	w.Header().Set("Content-Type", "text/html; charset=utf-8")
	fmt.Fprintf(w, `<!doctype html><meta charset="utf-8"><title>MeshCore TCP-Bridge</title>
<body style="font-family:system-ui;max-width:640px;margin:40px auto;padding:0 16px">
<h2>MeshCore TCP-Bridge läuft ✔</h2><p>Version %s</p>
<p>Öffne die <a href="%s/meshcore-webapp/">Meshcore Webapp by SaarMesh.de</a>, klicke auf <b>„TCP/WiFi“</b> und trage dort IP-Adresse und Port deiner Node ein.</p>
<p style="color:#666">Die Bridge selbst braucht keine Einstellungen – die Adresse der Node wird in der Webapp angegeben.</p></body>`,
		version, defaultOrigin)
}

func handleInfo(w http.ResponseWriter, r *http.Request) {
	setCORS(w, r)
	if r.Method == http.MethodOptions {
		w.WriteHeader(http.StatusNoContent)
		return
	}
	w.Header().Set("Content-Type", "application/json")
	_ = json.NewEncoder(w).Encode(map[string]string{"app": "meshcore-tcp-bridge", "version": version})
}

func setCORS(w http.ResponseWriter, r *http.Request) {
	if o := r.Header.Get("Origin"); originAllowed(o) && o != "" {
		w.Header().Set("Access-Control-Allow-Origin", o)
		w.Header().Set("Vary", "Origin")
		w.Header().Set("Access-Control-Allow-Private-Network", "true")
		w.Header().Set("Access-Control-Allow-Methods", "GET, OPTIONS")
	}
}

// ---------- WebSocket ↔ TCP ----------

type statusMsg struct {
	Type    string `json:"type"`
	Target  string `json:"target,omitempty"`
	Message string `json:"message,omitempty"`
	Version string `json:"version,omitempty"`
}

func handleWS(w http.ResponseWriter, r *http.Request) {
	origin := r.Header.Get("Origin")
	if !originAllowed(origin) {
		log.Printf("Abgelehnt: Webseite %q ist nicht erlaubt (siehe -allow-origin)", origin)
		http.Error(w, "origin not allowed", http.StatusForbidden)
		return
	}

	host := strings.TrimSpace(r.URL.Query().Get("host"))
	portStr := strings.TrimSpace(r.URL.Query().Get("port"))
	if portStr == "" {
		portStr = "5000"
	}

	// Origin wurde oben selbst geprüft (inkl. file:// = "null").
	c, err := websocket.Accept(w, r, &websocket.AcceptOptions{InsecureSkipVerify: true})
	if err != nil {
		log.Printf("WebSocket-Fehler: %v", err)
		return
	}
	c.SetReadLimit(1 << 16)
	ctx, cancel := context.WithCancel(r.Context())
	defer cancel()

	fail := func(msg string) {
		log.Printf("Fehler: %s", msg)
		sendStatus(ctx, c, statusMsg{Type: "error", Message: msg, Version: version})
		_ = c.Close(websocket.StatusPolicyViolation, truncate(msg, 120))
	}

	port, err := strconv.Atoi(portStr)
	if err != nil || port < 1 || port > 65535 {
		fail("Ungültiger Port: " + portStr)
		return
	}
	if !portAllowed(port) {
		fail(fmt.Sprintf("Port %d ist nicht freigegeben. Bridge mit -ports %s,%d starten.", port, *allowedPorts, port))
		return
	}
	if host == "" {
		fail("Keine Ziel-Adresse angegeben")
		return
	}

	ip, err := resolveTarget(ctx, host)
	if err != nil {
		fail(err.Error())
		return
	}
	target := net.JoinHostPort(ip.String(), strconv.Itoa(port))
	label := host + ":" + strconv.Itoa(port)

	log.Printf("Verbinde zu %s (%s) …", label, target)
	d := net.Dialer{Timeout: 6 * time.Second, KeepAlive: 30 * time.Second}
	tcp, err := d.DialContext(ctx, "tcp", target)
	if err != nil {
		fail("Companion nicht erreichbar (" + label + "): " + simplifyErr(err))
		return
	}
	defer tcp.Close()
	log.Printf("Verbunden: %s", label)
	sendStatus(ctx, c, statusMsg{Type: "connected", Target: label, Version: version})

	// TCP → WebSocket
	go func() {
		defer cancel()
		buf := make([]byte, 4096)
		for {
			n, err := tcp.Read(buf)
			if n > 0 {
				if werr := c.Write(ctx, websocket.MessageBinary, buf[:n]); werr != nil {
					return
				}
			}
			if err != nil {
				reason := "Companion hat die Verbindung beendet"
				if !errors.Is(err, net.ErrClosed) {
					log.Printf("%s: %v", reason, err)
				}
				_ = c.Close(websocket.StatusNormalClosure, reason)
				return
			}
		}
	}()

	// WebSocket → TCP
	for {
		typ, data, err := c.Read(ctx)
		if err != nil {
			break
		}
		if typ != websocket.MessageBinary {
			continue
		}
		if _, err := tcp.Write(data); err != nil {
			log.Printf("Schreibfehler zum Companion: %v", err)
			break
		}
	}
	log.Printf("Getrennt: %s", label)
}

func sendStatus(ctx context.Context, c *websocket.Conn, m statusMsg) {
	b, _ := json.Marshal(m)
	wctx, cancel := context.WithTimeout(ctx, 3*time.Second)
	defer cancel()
	_ = c.Write(wctx, websocket.MessageText, b)
}

// ---------- Prüfungen ----------

// originAllowed: nur die offizielle Webapp, lokal geöffnete Dateien (Origin "null")
// und localhost dürfen die Bridge benutzen – fremde Webseiten nicht.
func originAllowed(origin string) bool {
	if origin == "" || origin == "null" {
		return true
	}
	if strings.EqualFold(origin, defaultOrigin) {
		return true
	}
	u, err := url.Parse(origin)
	if err == nil {
		switch strings.ToLower(u.Hostname()) {
		case "localhost", "127.0.0.1", "::1":
			return true
		}
	}
	for _, o := range strings.Split(*extraOrigins, ",") {
		if o = strings.TrimRight(strings.TrimSpace(o), "/"); o != "" && strings.EqualFold(o, origin) {
			return true
		}
	}
	return false
}

func portAllowed(p int) bool {
	for _, s := range strings.Split(*allowedPorts, ",") {
		s = strings.TrimSpace(s)
		if s == "*" {
			return true
		}
		if lo, hi, ok := strings.Cut(s, "-"); ok {
			a, errA := strconv.Atoi(strings.TrimSpace(lo))
			b, errB := strconv.Atoi(strings.TrimSpace(hi))
			if errA == nil && errB == nil && a <= p && p <= b {
				return true
			}
			continue
		}
		if v, err := strconv.Atoi(s); err == nil && v == p {
			return true
		}
	}
	return false
}

// resolveTarget löst den Namen einmal auf und gibt eine IP zurück, damit genau
// die geprüfte Adresse verbunden wird. Standardmäßig nur lokale Netze.
func resolveTarget(ctx context.Context, host string) (net.IP, error) {
	host = strings.Trim(host, "[]")
	var ips []net.IP
	if ip := net.ParseIP(host); ip != nil {
		ips = []net.IP{ip}
	} else {
		rctx, cancel := context.WithTimeout(ctx, 5*time.Second)
		defer cancel()
		addrs, err := net.DefaultResolver.LookupIPAddr(rctx, host)
		if err != nil || len(addrs) == 0 {
			return nil, fmt.Errorf("Adresse %q konnte nicht aufgelöst werden", host)
		}
		for _, a := range addrs {
			ips = append(ips, a.IP)
		}
	}
	var pick net.IP
	for _, ip := range ips {
		if !*anyHost && !isLocal(ip) {
			return nil, fmt.Errorf("%s ist keine Adresse im lokalen Netz. Für andere Ziele Bridge mit -any-host starten.", host)
		}
		if pick == nil || (pick.To4() == nil && ip.To4() != nil) {
			pick = ip
		}
	}
	return pick, nil
}

func isLocal(ip net.IP) bool {
	return ip.IsPrivate() || ip.IsLoopback() || ip.IsLinkLocalUnicast()
}

func simplifyErr(err error) string {
	s := err.Error()
	switch {
	case strings.Contains(s, "refused"):
		return "Verbindung abgelehnt – läuft die WiFi-Firmware und stimmt der Port?"
	case strings.Contains(s, "timeout"), strings.Contains(s, "i/o timeout"):
		return "Zeitüberschreitung – ist das Gerät im selben Netz und eingeschaltet?"
	case strings.Contains(s, "no route"), strings.Contains(s, "unreachable"):
		return "Netz nicht erreichbar"
	}
	return s
}

func truncate(s string, n int) string {
	if len(s) <= n {
		return s
	}
	return s[:n]
}
