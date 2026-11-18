"""
CyberKit v2.0 - Complete Cybersecurity Toolkit (CLI Edition)
Author: Hamid Shafiq, Armaghan Arshad, Abdul Basit, Aqeel Abbas
"""

import os
import sys
import socket
import string
import hashlib
import urllib.parse
from concurrent.futures import ThreadPoolExecutor
import requests
from PIL import Image
from PIL.ExifTags import TAGS
import pypdf

COMMON_PASSWORDS = [
    "password", "123456", "password123", "admin", "letmein",
    "qwerty", "abc123", "iloveyou", "111111", "123123",
    "1234567890", "password1", "12345678", "superman", "batman"
]

COMMON_PORTS = {
    21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP", 53: "DNS",
    80: "HTTP", 110: "POP3", 139: "NetBIOS", 443: "HTTPS", 445: "SMB",
    1433: "MSSQL", 3306: "MySQL", 3389: "RDP", 5432: "PostgreSQL", 8080: "HTTP-Proxy"
}

SUBDOMAIN_WORDLIST = [
    "www", "mail", "ftp", "localhost", "webmail", "smtp", "api", "dev",
    "portal", "admin", "vpn", "remote", "server", "test", "cloud", "staging"
]

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def banner():
    print("""
\033[38;2;88;166;255m╔══════════════════════════════════════════════════════════════╗
║              CyberKit v2.0 - Core Security Suite             ║
║           Developed by Hamid, Armaghan, Basit, Aqeel         ║
╠══════════════════════════════════════════════════════════════╣\033[0m
  [1] Password Strength Analyzer
  [2] Cryptographic Hash Generator (MD5, SHA1, SHA256, SHA512)
  [3] Caesar Cipher (Encrypt, Decrypt, Brute Force)
  [4] Have I Been Pwned? (Email & Password Hash Leaks)
  [5] Document & Image Metadata Extractor (EXIF & PDF)
  [6] Subdomain Recon & Multi-threaded Port Scanner
  [7] Phishing Link & Threat Intelligence Scanner (VirusTotal)
  [0] Exit
\033[38;2;88;166;255m╚══════════════════════════════════════════════════════════════╝\033[0m
""")

# ─── 1. PASSWORD ANALYZER ───────────────────────────────────────────────────

def analyze_password(password: str) -> dict:
    checks = {
        "length_8": len(password) >= 8,
        "length_12": len(password) >= 12,
        "uppercase": any(c.isupper() for c in password),
        "lowercase": any(c.islower() for c in password),
        "digits": any(c.isdigit() for c in password),
        "symbols": any(c in string.punctuation for c in password),
        "not_common": password.lower() not in COMMON_PASSWORDS,
    }
    weights = {
        "length_8": 1, "length_12": 2, "uppercase": 1,
        "lowercase": 1, "digits": 1, "symbols": 2, "not_common": 2
    }
    score = sum(weights[k] for k, passed in checks.items() if passed)
    max_score = sum(weights.values())
    percentage = int((score / max_score) * 100)

    if percentage < 40:
        strength = "WEAK"
    elif percentage < 65:
        strength = "MODERATE"
    elif percentage < 85:
        strength = "STRONG"
    else:
        strength = "VERY STRONG"

    charset_size = (26 if checks["lowercase"] else 0) + \
                   (26 if checks["uppercase"] else 0) + \
                   (10 if checks["digits"] else 0) + \
                   (32 if checks["symbols"] else 0)
    entropy = round(len(password) * (charset_size.bit_length() - 1 if charset_size > 0 else 0), 2)

    return {
        "score": score,
        "max": max_score,
        "percentage": percentage,
        "strength": strength,
        "entropy": entropy,
        "checks": checks
    }

