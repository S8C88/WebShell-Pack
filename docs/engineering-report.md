# Engineering Report: WebShell-Pack v1.0

## Overview

**WebShell-Pack** is a minimal web shell generator designed for authorized
post-exploitation assessments. It produces one-liner shells in PHP, ASP, and
JSP with optional authentication and configurable obfuscation.

## Architecture

```
┌──────────┐    ┌──────────────┐    ┌───────────────┐
│   CLI     │───▶│  Generator   │───▶│  Obfuscation  │
│ argparse  │    │  (core)      │    │  Engine       │
└──────────┘    └──────┬───────┘    └───────┬───────┘
                       │                    │
                       ▼                    ▼
                ┌──────────────┐    ┌───────────────┐
                │  PAYLOADS    │    │  Output File  │
                │  dict        │    │  .php/.asp/.jsp│
                └──────────────┘    └───────────────┘
```

### Components

| Module | Responsibility |
|--------|---------------|
| `PAYLOADS` dict | Stores raw template strings for each language |
| `generate()` | Selects template, applies auth, minimal mode |
| `obfuscate()` | Transforms code via variable rename / hex / base64 |
| `save()` | Writes shell to filesystem |
| `cli()` | argparse interface |

## Design Decisions

### Minimal shell philosophy
- PHP shell is 43 bytes raw — `<?php system(base64_decode($_GET['c']));?>`
- Command is base64-encoded to avoid shell metacharacter issues
- No error handling — smallest footprint

### Auth mechanism
- Pre-shared key passed as `k` GET parameter
- Auth check returns `0` on mismatch (same size as valid output)

### Obfuscation levels
- **none**: raw template as-is
- **low**: rename GET parameter names (`c` → `x`, `k` → `a`)
- **medium**: hex-encode function names (`system` → `\x73\x79\x73\x74\x65\x6d`)
- **high**: full base64 eval wrapper (PHP only)

## Security Considerations

1. **Authorized use only** — this tool is for red-team assessments with
   explicit permission
2. **No logging** — shells do not log access by design
3. **No backdoors** — auth is single pre-shared key, no hardcoded backdoors
4. **Obfuscation ≠ encryption** — obfuscation is easily reversed

## File Layout

```
17-WebShell-Pack/
├── webshell_pack.py        # Generator
├── payloads/
│   ├── shell.php           # Raw PHP shell
│   ├── shell.asp           # Raw ASP shell
│   └── shell.jsp           # Raw JSP shell
├── tests/
│   └── test_webshell_pack.py  # 13 test functions
├── docs/
│   └── engineering-report.md
├── README.md
├── LICENSE
├── requirements.txt
└── .gitignore
```

## Test Coverage

13 test functions covering:

| Test | What it validates |
|------|-------------------|
| `test_version` | Version string |
| `test_generate_php_raw` | PHP generation with markers |
| `test_generate_asp_raw` | ASP generation with markers |
| `test_generate_jsp_raw` | JSP generation with markers |
| `test_generate_with_auth` | Auth password inclusion |
| `test_generate_minimal_php` | Minimal mode (no padding) |
| `test_generate_minimal_asp` | Minimal ASP generation |
| `test_generate_minimal_jsp` | Minimal JSP generation |
| `test_obfuscate_none` | No-op obfuscation |
| `test_obfuscate_low` | Variable rename |
| `test_obfuscate_high` | Full base64 eval |
| `test_save_file` | File write round-trip |
| `test_save_creates_directory` | Directory auto-creation |
| `test_payload_files_exist` | Raw payload file presence |
| `test_payload_php_works` | PHP payload contains valid code |
| `test_unsupported_type` | Error on bad type |

## Future Improvements

- Add support for CFM, PL, PY shell types
- Implement WAF bypass techniques (chunked encoding, parameter splitting)
- Add reverse shell payload generation
- Web UI for browser-based generation

---

*Report generated for WebShell-Pack v1.0 — MIT © 2026 S8C88*
