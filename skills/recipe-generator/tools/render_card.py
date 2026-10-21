#!/usr/bin/env python3
"""Render a recipe card HTML/PDF from a JSON recipe file.

Usage:
  render_card.py <recipe.json> <output.html|.pdf>
                 [--page-size A5|A4|A6|Letter]
                 [--template binder]

Injects JSON recipe data into an HTML template as a JS variable and optionally
converts to PDF via Chrome DevTools Protocol.

Exit codes: 0 ok, 1 invalid data, 2 usage error.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import re
import shutil
import socket
import struct
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path

EXIT_OK, EXIT_FAILED, EXIT_USAGE = 0, 1, 2

_TMPL_DIR = Path(__file__).resolve().parent.parent / "templates"
_CHROME_CANDIDATES = (
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "google-chrome",
    "chromium",
    "chromium-browser",
)
TEMPLATES = {
    "binder": _TMPL_DIR / "binder.html",
}
PAGE_SIZES = {
    "A5":     "A5 portrait",
    "A4":     "A4 portrait",
    "A6":     "A6 portrait",
    "Letter": "letter portrait",
}


def step_texts(data: dict) -> list[str]:
    """Every non-empty step text, with the steps of each group {heading, steps} flattened in."""
    texts = []
    for item in data.get("steps", []):
        if isinstance(item, dict):
            texts.extend(str(s) for s in item.get("steps", []) if str(s).strip())
        elif str(item).strip():
            texts.append(str(item))
    return texts


def validate(data: dict) -> list[str]:
    errors = []
    if not str(data.get("title", "")).strip():
        errors.append("title is empty")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(data.get("date", ""))):
        errors.append("date must be in RRRR-MM-DD format")
    for group in data.get("steps", []):
        if isinstance(group, dict) and not (str(group.get("heading", "")).strip() and group.get("steps")):
            errors.append("each step group needs a heading and at least one step")
    if not step_texts(data):
        errors.append("steps are empty")
    if not [t for t in data.get("tools", []) if str(t).strip()]:
        errors.append("tools are empty")
    return errors


def inject(data: dict, page_size: str, photo_name: str | None, tmpl_key: str) -> str:
    """Inject recipe data into the HTML template as a JS variable."""
    template = TEMPLATES[tmpl_key].read_text(encoding="utf-8")
    render_data = dict(data)
    render_data["_page_size"] = PAGE_SIZES[page_size]
    if photo_name:
        render_data["_photo"] = photo_name
    script = f'<script>window.RECIPE = {json.dumps(render_data, ensure_ascii=False)};</script>'
    return template.replace("<!-- RECIPE_DATA_PLACEHOLDER -->", script)


# ── WebSocket helpers (for Chrome DevTools Protocol) ─────────────────────────

def _ws_send(sock: socket.socket, data: str) -> None:
    payload = data.encode("utf-8")
    n = len(payload)
    mask_key = b"\x01\x02\x03\x04"
    masked = bytes(b ^ mask_key[i % 4] for i, b in enumerate(payload))
    if n < 126:
        header = bytes([0x81, 0x80 | n]) + mask_key
    elif n < 65536:
        header = bytes([0x81, 0xFE]) + struct.pack(">H", n) + mask_key
    else:
        header = bytes([0x81, 0xFF]) + struct.pack(">Q", n) + mask_key
    sock.sendall(header + masked)


def _ws_recv(sock: socket.socket) -> str:
    def read_exact(n: int) -> bytes:
        buf = b""
        while len(buf) < n:
            chunk = sock.recv(n - len(buf))
            if not chunk:
                raise ConnectionError("WebSocket closed")
            buf += chunk
        return buf

    hdr = read_exact(2)
    length = hdr[1] & 0x7F
    if length == 126:
        length = struct.unpack(">H", read_exact(2))[0]
    elif length == 127:
        length = struct.unpack(">Q", read_exact(8))[0]
    return read_exact(length).decode("utf-8", errors="replace")


# ── Chrome PDF conversion ─────────────────────────────────────────────────────

def find_chrome() -> str | None:
    for candidate in _CHROME_CANDIDATES:
        if candidate.startswith("/"):
            if Path(candidate).is_file():
                return candidate
        else:
            found = shutil.which(candidate)
            if found:
                return found
    return None


def html_to_pdf(html_path: Path, pdf_path: Path) -> tuple[bool, str]:
    """Convert HTML to PDF via Chrome DevTools Protocol (no default headers/footers)."""
    chrome = find_chrome()
    if not chrome:
        return False, "Google Chrome not found; install it or open the HTML manually."

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as _s:
        _s.bind(("127.0.0.1", 0))
        port = _s.getsockname()[1]

    proc = subprocess.Popen(
        [chrome, f"--remote-debugging-port={port}", "--headless=new",
         "--disable-gpu", "--no-sandbox", "--disable-dev-shm-usage", "--disable-extensions"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    sock: socket.socket | None = None
    try:
        for _ in range(40):
            try:
                urllib.request.urlopen(f"http://127.0.0.1:{port}/json/version", timeout=1)
                break
            except Exception:
                time.sleep(0.2)
        else:
            return False, "Chrome DevTools did not start in time."

        file_url = html_path.resolve().as_uri()
        req = urllib.request.Request(
            f"http://127.0.0.1:{port}/json/new?{file_url}", data=b"", method="PUT"
        )
        tab = json.loads(urllib.request.urlopen(req, timeout=5).read())
        ws_url: str = tab["webSocketDebuggerUrl"]
        ws_path = ws_url.split(f"127.0.0.1:{port}", 1)[1]

        ws_key = base64.b64encode(hashlib.sha1(b"RecipeCard12345=").digest()).decode()
        sock = socket.create_connection(("127.0.0.1", port), timeout=10)
        sock.sendall((
            f"GET {ws_path} HTTP/1.1\r\nHost: 127.0.0.1:{port}\r\n"
            f"Upgrade: websocket\r\nConnection: Upgrade\r\n"
            f"Sec-WebSocket-Key: {ws_key}\r\nSec-WebSocket-Version: 13\r\n\r\n"
        ).encode())
        resp = b""
        while b"\r\n\r\n" not in resp:
            resp += sock.recv(1024)
        if b"101" not in resp:
            return False, "WebSocket upgrade rejected by Chrome."

        cmd_id = 0

        def send(method: str, params: dict | None = None) -> int:
            nonlocal cmd_id
            cmd_id += 1
            _ws_send(sock, json.dumps({"id": cmd_id, "method": method, "params": params or {}}))
            return cmd_id

        def wait_result(target_id: int, timeout: float = 15.0) -> dict:
            sock.settimeout(timeout)
            while True:
                msg = json.loads(_ws_recv(sock))
                if msg.get("id") == target_id:
                    return msg

        _id = send("Page.enable")
        wait_result(_id)
        sock.settimeout(10.0)
        for _ in range(60):
            try:
                msg = json.loads(_ws_recv(sock))
                if msg.get("method") == "Page.loadEventFired":
                    break
            except socket.timeout:
                break
        time.sleep(0.5)

        _id = send("Page.printToPDF", {
            "displayHeaderFooter": False,
            "printBackground": True,
            "preferCSSPageSize": True,
        })
        result = wait_result(_id, timeout=30.0)
        if "error" in result:
            return False, f"CDP printToPDF: {result['error'].get('message', result['error'])}"

        pdf_b64 = result["result"].get("data", "")
        if not pdf_b64:
            return False, "CDP returned empty PDF data."
        pdf_path.write_bytes(base64.b64decode(pdf_b64))
        return True, ""

    except Exception as exc:
        return False, f"Chrome CDP error: {exc}"
    finally:
        if sock:
            try:
                sock.close()
            except Exception:
                pass
        try:
            proc.terminate()
            proc.wait(timeout=5)
        except Exception:
            pass


# ── Main ──────────────────────────────────────────────────────────────────────

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Render a recipe card from JSON data.")
    parser.add_argument("recipe", type=Path, help="JSON file with recipe content")
    parser.add_argument("output", type=Path, help="Output file (.html or .pdf)")
    parser.add_argument("--page-size", choices=sorted(PAGE_SIZES), default="A5")
    parser.add_argument("--template", choices=sorted(TEMPLATES), default="binder",
                        help="binder (the only layout)")
    args = parser.parse_args(argv)

    if not args.recipe.is_file():
        print(f"ERROR: {args.recipe} is not a file.", file=sys.stderr)
        return EXIT_USAGE

    try:
        data = json.loads(args.recipe.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"ERROR: {args.recipe} is not valid JSON: {exc}", file=sys.stderr)
        return EXIT_FAILED

    errors = validate(data)
    if errors:
        for msg in errors:
            print(f"ERROR: {msg}", file=sys.stderr)
        return EXIT_FAILED

    photo_name = None
    photo = str(data.get("photo", "")).strip()
    if photo:
        source = Path(photo).expanduser()
        if not source.is_file():
            print(f"ERROR: photo {source} does not exist.", file=sys.stderr)
            return EXIT_FAILED
        photo_name = source.name

    html_content = inject(data, args.page_size, photo_name, args.template)
    args.output.parent.mkdir(parents=True, exist_ok=True)

    if args.output.suffix.lower() == ".pdf":
        with tempfile.TemporaryDirectory(prefix="recipe-card-") as tmp:
            tmp_dir = Path(tmp)
            html_file = tmp_dir / "card.html"
            html_file.write_text(html_content, encoding="utf-8")
            if photo and photo_name:
                shutil.copy(Path(photo).expanduser(), tmp_dir / photo_name)
            ok, err = html_to_pdf(html_file, args.output)
            if not ok:
                print(f"ERROR: PDF conversion failed: {err}", file=sys.stderr)
                return EXIT_FAILED
    else:
        if photo and photo_name:
            shutil.copy(Path(photo).expanduser(), args.output.parent / photo_name)
        args.output.write_text(html_content, encoding="utf-8")

    print(f"Wrote {args.output} (template: {args.template}; page size: {args.page_size})")
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