def tool_password():
    print("\n\033[1m[ 01: PASSWORD STRENGTH ANALYZER ]\033[0m\n")
    password = input("Enter password to analyze: ").strip()
    if not password:
        print("[-] Error: No password provided.")
        return
    res = analyze_password(password)
    print(f"\n  Result   : {res['strength']} ({res['score']}/{res['max']} pts)")
    print(f"  Entropy  : ~{res['entropy']} bits")
    print(f"  Integrity: [{('█' * (res['percentage'] // 5)).ljust(20, '░')}] {res['percentage']}%\n")
    for k, v in res["checks"].items():
        print(f"   [{'✓' if v else '✗'}] {k.replace('_', ' ').capitalize()}")

# ─── 2. HASH GENERATOR ───────────────────────────────────────────────────────

def tool_hash():
    print("\n\033[1m[ 02: CRYPTOGRAPHIC HASH GENERATOR ]\033[0m\n")
    text = input("Enter plain text: ").strip()
    if not text:
        return
    enc = text.encode("utf-8")
    print("\n" + "─" * 64)
    print(f"  MD5    : {hashlib.md5(enc).hexdigest()} (Broken)")
    print(f"  SHA1   : {hashlib.sha1(enc).hexdigest()} (Deprec)")
    print(f"  SHA256 : {hashlib.sha256(enc).hexdigest()} (Standard)")
    print(f"  SHA512 : {hashlib.sha512(enc).hexdigest()} (High-Security)")
    print("─" * 64)

# ─── 3. CAESAR CIPHER ────────────────────────────────────────────────────────

def caesar_transform(text: str, shift: int) -> str:
    res = []
    for c in text:
        if c.isupper():
            res.append(chr((ord(c) - 65 + shift) % 26 + 65))
        elif c.islower():
            res.append(chr((ord(c) - 97 + shift) % 26 + 97))
        else:
            res.append(c)
    return "".join(res)

def tool_caesar():
    print("\n\033[1m[ 03: CAESAR CIPHER ENGINE ]\033[0m\n")
    mode = input("Select [1] Encrypt [2] Decrypt [3] Brute Force: ").strip()
    text = input("Enter target text: ").strip()
    if not text:
        return

    if mode in ("1", "2"):
        try:
            shift = int(input("Enter shift offset (1-25): ").strip())
        except ValueError:
            print("[-] Invalid numerical shift.")
            return
        if mode == "2":
            shift = -shift
        print(f"\n  Result: {caesar_transform(text, shift)}")
    elif mode == "3":
        print("\n=== Brute Force Decryption Matrix (Shifts 1-25) ===")
        for s in range(1, 26):
            print(f"  Shift {s:02d}: {caesar_transform(text, -s)}")

# ─── 4. HAVE I BEEN PWNED ────────────────────────────────────────────────────

def check_hibp_email(email: str, api_key: str):
    headers = {"hibp-api-key": api_key, "user-agent": "CyberKit-v2-Terminal"}
    url = f"https://haveibeenpwned.com/api/v3/breachedaccount/{urllib.parse.quote(email)}"
    try:
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code == 200:
            breaches = r.json()
            print(f"\n\033[31m[!] ALERT: Address found in {len(breaches)} public data breaches!\033[0m")
            for b in breaches:
                print(f"    - {b.get('Name')} | Date: {b.get('BreachDate')} | Compromised: {', '.join(b.get('DataClasses', []))}")
        elif r.status_code == 404:
            print("\n\033[32m[✓] CLEAN: No documented breach records for this email.\033[0m")
        elif r.status_code == 401:
            print("\n[-] Unauthorized: A valid HIBP API Key is required for email lookups.")
        else:
            print(f"[-] HTTP Error: Status code {r.status_code}")
    except Exception as e:
        print(f"[-] Connection failed: {e}")

def check_pwned_password_hash(password: str):
    sha1_pw = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()
    prefix, suffix = sha1_pw[:5], sha1_pw[5:]
    url = f"https://api.pwnedpasswords.com/range/{prefix}"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            hashes = (line.split(':') for line in r.text.splitlines())
            count = next((int(cnt) for h, cnt in hashes if h == suffix), 0)
            if count > 0:
                print(f"\n\033[31m[!] COMPROMISED: This password hash has appeared in {count:,} known database leaks!\033[0m")
            else:
                print("\n\033[32m[✓] SECURE: Password hash not seen in any known HIBP breaches.\033[0m")
    except Exception as e:
        print(f"[-] Failed to reach Pwned Passwords API: {e}")

