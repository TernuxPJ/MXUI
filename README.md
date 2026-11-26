<div align="center">

# MX-UI

**Lightweight, Offline-First Xray (`XHTTP packet-up`) & Telegram SOCKS5 Control Plane**

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Async-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Xray Core](https://img.shields.io/badge/Xray-XHTTP%20packet--up-111827?style=for-the-badge)](https://github.com/XTLS/Xray-core)
[![Telegram SOCKS5](https://img.shields.io/badge/Telegram-SOCKS5%20%2B%20bore.pub-26A5E4?style=for-the-badge&logo=telegram&logoColor=white)](https://core.telegram.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)

<br/>

A minimal, high-craft control panel built with **FastAPI**, **Xray Core**, **local Tailwind CSS**, and **bundled offline typography** (`InterDisplay`, `Inter`, `LiberationMono`, `NotoKufiArabic`). Zero CDN dependencies, zero animation flicker on live refresh, and built-in **RFC 1928/1929 SOCKS5** tunneling via `bore.pub` or Direct VPS.

[Features](#-highlights) • [Protocols](#-supported-protocols) • [Quick Start](#-quick-start) • [Configuration](#-environment-variables) • [Security](#-security)

</div>

---

## Highlights

| Area | Details |
| :--- | :--- |
| **Xray Inbounds** | Streamlined strictly to **VLESS** and **Trojan** over **XHTTP (`packet-up`)** with per-config UUIDs, traffic/expiry/IP/speed limits, custom SNI/CDN host, edge IP pool, and Base64 subscription links. |
| **Telegram SOCKS5 Panel** | Built-in pure-Python async **RFC 1928/1929 SOCKS5** proxy server with per-user credentials, one-click `tg://socks` & `https://t.me/socks` links, local QR codes, pause/resume/restart controls, and **`bore.pub` TCP tunnel** or **Direct VPS** exposure. |
| **Modern Obsidian & Alabaster UI** | Responsive dark/light theme with glassmorphic sticky header, semantic telemetry rings (CPU, RAM, Swap, Storage), expandable system diagnostics, and zero-flicker DOM diffing on auto-refresh. |
| **100% Offline-First Assets** | All stylesheets (`tailwind.css`, `app.css`) and fonts (`InterDisplay`, `Inter`, `LiberationMono`, `NotoKufiArabic`) are served locally from `static/` — no external font or CSS CDNs. |
| **Hardened Auth** | First-run `/setup` onboarding, salted `PBKDF2-HMAC-SHA256` password hashing with constant-time verification, signed `HttpOnly` session cookies, and login brute-force rate limiting. |

---

## Supported Protocols

| Protocol | Transport & Mode | Path | Notes |
| :--- | :--- | :--- | :--- |
| **VLESS** | `xhttp` (`mode=packet-up`) | `/xhttp` | TLS + Chrome uTLS fingerprint + `h2,http/1.1` ALPN |
| **Trojan** | `xhttp` (`mode=packet-up`) | `/xhttp-trojan` | TLS + Chrome uTLS fingerprint + `h2,http/1.1` ALPN |
| **Telegram SOCKS5** | TCP (`RFC 1928/1929`) | `bore.pub:<port>` or Direct VPS | Username/password auth, `tg://socks` & `t.me/socks` + QR |

---

## Quick Start

### Docker Compose (Recommended)

```bash
git clone https://github.com/TernuxPJ/MXUI.git
cd MXUI/deploy
docker compose up -d --build
```

Then open `http://<your-server-ip>:8080/setup` to create your admin credentials.

### Run Locally (Python 3.11+)

```bash
git clone https://github.com/TernuxPJ/MXUI.git
cd MXUI
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8080
```

---

## Environment Variables

| Variable | Default | Description |
| :--- | :--- | :--- |
| `PORT` | `8080` | Public HTTP port for the web panel and XHTTP reverse proxy |
| `MXUI_DATA_DIR` | `./data` | Persistent directory for state, SQLite/JSON data, and signing key |
| `PUBLIC_HOST` | Auto-detected | Public domain or IP used when generating VLESS/Trojan links |
| `CDN_HOST` | *(optional)* | Custom CDN / edge domain override for XHTTP links |
| `TG_TUNNEL_MODE` | `bore` | Telegram SOCKS5 exposure mode: `bore` (`bore.pub`) or `direct` (VPS IP) |
| `TG_BORE_SERVER` | `bore.pub` | Custom `bore` relay server host (when using `bore` mode) |

---

## Project Structure

```text
MXUI/
├── main.py                 # FastAPI entrypoint, lifespan, reverse proxy & middleware
├── app/
│   ├── auth.py             # PBKDF2-HMAC-SHA256 hashing, session cookies & rate limiter
│   ├── links.py            # VLESS & Trojan XHTTP (packet-up) URI + subscription builders
│   ├── state.py            # Persistent config state & protocol validation
│   ├── telegram_proxy.py   # Pure-Python async SOCKS5 server + bore.pub tunnel manager
│   └── routes/             # Auth, configs, system metrics & Telegram SOCKS5 APIs
├── templates/              # Jinja2 views (dashboard, login, setup, user portal)
├── static/
│   ├── css/                # Local tailwind.css & v3.2 Obsidian/Alabaster app.css
│   ├── fonts/              # Bundled InterDisplay, Inter, LiberationMono & NotoKufiArabic
│   └── js/                 # Zero-flicker dashboard controller & utilities
└── deploy/                 # Dockerfile & docker-compose.yml
```

---

## Security

- Never commit `data/` (`mxui_state.json`, `mxui_secret.key`) — excluded via `.gitignore`.
- Change default credentials immediately via `/setup` on first launch.
- Run behind HTTPS (reverse proxy / TLS terminator) when deploying on a public VPS.

---

<div align="center">
  <sub>Built and maintained by <b>Muvixo</b> · MX-UI</sub>
</div>
