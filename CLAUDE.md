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
- **Two demo files per new library, created by Claude, in `sandbox/<library>_demos/`** (grouped by the library they mainly demonstrate, e.g. `sandbox/rich_demos/`; gitignored, never committed):
  - `<library>_demo.py` — the **terminal** version: Claude gives the exact commands to run and what to look for in the output.
  - `<library>_debug.py` — the **PyCharm** version: runs with the plain Run/Debug button, no arguments or setup needed (hardcoded inputs/scenarios), with suggested breakpoint spots so the user can step through it in the debugger.
  - Never name them `test_*.py`: they hit the real network and are not pytest tests (real tests live in `tests/`).
- Claude should proactively suggest a demo/test-in-PyCharm step whenever a new library, pattern, or non-obvious API is introduced, rather than waiting to be asked.
- Claude does not write whole modules or commands for the user. Small illustrative snippets (a few lines, to show a pattern or a library call) are fine; full working implementations are not, even if asked for "just this once."
- Claude keeps asking clarifying/design questions when scope or intent is ambiguous, rather than guessing and building the wrong thing.
- **Keep answers very brief** — short and to the point; expand only when asked.
- **One step at a time:** give the user a single step, wait for it to be done and reviewed, then give the next. Never hand over a numbered list of steps to do all at once.
- **Roadmap and wiring before code, user involved throughout:** before starting a feature or file, Claude gives a short overview of all its steps (what each does and why in that order), and repeats it with a "you are here" marker whenever useful. Before each piece, Claude also shows how it fits in (who calls it, what goes in, what comes out, a tiny flow sketch if useful). The user then builds it in small increments (one method or concept at a time) and runs it after each one. Claude asks a quick check question (e.g. "what do you expect this to print?") before moving on, so the user understands how the parts connect and doesn't just type code.
- **Proactively explain Python concepts** as they come up (e.g. `_` vs `__` naming, `self`, decorators, generators), briefly, without waiting to be asked.
- **Explain every command or test snippet Claude gives**: what each part does, briefly, piece by piece. Never hand over an unexplained one-liner.
- **Every piece of code the user writes gets reviewed by Claude**, and any possible optimisation is pointed out each time (as a short snippet or explanation; the user applies it).
- **Don't repeat yourself:** never write the same logic twice. If something already exists (e.g. in `helpers/`), reuse it. When duplication appears, factor it out.
- **Readability is mandatory:** code must be very easy to read, even where advanced techniques are used. That means clear names, small functions and a short comment wherever a technique isn't obvious. If a clever version is harder to read, prefer the plain one. Imports are grouped (stdlib, blank line, third-party, blank line, local), but **not** sorted alphabetically within a group.
- **Keep this file current.** Whenever the user states a preference or settles a decision (including items under "Still open"), Claude updates the relevant section of this file right away — moving resolved items out of "Still open", replacing outdated statements rather than appending contradictions — and briefly tells the user what changed. Preferences that are personal or must not appear in the public repo go to Claude's local memory instead.

## Architecture principles

- **OOP wherever it makes sense** — this is a hard priority for this rewrite, not a nice-to-have. Prefer classes with methods and typed state over standalone functions passing large parameter lists, wherever the domain naturally supports it.
- **Layered separation, strictly enforced:**
  1. **Typer CLI commands** — parse arguments, validate flag combinations, call into objects. No lookup logic, no printing logic.
  2. **Domain-object methods** — the actual work (network calls, parsing). Never print. Never raise raw library exceptions — catch and re-raise as project-specific exceptions. Always return a typed **dataclass** result, never `None` or a bare bool, and put failures in an `.error` field on that dataclass rather than raising past the method boundary (so one failed check never stops the others). Every result also carries a list of `Finding` objects (see "Findings layer").
  3. **Render functions/classes** — take a result dataclass (+ verbosity level) and produce the terminal output. This is the *only* layer allowed to touch Rich/console output. There are two render paths: the Rich terminal output, and `--json` (machine-readable, including findings).