def tool_hibp():
    print("\n\033[1m[ 04: HAVE I BEEN PWNED DATA LEAK INTELLIGENCE ]\033[0m\n")
    print("  [1] Check Account Email (Requires HIBP API Key)")
    print("  [2] Check Password Leak Status (Zero-Knowledge k-Anonymity - Free & No Key)")
    choice = input("Select operation: ").strip()

    if choice == "1":
        email = input("Target email: ").strip()
        key = input("HIBP API Key: ").strip()
        if email and key:
            check_hibp_email(email, key)
        else:
            print("[-] Both target email and API key are required.")
    elif choice == "2":
        pw = input("Target password: ").strip()
        if pw:
            check_pwned_password_hash(pw)

# ─── 5. METADATA EXTRACTOR ───────────────────────────────────────────────────

def tool_metadata():
    print("\n\033[1m[ 05: METADATA & EXIF DATA EXTRACTOR ]\033[0m\n")
    path = input("Enter file path (JPEG or PDF): ").strip().strip('"').strip("'")
    if not os.path.exists(path):
        print("[-] File not found.")
        return

    ext = os.path.splitext(path)[1].lower()
    if ext in ('.jpg', '.jpeg'):
        try:
            img = Image.open(path)
            exif = img.getexif()
            if not exif:
                print("[-] No EXIF header table detected in this image.")
                return
            print("\n=== Extracted Image EXIF Attributes ===")
            for tid, val in exif.items():
                tag_name = TAGS.get(tid, tid)
                print(f"  {str(tag_name):24}: {val}")
        except Exception as e:
            print(f"[-] Image parsing failure: {e}")

    elif ext == '.pdf':
        try:
            reader = pypdf.PdfReader(path)
            meta = reader.metadata
            if not meta:
                print("[-] No document metadata catalog available.")
                return
            print("\n=== Extracted PDF Document Metadata ===")
            for k, v in meta.items():
                clean_k = k.lstrip('/')
                print(f"  {clean_k:24}: {v}")
            print(f"  {'Total Pages':24}: {len(reader.pages)}")
        except Exception as e:
            print(f"[-] PDF parsing failure: {e}")
    else:
        print("[-] Unsupported file format. Please specify a JPEG or PDF.")

# ─── 6. RECON SCANNER ────────────────────────────────────────────────────────

def probe_port(target_ip: str, port: int) -> tuple:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(0.6)
    try:
        if s.connect_ex((target_ip, port)) == 0:
            banner = ""
            try:
                s.sendall(b"HEAD / HTTP/1.0\r\n\r\n")
                banner = s.recv(128).decode(errors="ignore").strip().splitlines()[0]
            except Exception:
                banner = COMMON_PORTS.get(port, "Unknown")
            return port, True, banner
    except Exception:
        pass
    finally:
        s.close()
    return port, False, ""

def tool_scanner():
    print("\n\033[1m[ 06: NETWORK RECONNAISSANCE SCANNER ]\033[0m\n")
    print("  [1] Subdomain Enumeration")
    print("  [2] Multi-Threaded TCP Port Scanner")
    choice = input("Select scan mode: ").strip()

    if choice == "1":
        domain = input("Target base domain (e.g., example.com): ").strip()
        print(f"\n[*] Enumerating subdomains for {domain}...")
        for sub in SUBDOMAIN_WORDLIST:
            fqdn = f"{sub}.{domain}"
            try:
                ip = socket.gethostbyname(fqdn)
                print(f"  [+] Discovered: {fqdn:30} -> {ip}")
            except socket.gaierror:
                pass

    elif choice == "2":
        target = input("Target Hostname or IP address: ").strip()
        try:
            target_ip = socket.gethostbyname(target)
            print(f"\n[*] Scanning target: {target} ({target_ip})")
            print("=" * 64)
            print(f"{'PORT':<8}{'STATE':<10}{'SERVICE / BANNER'}")
            print("=" * 64)

            with ThreadPoolExecutor(max_workers=30) as pool:
                futures = [pool.submit(probe_port, target_ip, p) for p in COMMON_PORTS.keys()]
                for f in futures:
                    p, open_flag, desc = f.result()
                    if open_flag:
                        print(f"{p:<8}\033[32mOPEN\033[0m      {desc}")
        except socket.gaierror:
            print("[-] DNS Resolution failed for target host.")

