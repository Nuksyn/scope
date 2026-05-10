# scope — Domain Reconnaissance CLI

A fast, terminal-native recon tool built for SiteGround support engineers and anyone doing domain investigation work. Run targeted checks or full recon with a single command.

This is work in progress, if you have suggestions for the tool I would love to hear them and implement them further!
---

## Install

```bash
pip install -r requirements.txt
chmod +x scope.py
```

## Usage

```bash
# Quick full recon
python3 scope.py domain.com

# DNS lookups
python3 scope.py dns domain.com
python3 scope.py dns domain.com --record a --record mx
python3 scope.py dns domain.com --ptr 142.250.185.78
python3 scope.py dns domain.com --resolver 1.1.1.1
python3 scope.py dns domain.com --spf
python3 scope.py dns domain.com --dmarc
python3 scope.py dns domain.com --caa

# SSL certificate
python3 scope.py ssl domain.com
python3 scope.py ssl domain.com --cipher
python3 scope.py ssl domain.com --expiry
python3 scope.py ssl domain.com --issuer
python3 scope.py ssl domain.com --sans
python3 scope.py ssl domain.com --timeout 15

# WHOIS
python3 scope.py whois domain.com
python3 scope.py whois domain.com --registrar
python3 scope.py whois domain.com --dates
python3 scope.py whois domain.com --nameservers
python3 scope.py whois domain.com --dnssec
python3 scope.py whois domain.com --status

# HTTP analysis
python3 scope.py curlparse domain.com
python3 scope.py curlparse domain.com --headers
python3 scope.py curlparse domain.com --redirects
python3 scope.py curlparse domain.com --cached
python3 scope.py curlparse domain.com --status-code
python3 scope.py curlparse domain.com --ttfb
python3 scope.py curlparse domain.com --tls
python3 scope.py curlparse domain.com --cookies
python3 scope.py curlparse domain.com --verbose
python3 scope.py curlparse domain.com --uf
python3 scope.py curlparse domain.com --timeout 15

# SiteGround hosted check
python3 scope.py sg-hosted domain.com

# Run everything
python3 scope.py all domain.com
```

## Dependencies

```
typer
rich
requests
dnspython
python-whois
```


- User agent: SGScope/0.1.0-alpha (SiteGround Support Recon Tool)
- All output is copy-paste friendly — no table borders

## Author

Built by Nikola Nikolov Nikolov — SiteGround Support Team
