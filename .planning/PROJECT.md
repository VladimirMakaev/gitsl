# GitSL

## What This Is

A Python package that acts as a git CLI shim, intercepting git commands and translating them to equivalent Sapling (sl) commands. Designed to allow tools that expect git (like get-shit-done) to work transparently with Sapling repositories.

**Architecture:**
- `gitsl.py` — Entry point only (receives argv, dispatches to command handlers)
- `common.py` — Shared logic (parsing, subprocess handling, debug mode)
- One file per command (e.g., `cmd_status.py`, `cmd_commit.py`)

## Core Value

Git commands used by get-shit-done execute correctly against Sapling repos without the calling tool knowing the difference.

## Current State

**Shipped:** v1.0 MVP (2026-01-18)
**Lines of Code:** 1,984 Python
**Tests:** 91 passing
**Requirements:** 32/32 complete

## Requirements

### Validated

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

### Active

(None — ready for next milestone)

### Out of Scope

- Matching git diff output format exactly — pass-through is sufficient
- Porcelain flags for any command — only human-readable flags supported
- OAuth/authentication handling — Sapling handles this
- Remote operations (push/pull/fetch) — print to stderr as unsupported
- Branch operations — print to stderr as unsupported
- Interactive commands (rebase -i, add -p) — print to stderr as unsupported

## Context

**Target use case:** The get-shit-done CLI tool (github.com/glittercowboy/get-shit-done) calls git commands internally. By placing this shim earlier in PATH, those git calls get redirected to Sapling.

**Git commands used by get-shit-done:**
- `git status --short` / `git status --porcelain` — check repo state
- `git add <files>` / `git add -u` / `git add -A` — stage changes
- `git commit -m "..."` — create commits (multi-line messages via heredoc)
- `git log --oneline -N` — view recent commits
- `git rev-parse --short HEAD` — get current commit hash
- `git init` — initialize repo
- `git diff` — not actually used by GSD, but included for completeness

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
- **No dependencies**: Standard library only — no pip installs
- **Python 3**: Assume Python 3.8+ available
- **Sapling installed**: Assume `sl` command is available in PATH

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Multi-file architecture | Easier to maintain, one file per command | Adopted 2026-01-18 |
| Exit 0 on unsupported commands | Prevent calling CLI from failing | ✓ Good |
| Emulate porcelain exactly | GSD may parse this output | ✓ Good |
| Pass-through diff output | User confirmed no parsing of diff | ✓ Good |
| Manual argv parsing | argparse doesn't handle git-style subcommands well | ✓ Good |
| GITSL_DEBUG via env var | Avoid consuming CLI args | ✓ Good |
| subprocess.run() no PIPE | Real-time I/O passthrough | ✓ Good |

---
*Last updated: 2026-01-18 after v1.0 milestone*