# ─── 7. THREAT INTELLIGENCE ─────────────────────────────────────────────────

def inspect_url(target_url: str):
    parsed = urllib.parse.urlparse(target_url if "://" in target_url else "http://" + target_url)
    domain = parsed.netloc.split(':')[0]
    flags = []

    if any(domain.replace('.', '').isdigit() for _ in [0]):
        flags.append("Domain is a raw IP address (frequent phishing vector)")
    if domain.count('.') >= 4:
        flags.append("Abnormal number of subdomains (subdomain tunneling / brand impersonation)")
    if "@" in target_url:
        flags.append("Contains '@' credential indicator (potential auth redirect trick)")
    if any(brand in domain.lower() for brand in ["paypal", "microsoft", "google", "apple", "login", "secure", "verify"]) and not domain.endswith((".paypal.com", ".microsoft.com", ".google.com", ".apple.com")):
        flags.append("High-value brand keyword observed inside suspicious domain hierarchy")

    return domain, flags

def query_virustotal(domain: str, api_key: str):
    url = f"https://www.virustotal.com/api/v3/domains/{domain}"
    headers = {"x-apikey": api_key}
    try:
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code == 200:
            stats = r.json().get("data", {}).get("attributes", {}).get("last_analysis_stats", {})
            print(f"\n  VirusTotal Vendor Verifications:")
            print(f"    - Malicious  : \033[31m{stats.get('malicious', 0)}\033[0m")
            print(f"    - Suspicious : \033[33m{stats.get('suspicious', 0)}\033[0m")
            print(f"    - Harmless   : \033[32m{stats.get('harmless', 0)}\033[0m")
            print(f"    - Undetected : {stats.get('undetected', 0)}")
        else:
            print(f"[-] VirusTotal API returned status {r.status_code}")
    except Exception as e:
        print(f"[-] VirusTotal request failed: {e}")

def tool_threat():
    print("\n\033[1m[ 07: PHISHING & THREAT INTELLIGENCE SCANNER ]\033[0m\n")
    url = input("Enter suspect URL: ").strip()
    if not url:
        return
    domain, flags = inspect_url(url)
    print(f"\n  Domain Evaluated : {domain}")
    print(f"  Heuristic Status : {'\033[31mSUSPICIOUS\033[0m' if flags else '\033[32mPASS\033[0m'}")
    for flag in flags:
        print(f"   [!] {flag}")

    vt_key = input("\nOptional VirusTotal API Key (Enter to skip): ").strip()
    if vt_key:
        query_virustotal(domain, vt_key)

# ─── MAIN DISPATCHER ────────────────────────────────────────────────────────

def main():
    tools = {
        "1": tool_password,
        "2": tool_hash,
        "3": tool_caesar,
        "4": tool_hibp,
        "5": tool_metadata,
        "6": tool_scanner,
        "7": tool_threat
    }
    while True:
        clear()
        banner()
        choice = input("  Execute Option [0-7] > ").strip()
        if choice == "0":
            print("\nExiting CyberKit Suite. Stay secure.\n")
            sys.exit(0)
        elif choice in tools:
            tools[choice]()
        else:
            print("[-] Invalid selection.")
        input("\nPress [Enter] to return to dashboard menu...")

if __name__ == "__main__":
    main()