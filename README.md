# CyberKit

A modular, zero-dependency cybersecurity analysis and educational framework. CyberKit provides dual operational interfaces: a high-efficiency terminal CLI and a hardware-accelerated web dashboard[cite: 1, 2, 4].

## Features

1. **Password Strength Assessment Matrix**: Computes Shannon entropy, character set key space metrics, and checks common dictionaries[cite: 1, 2, 4].
2. **Cryptographic Digest Engine**: Generates MD5, SHA-1, SHA-256, and SHA-512 hashes with security alerts[cite: 1, 2, 4].
3. **Caesar Shift Transformation & Cracker**: Symmetrical substitution cipher supporting encryption, decryption, and full 25-state brute-force key depletion[cite: 1, 2, 4].
4. **Have I Been Pwned (HIBP) Integration**: Queries account breaches via the HIBP REST API and checks compromised password hashes using zero-knowledge k-Anonymity.
5. **Metadata & Forensic Reader**: Extracts EXIF camera parameters, timestamps, and authorship data from JPEG and PDF files.
6. **Subdomain Recon & Port Scanner**: Multi-threaded TCP socket mapper discovering exposed network services and subdomains.
7. **Phishing & Threat Intelligence Analyzer**: Identifies typosquatting, credential harvesting patterns, and correlates reputation via the VirusTotal v3 API.

---

## Installation & Deployment

### 1. Where to Install
Create an isolated Python Virtual Environment (`.venv`) inside the root directory of your cloned repository.

### 2. Setup Guide

#### On Windows (PowerShell or CMD):
```bash
# Clone the repository
git clone [https://github.com/hamidshafiq7/cyberkit.git](https://github.com/hamidshafiq7/cyberkit.git)
cd cyberkit

# Create virtual environment
python -m venv .venv

# Activate virtual environment
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt