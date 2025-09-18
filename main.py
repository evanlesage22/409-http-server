#!/usr/bin/env python3
import os
import socket
import sys
import threading
from urllib.parse import unquote
import mimetypes
from datetime import datetime

HOST = "127.0.0.1"
PORT = 8080
DOC_ROOT = os.path.abspath("./www")
SERVER_NAME = "SimpleHTTP10/1.0"

mimetypes.add_type("text/css", ".css")
mimetypes.add_type("application/javascript", ".js")
mimetypes.add_type("image/svg+xml", ".svg")
mimetypes.add_type("image/webp", ".webp")

def http_date():
    return datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")

def build_headers(status_line, headers_dict, body_bytes=b""):
    headers = [status_line]
    for k, v in headers_dict.items():
        headers.append(f"{k}: {v}")
    headers.append("")
    head = "\r\n".join(headers).encode("iso-8859-1") + b"\r\n"
    return head + body_bytes

def safe_join(doc_root, url_path):
    path = unquote(url_path.split("?", 1)[0].split("#", 1)[0])
    if path == "/":
        path = "/index.html"
    rel = path.lstrip("/")
    fs_path = os.path.normpath(os.path.join(doc_root, rel))
    if os.path.commonpath([fs_path, doc_root]) != doc_root:
        return None
    return fs_path

def guess_type(fs_path):
    ctype, _ = mimetypes.guess_type(fs_path)
    return ctype or "application/octet-stream"

def read_request(sock):
    sock.settimeout(2.0)
    data = b""
    cap = 65536
    while b"\r\n\r\n" not in data and len(data) < cap:
        chunk = sock.recv(4096)
        if not chunk:
            break
        data += chunk
    return data

def parse_request_head(raw):
    try:
        head = raw.split(b"\r\n\r\n", 1)[0].decode("iso-8859-1")
        lines = head.split("\r\n")
        req_line = lines[0]
        method, path, version = req_line.split(" ")
        headers = {}
        for line in lines[1:]:
            if not line:
                continue
            if ":" in line:
                k, v = line.split(":", 1)
                headers[k.strip().lower()] = v.strip()
        return method, path, version, headers
    except Exception:
        return None

def send_404(conn):
    custom = os.path.join(DOC_ROOT, "404.html")
    if os.path.isfile(custom):
        body = open(custom, "rb").read()
        headers = {
            "Date": http_date(),
            "Server": SERVER_NAME,
            "Content-Type": guess_type(custom),
            "Content-Length": str(len(body)),
            "Connection": "close",
        }
        resp = build_headers("HTTP/1.0 404 Not Found", headers, body)
    else:
        body = b"File Not Found.\n"
        headers = {
            "Date": http_date(),
            "Server": SERVER_NAME,
            "Content-Type": "text/plain",
            "Content-Length": str(len(body)),
            "Connection": "close",
        }
        resp = build_headers("HTTP/1.0 404 Not Found", headers, body)
    conn.sendall(resp)

def handle_client(conn, addr):
    try:
        raw = read_request(conn)
        if not raw:
            return
        parsed = parse_request_head(raw)
        if not parsed:
            body = b"Bad Request\n"
            headers = {
                "Date": http_date(),
                "Server": SERVER_NAME,
                "Content-Type": "text/plain",
                "Content-Length": str(len(body)),
                "Connection": "close",
            }
            conn.sendall(build_headers("HTTP/1.0 400 Bad Request", headers, body))
            return

        method, path, version, headers = parsed
        if method != "GET":
            body = b"Method Not Allowed\n"
            hdrs = {
                "Date": http_date(),
                "Server": SERVER_NAME,
                "Allow": "GET",
                "Content-Type": "text/plain",
                "Content-Length": str(len(body)),
                "Connection": "close",
            }
            conn.sendall(build_headers("HTTP/1.0 405 Method Not Allowed", hdrs, body))
            return

        fs_path = safe_join(DOC_ROOT, path)
        if not fs_path or not os.path.exists(fs_path):
            send_404(conn)
            return

        if os.path.isdir(fs_path):
            idx = os.path.join(fs_path, "index.html")
            if os.path.isfile(idx):
                fs_path = idx
            else:
                send_404(conn)
                return

        try:
            with open(fs_path, "rb") as f:
                body = f.read()
        except OSError:
            send_404(conn)
            return

        ctype = guess_type(fs_path)
        headers_out = {
            "Date": http_date(),
            "Server": SERVER_NAME,
            "Content-Type": ctype,
            "Content-Length": str(len(body)),
            "Connection": "close",
        }
        resp = build_headers("HTTP/1.0 200 OK", headers_out, body)
        conn.sendall(resp)
    finally:
        conn.close()

def serve(host=HOST, port=PORT):
    os.makedirs(DOC_ROOT, exist_ok=True)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((host, port))
        s.listen(5)
        print(f"Serving HTTP/1.0 on http://{host}:{port} (doc root: {DOC_ROOT})")
        while True:
            conn, addr = s.accept()
            t = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
            t.start()

if __name__ == "__main__":
    if len(sys.argv) >= 2:
        PORT = int(sys.argv[1])
    if len(sys.argv) >= 3:
        DOC_ROOT = os.path.abspath(sys.argv[2])
    serve(HOST, PORT)