- **`src/` layout**, `pyproject.toml`-based project, not a flat script folder.
- **Custom exception hierarchy** — one base `DomainScopeError`, with specific subclasses per failure type (e.g. `DnsTimeoutError`, `DnsNxDomainError`, `SslHandshakeError`, `WhoisNotFoundError`, `InvalidTargetError`, itself the parent of `InvalidIpError`/`InvalidDomainError`). Each check module catches the underlying library's exceptions and re-raises its own, so `except DomainScopeError` at a boundary reliably covers every anticipated failure — anything else is a genuine bug and should surface as a real traceback, not be silently swallowed.
- **A single, shared input-normalization entry point.** Every command that takes a domain or IP funnels through one `Target.parse()` classmethod, in `helpers/target.py` (`Target` is an abstract base class, `DomainTarget` and `IPTarget` its frozen-dataclass children, each implementing the abstract `host` property: the string checks connect to and echo; called once, inside the relevant object's `__init__`), which: strips/lowercases, strips protocol and path/port, strips leading and trailing dots from the host (e.g. `.example.com` from cookie/nginx notation, `example.com.` from DNS output), converts IDN to punycode, rejects CIDR ranges (e.g. `1.1.1.0/24`) with `InvalidTargetError` rather than stripping the `/24` as a path, and detects whether the input is actually an IP address (returning a distinct `IPTarget` vs `DomainTarget`, since a bare IP means different things to different checks — e.g. `whois` runs real IP RDAP + PTR on an IP, `dns` rejects/redirects since there's no zone for a bare IP).
- **No caching** — every lookup should hit the network fresh, by explicit decision (the user often re-checks the same domain in one session and wants current data, not a stale cache). **Exception:** reference data (the GeoLite2 database, cloud/crawler IP range lists) is downloaded and stored locally in the user data dir, refreshed periodically. Lookups themselves stay live.
- **Parallel execution for composite commands** — `recon` (and similar) run their sub-checks concurrently via `concurrent.futures.ThreadPoolExecutor`, collecting all results before printing anything (so output stays in a fixed, readable order despite concurrent execution).
- **Always-on, rotating error log** (size- or age-based rotation, e.g. 5MB or 30 days) via the standard `logging` module — every caught exception is logged with domain + traceback, regardless of verbosity. No `--debug` flag for now; that can be added later if needed.
- **Verbosity via counted flags** (`-v`, `-vv`, `-vvv`), read only by the render layer — the underlying check methods always fetch and return full data regardless of verbosity. Default = findings + key facts; `-v` and up = full data.
- **Exit codes:** `0` = OK, `1` = a check failed / problems found, `2` = bad input.
- **External/network-sourced strings must be treated as untrusted** wherever they reach Rich's markup-parsing console output (headers, WHOIS fields, DNS TXT records, etc.) — handled by `Printer`, which builds lines from Rich `Text` objects (never parsed as markup).
- **No root/admin access, ever.** The tool must install and run entirely as a normal user (e.g. on a work Mac without admin rights): user-space install, no `sudo`, no Homebrew, no system-wide writes. Features must avoid anything needing privileges (no raw sockets/`scapy`). Config, logs, and data files live in the user's home directory.
- **Cross-platform: Linux, macOS and Windows.** Every feature must work on all three:
  - Paths use `pathlib`, never hardcoded `/` or `~` strings.
  - Config, log and data directories come from per-OS user directories (e.g. `platformdirs`).
  - **No shelling out to system tools** (`dig`, `whois`, `openssl`, `curl`, `ping`...): pure-Python libraries only.
  - No shell-specific syntax or POSIX-only modules without a fallback.
  - CI runs the tests on all three OSes.
- **Config file in TOML**, user-editable by hand or via an interactive `config` command (arrow-key menu, built with `questionary`) that writes the file back out.

## The "helpers" section

A dedicated shared module/package (e.g. `domainscope/helpers/`) for logic reused across more than one check — this is where things like the target-parsing function, a shared configured **`httpx`** client (timeouts, headers, `verify=False` handling; not `requests`), the logging setup, the config loader, `ProviderRegistry`, `CloudIpMatcher`, and the section-formatting class (below) live. Individual check modules import from here rather than duplicating small pieces of logic — this is meant to be actively used, not a dumping ground.

## Findings layer (cross-cutting)

