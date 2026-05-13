



# SGScope
**SiteGround Support Recon & Diagnostic Tool**

SGScope is a CLI utility for rapid reconnaissance of sites hosted on or moving to SiteGround[cite: 1]. It pulls DNS, SSL details, and SG-specific headers (Caching, CDN, and PHP type) into a single terminal view[cite: 1].

## Quick Start

1. **Install dependencies:**
````
   pip install -r requirements.txt
   ````



**Make it executable although in case it is not:**
```bash
chmod +x scope

```


3. **Test it:**
```bash
./scope recon domain.com


```



```

---

## Commands & Usage

Use `./scope [COMMAND] --help` to see all available flags for a specific module[cite: 1].

### General Recon
Run the full suite (DNS, SSL, Curl, and SG info) in one go[cite: 1]:
```bash
./scope recon domain.com

```

### DNS Diagnostics

Check specific records or run a full zone check:

```bash
./scope dns domain.com --spf --dmarc

```

### SSL & TLS

Extract cipher suites, expiry dates, and SANs:

```bash
./scope ssl domain.com --expiry --issuer

```

### Curl & Cache Analysis

Check SiteGround NGINX cache performance and headers:

```bash
./scope curl domain.com --cached

```

The `--cached` flag runs 10 hits to calculate a hit/miss percentage.

### WhoIs

Quick registrar and expiration check:

```bash
./scope whois domain.com --registrar --dates

```

---

## Configuration

Customization (User-Agent, timeouts, colors) is handled in `tools/config.py`.

**Updates:** The tool checks for updates on launch. To stop the tool from overwriting manual changes, change the `version` string in `main.py`.

## Dependencies

* `typer` / `rich` (CLI & Formatting)


* `requests` / `urllib3` (HTTP/SSL)


* `dnspython` / `python-whois` (Network records)



---

### Technical Notes

* **SSL Validation:** The tool defaults to `verify=False` so it doesn't crash when inspecting sites with broken or expired certificates.


* **SG Ping:** The `sg_hosted` check relies on the `.well-known/sg-hosted-ping` endpoint.



```

---

### 🛠️ Mac ZSH Shortcut Setup
To run `scope` from anywhere, paste this at the bottom of your `~/.zshrc` file:

```zsh
# SGScope Global Shortcut
scope() {
    source /path/to/your/sgscope/venv/bin/activate
    python3 /path/to/your/sgscope/scope "$@"
}

#### Additionally!

scope --install-completion
#### and reset terminal
```

*(Make sure to change `/path/to/your/sgscope` to the actual folder path on your Mac.)*
