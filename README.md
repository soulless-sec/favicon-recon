# Favicon Recon

<p align="center">
<img src="https://img.shields.io/badge/Python-3.x-3776AB?style=for-the-badge&logo=python&logoColor=white"/>
<img src="https://img.shields.io/badge/Linux-Kali-000000?style=for-the-badge&logo=linux&logoColor=white"/>
<img src="https://img.shields.io/badge/Shodan-Favicon%20Hunting-red?style=for-the-badge"/>
<img src="https://img.shields.io/badge/FOFA-Favicon%20Search-orange?style=for-the-badge"/>
<img src="https://img.shields.io/badge/Censys-Favicon%20Recon-purple?style=for-the-badge"/>
</p>

<p align="center"><b>Automated favicon discovery and hash generation for Shodan, FOFA and Censys reconnaissance.</b></p>

---

## Overview

**Favicon Recon** is a lightweight Python CLI tool that automatically discovers a website's favicon, downloads it, calculates multiple hashes, and generates ready-to-use search queries for **Shodan**, **FOFA**, and **Censys**.

```bash
./favicon-recon.py https://example.com
```

## Features

- Automatic favicon discovery
- HTML `<link rel="icon">` parsing
- Relative favicon URL resolution
- Standard favicon path detection
- Shodan-compatible MurmurHash3 calculation
- MD5, SHA1 and SHA256 generation
- Ready-to-copy Shodan, FOFA and Censys queries
- Colorful terminal interface using Rich
- Custom HTTP timeout support

## Installation

```bash
git clone https://github.com/yourusername/favicon-recon.git
cd favicon-recon
pip install -r requirements.txt
chmod +x favicon-recon.py
```

## Usage

```bash
./favicon-recon.py https://example.com
```

```bash
./favicon-recon.py example.com
```

Custom timeout:

```bash
./favicon-recon.py https://example.com -t 20
```

Help:

```bash
./favicon-recon.py --help
```

## Generated Hashes

| Hash | Usage |
|---|---|
| MurmurHash3 | Shodan & FOFA |
| MD5 | Censys |
| SHA1 | File fingerprint |
| SHA256 | File fingerprint |

## Search Queries

### Shodan

```text
http.favicon.hash:251235005
```

### FOFA

```text
icon_hash="251235005"
```

### Censys — Legacy MD5

```text
services.http.response.favicons.md5_hash="099dbgyt5645464340bd5f1eb6d7"
```

### Censys — Platform Host MD5

```text
host.services.endpoints.http.favicons.hash_md5="099dbgyt5645464340bd5f1eb6d7"
```

### Censys — Platform Web MD5

```text
web.endpoints.http.favicons.hash_md5="099dbgyt5645464340bd5f1eb6d7"
```

## How It Works

```text
                Target Website
                       |
                       v
             Favicon Discovery
                       |
                       v
              Download Favicon
                       |
                       v
             Hash Calculation
                       |
          +------------+------------+
          |            |            |
          v            v            v
        MMH3          MD5      SHA1/SHA256
          |            |
     +----+----+       |
     v         v       v
  Shodan      FOFA   Censys
```


## Requirements

```text
requests
mmh3
rich
```

Install:

```bash
pip install -r requirements.txt
```

## Use Cases

- Passive reconnaissance
- Asset discovery
- Infrastructure correlation
- Attack surface mapping
- Bug bounty reconnaissance
- Red team reconnaissance
- OSINT research
- CTF challenges
- Authorized security assessments

## Limitations

- Some websites may not expose a favicon.
- Multiple favicon files may exist on the same website.
- Dynamic or authenticated favicons may not be accessible.
- CDN or WAF protections may block requests.
- The first valid favicon discovered is selected.

## Roadmap

- [ ] Detect all favicon URLs
- [ ] Hash every discovered favicon
- [ ] SVG favicon support
- [ ] ICO multi-resolution support
- [ ] JSON output
- [ ] CSV export
- [ ] Output file support
- [ ] Interactive mode
- [ ] Clipboard copy support
- [ ] Subdomain batch scanning

## Responsible Use

This project is intended for **educational purposes and authorized security research only**.

Only use this tool against systems that you own or have explicit permission to assess.

---

<p align="center"><b>Favicon → Hash → Hunt</b></p>
<p align="center">Made for Security Researchers & Offensive Security Enthusiasts.</p>