- Every check result dataclass carries a list of **`Finding`** objects:
  - severity: critical / warning / info;
  - a short code, e.g. `DNSSEC_BROKEN`;
  - a plain-language message: what's wrong and what it means.
- The render layer prints **findings first and prominently**; raw data comes after.
- `recon` applies **correlation rules** across results to surface root causes. Examples:
  - domain on clientHold/serverHold, or expired/in redemption;
  - DNSSEC DS present but the zone is unsigned, or keys mismatched;
  - nameservers at a third-party provider;
  - resolvers disagreeing;
  - cert for a different domain, cert expired or chain incomplete;
  - redirect loop or final 5xx;
  - IPs belonging to a CDN.
- Domain and SSL "expiring soon" are findings (thresholds in config). They're warnings during a normal run, not background monitoring.

## Provider detection (data-driven)

- A **TOML data file** maps patterns to providers:
  - DNS provider (NS suffixes);
  - mail provider (MX suffixes, SPF include domains);
  - parked/for-sale domains (parking-service NS/A patterns);
  - hosted website builders (CNAME targets such as Shopify/Wix/Squarespace), detected from DNS, not HTML.
- Mail-provider entries list their known **DKIM selectors**, so DKIM is checked at the detected provider's selectors (e.g. "Google Workspace detected but no key at `google._domainkey`"). Autodiscover/autoconfig records are checked for the detected mail provider.
- The default file ships **inside the package** (read with `importlib.resources`). An optional user file in the config dir is merged on top.
- A **`ProviderRegistry`** class in helpers loads the data and exposes match methods returning a `Provider` dataclass or `None`. Suffix matching must respect dot boundaries, trailing dots and case.

## Cloud / crawler IP identification

- Uses providers' **official published IP range lists**: AWS, Google Cloud, Cloudflare, Google crawlers, Bing, OpenAI crawlers, and others that publish them. Azure is skipped initially, because its download URL changes weekly.
- The lists are downloaded with httpx (never by shelling out to `curl`) and parsed into one common format: prefix, provider, service, region. They're stored in the user data dir and refreshed periodically (the "no caching" exception above).
- OOP design:
  - a base **`RangeSource`** (`fetch()`, `parse()`) with one subclass per provider;
  - a **`CloudIpMatcher`** in helpers doing longest-prefix match, so a specific service beats AWS's catch-all `AMAZON` entries. It uses the stdlib `ipaddress` module.
- **Crawler verification:** reverse DNS on the IP, then forward DNS on the result, to tell a real Googlebot from a fake one.

## Resolver identity

- Shows which recursive resolver the machine actually uses, via special lookup names (e.g. TXT `o-o.myaddr.l.google.com`, `whoami.akamai.net`). These reveal the real upstream resolver behind a home/office gateway.
- Optionally enriches the resulting IP with the existing whois/geo lookups.

## New formatting system (replaces ad hoc `console.print` borders)

The old code hand-writes Unicode border lines (`══════...`) and titles inline, in every check module, with inconsistent spacing and Rich markup easy to get wrong. Replace this with a dedicated formatting class in the helpers module. The original sketch was a header-only `Section` class (superseded by `Printer` below):

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

