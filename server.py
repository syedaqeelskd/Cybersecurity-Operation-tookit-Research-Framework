"""
CyberKit v2.0 - Local Backend REST API & Server
Serves static frontend and handles local execution (sockets, APIs, EXIF)
"""

import os
import socket
import hashlib
import urllib.parse
from concurrent.futures import ThreadPoolExecutor
from flask import Flask, request, jsonify, send_from_directory
import requests
from PIL import Image
from PIL.ExifTags import TAGS
import pypdf

app = Flask(__name__, static_folder=".", static_url_path="")
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB maximum upload
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "temp_uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

COMMON_PORTS = {
    21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP", 53: "DNS",
    80: "HTTP", 110: "POP3", 139: "NetBIOS", 443: "HTTPS", 445: "SMB",
    1433: "MSSQL", 3306: "MySQL", 3389: "RDP", 5432: "PostgreSQL", 8080: "HTTP-Proxy"
}

@app.route("/")
def index():
    return send_from_directory(".", "index.html")

# ─── API: HAVE I BEEN PWNED ──────────────────────────────────────────────────
@app.route("/api/breach-check", methods=["POST"])
def breach_check():
    data = request.json or {}
    email = data.get("email", "").strip()
    api_key = data.get("apiKey", "").strip()

    if not email:
        return jsonify({"error": "Target email is required."}), 400
    if not api_key:
        return jsonify({"error": "An authentic HIBP API Key is required by haveibeenpwned.com to search accounts."}), 400

    headers = {"hibp-api-key": api_key, "user-agent": "CyberKit-WebEngine"}
    url = f"https://haveibeenpwned.com/api/v3/breachedaccount/{urllib.parse.quote(email)}"

    try:
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code == 200:
            return jsonify({"breached": True, "count": len(r.json()), "breaches": r.json()})
        elif r.status_code == 404:
            return jsonify({"breached": False, "count": 0, "breaches": []})
        elif r.status_code == 401:
            return jsonify({"error": "Invalid HIBP API Key supplied."}), 401
        return jsonify({"error": f"Upstream HIBP status code: {r.status_code}"}), 502
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ─── API: METADATA EXTRACTOR ────────────────────────────────────────────────
@app.route("/api/extract-metadata", methods=["POST"])
def extract_metadata():
    if "file" not in request.files:
        return jsonify({"error": "No file received."}), 400
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "Empty filename."}), 400

    save_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(save_path)
    metadata = {}
    ext = os.path.splitext(file.filename)[1].lower()

    try:
        if ext in [".jpg", ".jpeg"]:
            img = Image.open(save_path)
            exif = img.getexif()
            if exif:
                for k, v in exif.items():
                    metadata[str(TAGS.get(k, k))] = str(v)
        elif ext == ".pdf":
            reader = pypdf.PdfReader(save_path)
            if reader.metadata:
                for k, v in reader.metadata.items():
                    metadata[k.lstrip("/")] = str(v)
            metadata["PageCount"] = str(len(reader.pages))
        else:
            return jsonify({"error": "Only JPEG and PDF files are supported."}), 400
    except Exception as e:
        return jsonify({"error": f"Extraction error: {str(e)}"}), 500
    finally:
        if os.path.exists(save_path):
            os.remove(save_path)

    return jsonify({"filename": file.filename, "metadata": metadata})

# ─── API: PORT SCANNER ───────────────────────────────────────────────────────
def check_port(target_ip, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(0.7)
    try:
        if s.connect_ex((target_ip, port)) == 0:
            return port, True, COMMON_PORTS.get(port, "Unknown")
    except Exception:
        pass
    finally:
        s.close()
    return port, False, ""

@app.route("/api/scan-ports", methods=["POST"])
def scan_ports():
    data = request.json or {}
    target = data.get("target", "").strip()
    if not target:
        return jsonify({"error": "Target hostname or IP is required."}), 400

    try:
        target_ip = socket.gethostbyname(target)
    except socket.gaierror:
        return jsonify({"error": f"Could not resolve host: {target}"}), 400

    results = []
    with ThreadPoolExecutor(max_workers=25) as executor:
        futures = [executor.submit(check_port, target_ip, p) for p in COMMON_PORTS.keys()]
        for f in futures:
            port, is_open, desc = f.result()
            if is_open:
                results.append({"port": port, "service": desc, "status": "OPEN"})

    return jsonify({"target": target, "ip": target_ip, "open_ports": results})

# ─── API: VIRUSTOTAL & THREAT INTEL ──────────────────────────────────────────
@app.route("/api/threat-intel", methods=["POST"])
def threat_intel():
    data = request.json or {}
    target_url = data.get("url", "").strip()
    vt_key = data.get("apiKey", "").strip()

    if not target_url:
        return jsonify({"error": "URL parameter is missing."}), 400

    parsed = urllib.parse.urlparse(target_url if "://" in target_url else "http://" + target_url)
    domain = parsed.netloc.split(":")[0]

    flags = []
    if any(c.isdigit() for c in domain.replace(".", "")):
        flags.append("Domain contains raw decimal sequences or an IP.")
    if domain.count(".") >= 4:
        flags.append("Excessive subdomains (potential DNS tunneling or phishing cloaking).")
    if any(k in domain.lower() for k in ["secure", "login", "verify", "update", "bank", "account"]) and not domain.endswith((".com", ".net", ".org", ".edu", ".gov")):
        flags.append("Phishing heuristic: High-risk auth keyword on an uncommon TLD.")

    vt_data = None
    if vt_key:
        try:
            r = requests.get(
                f"https://www.virustotal.com/api/v3/domains/{domain}",
                headers={"x-apikey": vt_key},
                timeout=10
            )
            if r.status_code == 200:
                vt_data = r.json().get("data", {}).get("attributes", {}).get("last_analysis_stats", {})
        except Exception:
            pass

    return jsonify({"domain": domain, "flags": flags, "virustotal": vt_data})

if __name__ == "__main__":
    print("\n* CyberKit Backend Engine running on http://127.0.0.1:5000")
    print("* Web dashboard accessible at http://localhost:5000\n")
    app.run(host="0.0.0.0", port=5000, debug=False)