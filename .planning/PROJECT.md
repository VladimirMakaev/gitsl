# GitSL

## What This Is

A Python package that acts as a git CLI shim, intercepting git commands and translating them to equivalent Sapling (sl) commands. Allows any tool that expects git to work transparently with Sapling repositories.

**Architecture:**
- `gitsl.py` — Entry point only (receives argv, dispatches to command handlers)
- `common.py` — Shared logic (parsing, subprocess handling, debug mode)
- One file per command (e.g., `cmd_status.py`, `cmd_commit.py`)

## Core Value

Git commands execute correctly against Sapling repos without the calling tool knowing the difference.

## Current State

**Shipped:** v1.1 (2026-01-19)
**PyPI:** https://pypi.org/project/gitsl/
**Lines of Code:** 3,131 Python
**Tests:** 124 passing (parallel, cross-platform)

## Requirements

### Validated

**v1.0 Core Commands:**
- ✓ Script intercepts git commands from argv — v1.0
- ✓ `git status` translates to `sl status` — v1.0
- ✓ `git status --short` emulates git's short format from sl output — v1.0
- ✓ `git status --porcelain` emulates git's porcelain format exactly — v1.0
- ✓ `git add <files>` translates to `sl add <files>` — v1.0
- ✓ `git add -u` emulates by finding modified tracked files and adding them — v1.0
- ✓ `git add -A` translates to `sl addremove` — v1.0
- ✓ `git commit -m "msg"` translates to `sl commit -m "msg"` — v1.0
- ✓ `git log` translates to `sl log` — v1.0
- ✓ `git log -N` translates to `sl log -l N` — v1.0
- ✓ `git log --oneline` emulates git's oneline format from sl output — v1.0
- ✓ `git diff` translates to `sl diff` (pass-through) — v1.0
- ✓ `git rev-parse --short HEAD` translates to `sl whereami` — v1.0
- ✓ `git init` translates to `sl init` — v1.0
- ✓ Unsupported commands print original command to stderr and exit 0 — v1.0

**v1.1 Polish & Documentation:**
- ✓ Cross-platform test runner (`./test`, `./test <command>`) — v1.1
- ✓ 124 tests including edge cases and error conditions — v1.1
- ✓ pip-installable package with pyproject.toml — v1.1
- ✓ GitHub Actions CI (Linux, macOS, Windows × Python 3.9/3.11/3.13) — v1.1
- ✓ PyPI trusted publishing with OIDC — v1.1
- ✓ Production README with badges and command documentation — v1.1

### Active

None — planning next milestone.

### Out of Scope

- Matching git diff output format exactly — pass-through is sufficient
- OAuth/authentication handling — Sapling handles this
- Remote operations (push/pull/fetch) — Sapling model differs fundamentally
- Interactive commands (rebase -i, add -p) — require terminal control

## Context

**Target use case:** Any tool that calls git commands internally can work with Sapling repos by placing this shim earlier in PATH.

**Sapling command mappings:**
| Git | Sapling | Notes |
|-----|---------|-------|
| `git status` | `sl status` | Output format similar |
| `git add <files>` | `sl add <files>` | Direct |
| `git add -A` | `sl addremove` | Different command |
| `git commit -m` | `sl commit -m` | Direct |
| `git log -N` | `sl log -l N` | Different flag |
| `git rev-parse --short HEAD` | `sl whereami` | Different command |
| `git init` | `sl init` | Direct |
| `git diff` | `sl diff` | Direct |

**Emulation required for:**
- `--porcelain` / `--short` on status — reformat sl output to match git exactly
- `-u` on add — find modified tracked files via `sl status -m`, then add
- `--oneline` on log — reformat sl output to `<hash> <subject>` format

## Constraints

- **Multi-file package**: Entry point in gitsl.py, shared logic in common.py, one file per command
- **No runtime dependencies**: Standard library only for core functionality
- **Python 3**: Python 3.9+ required
- **Sapling installed**: Assume `sl` command is available in PATH
- **Cross-platform**: Must work on MacOS, Linux, Windows

## Development Guidelines

**When making changes that affect compatibility or features:**

1. **Update README.md command support matrix** — When adding/modifying/removing command support, update the compatibility matrix in README.md
2. **Update Python version compatibility** — When using new Python features, verify they work on all supported versions (3.9+) and update docs if min version changes
3. **Update CI matrix** — When platform behavior differs (e.g., OSS vs Homebrew Sapling), ensure CI tests cover all variants
4. **Use Optional[X] not X | None** — For Python 3.9 compatibility (union operator added in 3.10)
5. **Test with OSS Sapling** — Local testing may use different Sapling version than CI; OSS Sapling creates `.sl`, Homebrew creates `.hg`

**Checking CI Status (GitHub Actions):**

```bash
# List recent workflow runs
curl -s "https://api.github.com/repos/VladimirMakaev/gitsl/actions/runs?per_page=5" | \
  python3 -c "import json,sys; [print(f\"{r['id']} | {r['status']:12} | {r['conclusion'] or 'pending':10} | {r['head_sha'][:7]}\") for r in json.load(sys.stdin).get('workflow_runs',[])]"

# Check specific run's jobs
curl -s "https://api.github.com/repos/VladimirMakaev/gitsl/actions/runs/<RUN_ID>/jobs" | \
  python3 -c "import json,sys; [print(f\"{j['name']:40} | {j['status']:12} | {j['conclusion'] or 'pending'}\") for j in json.load(sys.stdin).get('jobs',[])]"

# Web URL for CI runs
# https://github.com/VladimirMakaev/gitsl/actions
```

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Multi-file architecture | Easier to maintain, one file per command | ✓ Good |
| Exit 0 on unsupported commands | Prevent calling CLI from failing | ✓ Good |
| Emulate porcelain exactly | Tools may parse this output | ✓ Good |
| Pass-through diff output | No parsing of diff needed | ✓ Good |
| Manual argv parsing | argparse doesn't handle git-style subcommands well | ✓ Good |
| GITSL_DEBUG via env var | Avoid consuming CLI args | ✓ Good |
| subprocess.run() no PIPE | Real-time I/O passthrough | ✓ Good |
| pyproject.toml with setuptools | Modern packaging, flat layout | ✓ Good |
| OIDC trusted publishing | No API tokens in secrets | ✓ Good |
| Parallel tests with pytest-xdist | 4x faster test execution | ✓ Good |

---
*Last updated: 2026-01-19 after v1.1 milestone completion*