**Decided scope (expanded beyond headers):** this is a general-purpose output class — **`Printer`, in `helpers/printer.py`** — used by the render layer for everything it prints:
- section headers (left-aligned title, generic — e.g. "SSL Certificate", **never the domain in the border**), the content lines inside a section, and closing/footer lines; content is left-aligned with no extra indent;
- lines in the old tool's **nmap style**: `[+]` ok / `[!]` warn / `[x]` fail / `[-]` negative/absent / `[*]` info, then `label :: value` — **no emoji/unicode icons**. The marker is **optional per line** and used only where a status matters (e.g. a check passed/failed); plain data lists (e.g. HTTP response headers) have no markers. The empty marker column is kept even when no row has a marker, which gives unmarked rows a one-space indent (deliberate, the user likes it);
- info lines are laid out with **Rich `Table.grid`** (label column auto-sized, long values wrap inside the value column) instead of fixed-width `:<N` padding;
- **automatic marker selection** when requested, via `Status.from_bool(value)` (a classmethod on the enum: `True` → `OK`, `False` → `FAIL`); `line()` itself only takes an explicit status or none. Domain thresholds (e.g. days-to-expiry) are renderer helpers that return a `Status`;
- colours from a named palette (the old tool's palette as a starting point; can be changed freely);
- input echo: one `[*] Target :: example.com` line, printed **once per run, above the first section** (never repeated per section). It shows the parsed (normalised) target; for `recon` the target is parsed once and the same object is shared by all sub-checks;
- **optional prompt support** in the `[?] Question` style (Rich `Prompt`/`Confirm`), meant for the `config` setup wizard, not for normal check output;
- escapes all values by default (untrusted network data), so markup injection / `MarkupError` can't happen;
- width: the **whole output** (header, rows and footer) has one fixed width, a constant of 90 columns, shrinking to the terminal width when the terminal is narrower.

**Decided design:**
- Status is an **`Enum`** (e.g. `Status.OK`, `.WARN`, `.FAIL`, `.ABSENT`, `.INFO`), never plain strings.
- The printer only *displays* a status; **domain thresholds** (e.g. SSL "< 14 days = warn") live with the relevant check/renderer. Generic bool → `[+]`/`[x]` is fine in the printer.
- Colours are named styles in a Rich **`Theme`** (e.g. `"ok"`, `"label"`), not hex codes in strings — later loadable from the TOML config.
- Lines are built with Rich **`Text`** objects, so untrusted data is safe by construction (no reliance on remembering `escape()`).
- **`Printer` creates and owns its own `Console`** (no console injection) and has one job: printing. Tests capture its output with pytest's `capsys` instead.
- Sections are a **context manager**: `with printer.section("SSL Certificate"): ...` resets the rows on enter; `printer.line(label, value, status=None)` only **collects** a row `(status, label, value)`, and the section's grid (header, aligned rows, footer) is printed together when the `with` block ends — a grid needs all rows to size its columns. Internally, `section()` calls small private helpers, `_header(title)` and `_footer()`. The header looks like `════ Title ═════…`: the `═` lead-in and the line are in the `"header"` style and only the title is in the `"title"` style (mint green). The footer is a `═` rule in `"header"`, followed by one blank line to separate sections. **Fixed width:** the console itself is capped at the width constant (90) in `__init__`, so header, rows and footer all share it. It's never wider than the terminal, and never fitted to the content. The header always starts with the `═` lead-in, never with the title.
Prototype of the building blocks: `sandbox/rich_demos/printer_demo.py`.

## Command structure (final short names)

| Command | Purpose |
|---|---|
| `whois` | RDAP-first + classic WHOIS fallback. Domain availability detection (404 → available; `pendingDelete`/`redemptionPeriod` → not yet; otherwise registered, with raw EPP status codes shown). On an IP: IP RDAP (org/netblock/abuse contact) + PTR as a bonus line. |
| `dns` | A/AAAA/CNAME/MX/NS/TXT/DS/CAA by default, empty types silently omitted. `--type` queries any record type (dig replacement), so the DNS code is generic over record types rather than hardcoding the list. `+trace` mode: iterative resolution from the root, showing each delegation step, built as a reusable class. DNSSEC chain shown as a tree from root to domain, marking where it breaks, built on the trace class. Also handles DNSSEC validation, SOA serial + per-record TTL, multi-resolver propagation check. Fixed, accurate NXDOMAIN messaging (NXDOMAIN ≠ "domain doesn't exist"). Delegation-consistency check (registry NS vs. authoritative NS + glue records) — parked, revisit later. |
| `ssl` | Cipher/expiry/issuer/SANs. Fixed empty-cert-on-verify-failure bug (via `cryptography`, using `getpeercert(binary_form=True)`), timezone-correct expiry math, no crash on timeout/fallback failure. Adds chain-of-trust completeness check and SNI cert-mismatch check. `--ip` pinning: connect to a given IP while using the domain for SNI and verification. Certificates on non-web ports (e.g. 465/993/995) and via STARTTLS (e.g. 587/25). OCSP stapling check — no decision yet. |
| `http` | (was `curlparse`/`http_probe`) Status/headers/cache/UF-PHP detection, working `--redirects`, real TTFB, redirect-loop detection. Adds mixed-content check and broken/missing-image detection (via BeautifulSoup4, with `data-src` lazy-load fallback and content-type verification). Built on **httpx**. `--ip` pinning: request the IP with the domain in the `Host` header and httpx's `sni_hostname` request extension. **Never monkeypatch `socket.getaddrinfo`** (process-wide, breaks parallel checks in `recon`). Redirects followed manually (`follow_redirects=False` + own loop); with `--ip`, hops on the same host stay pinned, and the output makes the pinned IP obvious. SEO-spam / cloaking detection: fetch as Googlebot vs. a normal browser and compare content (injected spam links/keywords); fetch with a Google search `Referer` + mobile UA to catch redirects shown only to search visitors. CDN detection — possibly via the provider data file instead of a plugin system (open). |
| `ptr` | Own top-level command (previously a broken `dns` flag requiring a dummy domain). IPv4 now; IPv6 (`ip6.arpa` nibble reversal) — not yet confirmed. |
| `port` | TCP reachability (open/closed/filtered) with banner grabbing. Presets: `web`, `mail`, `db`, `ssh-ftp`. |
| `geo` | IP geolocation via local GeoLite2 database. Update path: the user's own self-hosted API, whose only job is serving the MaxMind GeoLite2 database (cloud range lists don't go through it), on the user's own web hosting (language TBD — PHP likely, Python availability unconfirmed) refreshed by cron, auth method TBD. |
| `email` | Full SPF/DKIM/DMARC validation (chain/lookup-limit aware, not just presence) + multi-DNSBL blocklist check. |
| `recon` | Fast composite: `whois` + `dns` (base records) + `ssl` + `http`, run in parallel. Replaces the old, buggy `all` command. Applies the correlation rules (see "Findings layer"). |
| `deepscan` | Slower composite: DNSSEC/SOA-TTL/propagation (via `dns` flags) + `email` + `geo` + anything else "more than a quick check." Exact contents to settle during build. |
| `config` | Interactive TOML config editor (arrow-key menu via `questionary`). |
| data status (name TBD) | Shows the age of every local data source (GeoLite2, each cloud range list), with a refresh option. |
| resolver identity (placement TBD) | See "Resolver identity" — own command or part of a self-diagnostics command. |

