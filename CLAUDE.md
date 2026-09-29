# Domain Scope Rewrite — Project Brief

## Context

There is an existing project at `https://github.com/Nuksyn/scope` — a Python CLI tool, now named **Domain Scope** (see "Naming" below), built for web-hosting support recon (DNS, SSL, WHOIS, HTTP/CDN checks on customer domains). It works, but it has a long list of structural and correctness bugs (functions mixing lookup/flag-logic/printing together, inconsistent domain-input handling, silent failures, an unsafe auto-updater, etc.).

**We are not patching this project. We are rewriting it from scratch**, keeping the intent (a fast CLI recon tool for a support engineer's daily domain/network diagnostics) but replacing the architecture entirely.

## Naming

- The tool is **Domain Scope**. Python package: `domainscope` (`src/domainscope/`). CLI command: `scope` (same as the original tool, e.g. `scope dns example.com`).
- **No references to any specific hosting provider or employer**, anywhere: not in the tool's name, package/module names, CLI command, User-Agent, user-facing output, docs, or this file.
- HTTP User-Agent: tool name + version, e.g. `DomainScope/0.3.0`, overridable via the TOML config.

## Who does what

- **The user writes all production code themselves.** Claude's job is to teach, guide, and review — not to hand over finished files.
- When a new library or pattern is needed, Claude's default move is to give the user a **small, runnable demo script** they can open in PyCharm and actually run, so they see the library's behavior firsthand (e.g. "run this against `dnspython` to see what a `NoAnswer` exception actually looks like") — *then* the user writes the real version themselves, with Claude reviewing/correcting rather than authoring.
- **Two demo files per new library, created by Claude, in `sandbox/`** (gitignored, never committed):
  - `<library>_demo.py` — the **terminal** version: Claude gives the exact commands to run and what to look for in the output.
  - `<library>_debug.py` — the **PyCharm** version: runs with the plain Run/Debug button, no arguments or setup needed (hardcoded inputs/scenarios), with suggested breakpoint spots so the user can step through it in the debugger.
  - Never name them `test_*.py`: they hit the real network and are not pytest tests (real tests live in `tests/`).
- Claude should proactively suggest a demo/test-in-PyCharm step whenever a new library, pattern, or non-obvious API is introduced, rather than waiting to be asked.
- Claude does not write whole modules or commands for the user. Small illustrative snippets (a few lines, to show a pattern or a library call) are fine; full working implementations are not, even if asked for "just this once."
- Claude keeps asking clarifying/design questions when scope or intent is ambiguous, rather than guessing and building the wrong thing.
- **Keep answers very brief** — short and to the point; expand only when asked.
- **Keep this file current.** Whenever the user states a preference or settles a decision (including items under "Still open"), Claude updates the relevant section of this file right away — moving resolved items out of "Still open", replacing outdated statements rather than appending contradictions — and briefly tells the user what changed. Preferences that are personal or must not appear in the public repo go to Claude's local memory instead.

## Architecture principles

- **OOP wherever it makes sense** — this is a hard priority for this rewrite, not a nice-to-have. Prefer classes with methods and typed state over standalone functions passing large parameter lists, wherever the domain naturally supports it.
- **Layered separation, strictly enforced:**
  1. **Typer CLI commands** — parse arguments, validate flag combinations, call into objects. No lookup logic, no printing logic.
  2. **Domain-object methods** — the actual work (network calls, parsing). Never print. Never raise raw library exceptions — catch and re-raise as project-specific exceptions. Always return a typed **dataclass** result, never `None` or a bare bool, and put failures in an `.error` field on that dataclass rather than raising past the method boundary (so one failed check never stops the others).
  3. **Render functions/classes** — take a result dataclass (+ verbosity level) and produce the terminal output. This is the *only* layer allowed to touch Rich/console output.
- **`src/` layout**, `pyproject.toml`-based project, not a flat script folder.
- **Custom exception hierarchy** — one base `ScopeError`, with specific subclasses per failure type (e.g. `DnsTimeoutError`, `DnsNxDomainError`, `SslHandshakeError`, `WhoisNotFoundError`, `InvalidTargetError`). Each check module catches the underlying library's exceptions and re-raises its own, so `except ScopeError` at a boundary reliably covers every anticipated failure — anything else is a genuine bug and should surface as a real traceback, not be silently swallowed.
- **A single, shared input-normalization entry point.** Every command that takes a domain or IP funnels through one `parse_target()` function (called once, inside the relevant object's `__init__`), which: strips/lowercases, strips protocol and path/port, strips trailing dot, converts IDN to punycode, and detects whether the input is actually an IP address (returning a distinct `IPTarget` vs `DomainTarget`, since a bare IP means different things to different checks — e.g. `whois` runs real IP RDAP + PTR on an IP, `dns` rejects/redirects since there's no zone for a bare IP).
- **No caching** — every lookup should hit the network fresh, by explicit decision (the user often re-checks the same domain in one session and wants current data, not a stale cache).
- **Parallel execution for composite commands** — `recon` (and similar) run their sub-checks concurrently via `concurrent.futures.ThreadPoolExecutor`, collecting all results before printing anything (so output stays in a fixed, readable order despite concurrent execution).
- **Always-on, rotating error log** (size- or age-based rotation, e.g. 5MB or 30 days) via the standard `logging` module — every caught exception is logged with domain + traceback, regardless of verbosity. No `--debug` flag for now; that can be added later if needed.
- **Verbosity via counted flags** (`-v`, `-vv`, `-vvv`), read only by the render layer — the underlying check methods always fetch and return full data regardless of verbosity.
- **External/network-sourced strings must be treated as untrusted** wherever they reach Rich's markup-parsing console output (headers, WHOIS fields, DNS TXT records, etc.) — escape before printing. This is a known gap to close before the tool handles real customer data, even though it was deprioritized during early feature planning.
- **No root/admin access, ever.** The tool must install and run entirely as a normal user (e.g. on a work Mac without admin rights): user-space install (pipx/`uv`), no `sudo`, no system-wide writes. Features must avoid anything needing privileges — e.g. `ping`/`troute` use the system `ping`/`traceroute` binaries or an unprivileged mode (like `icmplib`'s), never raw sockets/`scapy`. Config, logs, and data files live in the user's home directory.
- **Config file in TOML**, user-editable by hand or via an interactive `config` command (arrow-key menu, built with `questionary`) that writes the file back out.

## The "helpers" section

A dedicated shared module/package (e.g. `domainscope/helpers/`) for logic reused across more than one check — this is where things like the target-parsing function, a shared configured `requests`/`httpx` session (timeouts, headers, `verify=False` handling), the logging setup, and the section-formatting class (below) live. Individual check modules import from here rather than duplicating small pieces of logic — this is meant to be actively used, not a dumping ground.

## New formatting system (replaces ad hoc `console.print` borders)

The old code hand-writes Unicode border lines (`══════...`) and titles inline, in every check module, with inconsistent spacing and Rich markup easy to get wrong. Replace this with a dedicated formatting class in the helpers module — something like:

```python
class Section:
    def __init__(self, title: str, border_char: str = "─", width: int | None = None):
        ...
    def render(self) -> str:
        # auto-sizes the border to the title length (or a given/terminal width),
        # returns a ready-to-print Rich-formatted string
        ...
```

The point: one object, constructed with a title and a border style, handles its own width/centering/coloring — no check module should ever hand-build a border string again. This should be one of the first pieces built, since every other check's output depends on it.

## Command structure (final short names)

| Command | Purpose |
|---|---|
| `whois` | RDAP-first + classic WHOIS fallback. Domain availability detection (404 → available; `pendingDelete`/`redemptionPeriod` → not yet; otherwise registered, with raw EPP status codes shown). On an IP: IP RDAP (org/netblock/abuse contact) + PTR as a bonus line. |
| `dns` | A/AAAA/MX/NS/TXT/DS/CAA, empty types silently omitted by default. Also handles DNSSEC validation, SOA serial + per-record TTL, multi-resolver propagation check. Fixed, accurate NXDOMAIN messaging (NXDOMAIN ≠ "domain doesn't exist"). Delegation-consistency check (registry NS vs. authoritative NS + glue records) — parked, revisit later. |
| `ssl` | Cipher/expiry/issuer/SANs. Fixed empty-cert-on-verify-failure bug (via `cryptography`, using `getpeercert(binary_form=True)`), timezone-correct expiry math, no crash on timeout/fallback failure. Adds chain-of-trust completeness check and SNI cert-mismatch check. OCSP stapling check — no decision yet. |
| `http` | (was `curlparse`/`http_probe`) Status/headers/cache/UF-PHP detection, working `--redirects`, real TTFB, redirect-loop detection. Adds mixed-content check and broken/missing-image detection (via BeautifulSoup4, with `data-src` lazy-load fallback and content-type verification). CDN detection lives here too, via a plugin system — parked, revisit later. |
| `ptr` | Own top-level command (previously a broken `dns` flag requiring a dummy domain). IPv4 now; IPv6 (`ip6.arpa` nibble reversal) — not yet confirmed. |
| `port` | TCP reachability (open/closed/filtered) with banner grabbing. Presets: `web`, `mail`, `db`, `ssh-ftp`. |
| `troute` | (was `traceroute`) Path diagnostics. |
| `ping` | Latency + packet loss. |
| `geo` | IP geolocation via local GeoLite2 database. Update path: a self-hosted endpoint on the user's own web hosting (language TBD — PHP likely, Python availability unconfirmed) refreshed by cron, auth method TBD. |
| `tld` | (was `tld-status`) Health of a specific TLD's own registry infrastructure (its authoritative NS + RDAP endpoint) — explicitly not the 13 DNS root servers. |
| `le-status` | (was `letsencrypt-status`) Let's Encrypt's public status page + live ACME directory reachability. Explicitly excludes an acme-challenge path check. |
| `rep` | (was `reputation`) Google Safe Browsing (malware/phishing) check. |
| `email` | Full SPF/DKIM/DMARC validation (chain/lookup-limit aware, not just presence) + multi-DNSBL blocklist check. |
| `recon` | Fast composite: `whois` + `dns` (base records) + `ssl` + `http`, run in parallel. Replaces the old, buggy `all` command. |
| `deepscan` | Slower composite: DNSSEC/SOA-TTL/propagation (via `dns` flags) + `email` + `geo` + anything else "more than a quick check." Exact contents to settle during build. |
| `config` | Interactive TOML config editor (arrow-key menu via `questionary`). |

Global flag: `scope --version` (an eager option on the `@app.callback()`), not a `version` command. The version is read from the installed package metadata (`importlib.metadata`), so `pyproject.toml` is the single source of truth.

## Explicitly out of scope (decided during planning, don't reintroduce without asking)

REPL mode, batch/bulk domain input, caching, expiry watch/alerting, diff/history mode, side-by-side domain comparison, WordPress/CMS fingerprinting, SMTP deep check, exposed-sensitive-file scanner, server software fingerprinting, CORS header check, domain-transfer-readiness check, datacenter/region confirmation, headless-browser/JS-error checks, mypy/static typing (for now), auto-formatting tools (for now), authoritative-nameserver-consistency check (propagation check covers this), www/apex consistency check, explicit domain-age surfacing, typosquat/similar-domain check.

## Git / repository workflow

- **Same repository as the existing `Nuksyn/scope` project** — this is a from-scratch architectural rewrite of the same tool, not a fork or a new identity, so the repo, its history, and the old bug-list context stay valuable even though the old code isn't being built on.
- **Freeze the old code first**: `git tag v0.2.0-legacy` on the current `master`, pushed, before any rewrite work starts — this guarantees the old working tool is always recoverable via `git checkout v0.2.0-legacy`, independent of how far the rewrite progresses.
- **All rewrite work happens on a branch** (e.g. `v2-rewrite`), not directly on `master`, so `master` isn't left in a half-broken state while the rewrite is in progress.
- **Merge back to `master` with a regular `git merge`** (not squash) once the rewrite is usable — this preserves each commit's original date, which also matters for GitHub's contribution graph: only commits on the default branch (or `gh-pages`) count toward it, and a squash merge would collapse the whole branch's work into a single commit dated the merge day, losing the graph's reflection of the actual work timeline. A plain merge retroactively fills in the graph with the real commit dates once merged.
- **The user makes all commits and pushes themselves.** Claude doesn't run `git add`/`commit`/`push`; instead it gives the exact commands to run, each with a one-line explanation, plus a suggested commit message.
- Tag the merged result (e.g. `v0.3.0`) once it lands on `master`.
- Before committing on the branch, confirm `git config user.email` matches a **verified email on the GitHub account** — commits with an unverified/mismatched email silently don't count toward the contribution graph, and this is easiest to fix before many commits pile up under the wrong email.

## Tests belong in the repo

- `tests/` sits alongside `src/`, not inside it (`pytest` finds it automatically).
- Any fixture/mock data a test needs (sample DNS responses, fake WHOIS records, recorded HTTP cassettes if `vcr.py`/`pytest-recording` is the chosen mocking approach) is committed too — a test with no fixture to replay against is useless in CI.
- If recorded HTTP cassettes are used, scrub any real secrets/customer data from them before committing — they become permanent repo history once pushed.
- Not committed: test run artifacts (`.pytest_cache/`, `__pycache__/`, `.coverage`, `htmlcov/`) — add these to `.gitignore` alongside the existing `__pycache__/` entry.

## Geo API endpoint (self-hosted) — feasibility note

Confirmed to be a small, low-effort piece once the `.mmdb` file and PHP's `geoip2/geoip2` library are in place — a ~20-30 line PHP script reading the IP from a query param, checking a shared API key, and returning JSON from the MaxMind reader. The two things to confirm before starting that piece: whether **SSH + Composer** is available on the hosting plan (decides whether the library install is one command or a manual drop-in), and where an API key can be stored outside the public webroot on that plan.

## Still open — needs a decision before building the relevant piece

- IP address-family preference (A vs AAAA) when a domain has both, for geo/curl-type checks
- IPv6 support for `ptr`
- CDN detector plugin file/module structure (parked — was mid-discussion)
- Nameserver redundancy/diversity check — no preference given yet
- OCSP stapling check inclusion
- Mocking approach for tests (`unittest.mock` vs `pytest-httpx`/`responses` vs `vcr.py`)
- pipx as the install method — deferred to post-development testing on macOS
- Rich markup escaping — deferred, but flagged as a pre-launch requirement
