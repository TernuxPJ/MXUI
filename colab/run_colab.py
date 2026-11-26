#!/usr/bin/env python3
"""MX-UI Google Colab Launcher with Xray Core + trycloudflare Quick Tunnel."""
import os
import re
import shutil
import socket
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent.parent


def find_free_port(preferred: int = 8899) -> int:
    for candidate in (preferred, 8899, 8900, 8901, 7861, 9090):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("0.0.0.0", candidate))
                return candidate
            except OSError:
                continue
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("0.0.0.0", 0))
        return int(s.getsockname()[1])


def run(cmd, check=True, env=None):
    print(f"$ {cmd}", flush=True)
    p = subprocess.Popen(cmd, cwd=str(APP_DIR), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, env=env)
    for line in p.stdout:
        print(line, end="", flush=True)
    p.wait()
    if check and p.returncode != 0:
        raise RuntimeError(f"Command failed ({p.returncode}): {cmd}")
    return p.returncode


def ensure_xray():
    xray_bin = APP_DIR / "bin" / "xray"
    if shutil.which("xray") or xray_bin.exists():
        print(f"[1/3] Xray Core ready ({shutil.which('xray') or xray_bin})", flush=True)
        return
    print("[1/3] Installing Xray Core binary...", flush=True)
    if not shutil.which("unzip"):
        run("apt-get update -qq && apt-get install -y -qq curl unzip", check=False)
    env = os.environ.copy()
    env["XRAY_DEST"] = str(APP_DIR / "bin")
    run("bash deploy/install_xray.sh", check=False, env=env)



def ensure_bore():
    bore_bin = APP_DIR / "bin" / "bore"
    if shutil.which("bore") or bore_bin.exists():
        print(f"[2/4] bore ready ({shutil.which('bore') or bore_bin})", flush=True)
        return
    print("[2/4] Installing bore binary for Telegram SOCKS5 tunnel (bore.pub)...", flush=True)
    (APP_DIR / "bin").mkdir(parents=True, exist_ok=True)
    url = "https://github.com/ekzhang/bore/releases/download/v0.5.2/bore-v0.5.2-x86_64-unknown-linux-musl.tar.gz"
    run(f"curl -fsSL '{url}' -o /tmp/bore.tar.gz && tar -xzf /tmp/bore.tar.gz -C '{APP_DIR / 'bin'}' bore && chmod +x '{bore_bin}'", check=False)


def ensure_cloudflared() -> str:
    existing = shutil.which("cloudflared")
    if existing:
        return existing
    print("[2/3] Downloading cloudflared...", flush=True)
    bin_path = "/usr/local/bin/cloudflared"
    run(f"curl -fsSL https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -o {bin_path}")
    os.chmod(bin_path, 0o755)
    return bin_path


def main():
    subprocess.run(["pkill", "-f", str(APP_DIR / "main.py")], check=False)
    subprocess.run(["pkill", "-x", "cloudflared"], check=False)
    subprocess.run(["pkill", "-x", "xray"], check=False)
    time.sleep(0.5)

    ensure_xray()
    ensure_bore()
    cf_bin = ensure_cloudflared()

    preferred = int(os.environ.get("PORT", "8899") or "8899")
    if preferred == 8080 and os.path.exists("/content"):
        preferred = 8899
    port = find_free_port(preferred)

    print(f"[3/3] Starting MX-UI on http://127.0.0.1:{port} ...", flush=True)
    app_env = os.environ.copy()
    app_env.update({
        "PORT": str(port),
        "PYTHONUNBUFFERED": "1",
        "TLS_MODE": "tls",
        "PUBLIC_CONNECT_PORT": "443",
        "TG_TUNNEL_MODE": "bore",
        "BORE_SERVER": "bore.pub",
        "PATH": f"{APP_DIR / 'bin'}:{app_env.get('PATH', '')}",
    })
    app_proc = subprocess.Popen(
        [sys.executable, "-u", str(APP_DIR / "main.py")],
        cwd=str(APP_DIR),
        stdout=open("/tmp/mxui.log", "w"),
        stderr=subprocess.STDOUT,
        env=app_env,
    )

    ready = False
    for _ in range(30):
        if app_proc.poll() is not None:
            print(open("/tmp/mxui.log").read(), flush=True)
            raise RuntimeError(f"MX-UI exited early with code {app_proc.returncode}")
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{port}/", timeout=2) as r:
                if r.status < 500:
                    ready = True
                    break
        except Exception:
            time.sleep(1)

    if not ready:
        print(open("/tmp/mxui.log").read(), flush=True)
        raise RuntimeError("MX-UI did not start in time. Check /tmp/mxui.log")

    print(f"[OK] MX-UI listening locally on http://127.0.0.1:{port}", flush=True)

    cf_proc = subprocess.Popen(
        [cf_bin, "tunnel", "--no-autoupdate", "--protocol", "http2", "--url", f"http://127.0.0.1:{port}"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    url_re = re.compile(r"https://[a-z0-9-]+\.trycloudflare\.com")
    printed = False
    for line in cf_proc.stdout:
        m = url_re.search(line)
        if m and not printed:
            printed = True
            url = m.group(0)
            print(f"[TUNNEL] Waiting for Cloudflare DNS propagation ({url})...", flush=True)
            for _ in range(20):
                try:
                    with urllib.request.urlopen(url, timeout=3) as hr:
                        if hr.status < 500:
                            break
                except Exception:
                    time.sleep(1)
            print("\n" + "=" * 68, flush=True)
            print(f"  MX-UI LIVE URL : {url}", flush=True)
            print(f"  Local Port     : http://127.0.0.1:{port}", flush=True)
            print(f"  Logs           : /tmp/mxui.log", flush=True)
            print("=" * 68 + "\n", flush=True)

    app_proc.wait()


if __name__ == "__main__":
    main()