Global flags: `--json` (machine-readable output, a separate render path) and `-v`/`-vv`/`-vvv`. `scope --version` (an eager option on the `@app.callback()`), not a `version` command. The version is read from the installed package metadata (`importlib.metadata`), so `pyproject.toml` is the single source of truth.

## Explicitly out of scope (decided during planning, don't reintroduce without asking)

REPL mode, batch/bulk domain input, caching, expiry watch/alerting, diff/history mode, side-by-side domain comparison, WordPress/CMS fingerprinting, SMTP deep check, exposed-sensitive-file scanner, server software fingerprinting, CORS header check, domain-transfer-readiness check, datacenter/region confirmation, headless-browser/JS-error checks, mypy/static typing (for now), auto-formatting tools (for now), authoritative-nameserver-consistency check (propagation check covers this), www/apex consistency check, explicit domain-age surfacing, typosquat/similar-domain check, `rep` / Google Safe Browsing reputation check (dropped: needs an API key), `ping`, `troute`, `le-status`, `tld` (commands removed), TLS/HTTP protocol version checks, ASN-based lookups, any "hosted with us / not with us" check (this is a generic domain tool, not tied to one hosting company). Docker (not used in this project: no containers, test lab or images).

## Packaging and portability

- Must work on Windows, macOS and Linux **without admin rights and without Homebrew**.
- Standard `pyproject.toml` packaging from day one:
  - console-script entry point in `[project.scripts]`;
  - bundled files via `importlib.resources` (no `__file__` path tricks);
  - all user files (config, logs, data) via `platformdirs`;
  - version read with `importlib.metadata`;
  - `requires-python = ">=3.11"` (needed for `tomllib`).
- Develop with an editable install (`pip install -e .`).
- **Install method, decided at release:** `uv tool install` as the primary path (user-level, can download its own Python), `pipx` compatible, PyInstaller binaries as a fallback if uv is blocked. Requires one test on a real locked-down machine. Later, a CI matrix (Windows/macOS/Linux) tests installation automatically.

## Git / repository workflow

- **Same repository as the existing `Nuksyn/scope` project** — this is a from-scratch architectural rewrite of the same tool, not a fork or a new identity, so the repo, its history, and the old bug-list context stay valuable even though the old code isn't being built on.
- **Freeze the old code first**: `git tag v0.2.0-legacy` on the current `master`, pushed, before any rewrite work starts — this guarantees the old working tool is always recoverable via `git checkout v0.2.0-legacy`, independent of how far the rewrite progresses.
- **All rewrite work happens on a branch** (e.g. `v2-rewrite`), not directly on `master`, so `master` isn't left in a half-broken state while the rewrite is in progress.
- **Merge back to `master` with a regular `git merge`** (not squash) once the rewrite is usable — this preserves each commit's original date, which also matters for GitHub's contribution graph: only commits on the default branch (or `gh-pages`) count toward it, and a squash merge would collapse the whole branch's work into a single commit dated the merge day, losing the graph's reflection of the actual work timeline. A plain merge retroactively fills in the graph with the real commit dates once merged.
- **The user makes all commits and pushes themselves.** Claude doesn't run `git add`/`commit`/`push`; instead it gives the exact commands to run, each with a one-line explanation, plus a suggested commit message.
- Tag the merged result (e.g. `v0.3.0`) once it lands on `master`.
- Before committing on the branch, confirm `git config user.email` matches a **verified email on the GitHub account** — commits with an unverified/mismatched email silently don't count toward the contribution graph, and this is easiest to fix before many commits pile up under the wrong email.

## Tests belong in the repo

- **Every production file gets its pytest tests as soon as the file is complete**, before moving on to the next one: `tests/test_<module>.py`. The user writes them, and Claude guides and reviews. Tests must run in GitHub Actions, which means:
  - no real network;
  - no terminal-size or OS assumptions;
  - passing on Linux, macOS and Windows.
- CI runs on every push and pull request. Planned (set up once the first real test exists):
  - a local git **pre-commit hook** that runs pytest and blocks the commit on failure;
  - **GitHub Actions** CI running pytest on Linux, macOS and Windows;
  - a **branch protection** rule on `master` requiring CI to pass before merging.
- `tests/` sits alongside `src/`, not inside it (`pytest` finds it automatically).
- Any fixture/mock data a test needs (sample DNS responses, fake WHOIS records, recorded HTTP cassettes if `vcr.py`/`pytest-recording` is the chosen mocking approach) is committed too — a test with no fixture to replay against is useless in CI.
- If recorded HTTP cassettes are used, scrub any real secrets/customer data from them before committing — they become permanent repo history once pushed.
- Not committed: test run artifacts (`.pytest_cache/`, `__pycache__/`, `.coverage`, `htmlcov/`) — add these to `.gitignore` alongside the existing `__pycache__/` entry.

## Geo API endpoint (self-hosted) — feasibility note

Confirmed to be a small, low-effort piece once the `.mmdb` file and PHP's `geoip2/geoip2` library are in place — a ~20-30 line PHP script reading the IP from a query param, checking a shared API key, and returning JSON from the MaxMind reader. The two things to confirm before starting that piece: whether **SSH + Composer** is available on the hosting plan (decides whether the library install is one command or a manual drop-in), and where an API key can be stored outside the public webroot on that plan.

## Still open — needs a decision before building the relevant piece

- IP address-family preference (A vs AAAA) when a domain has both, for geo/curl-type checks
- IPv6 support for `ptr`
- CDN detection: may be handled by the provider data file instead of a plugin system
- Nameserver redundancy/diversity check — no preference given yet
- OCSP stapling check inclusion
- Mocking approach for tests (`unittest.mock` vs `pytest-httpx`/`responses` vs `vcr.py`)
- Abstract base classes (e.g. `BaseCheck`, `BaseResult`, `BaseRenderer`) — to discuss later
- SRV records in `dns`: include or not
- With `--ip`, when a redirect leaves the pinned host: follow it via real DNS and flag it, or stop at that hop
- Provider data: one combined file or one per kind; user-override layer from day one or later
- Cloud range list refresh: automatic when older than a day, manual command, or both
- Where resolver identity lives (its own command, or part of a self-diagnostics command)
