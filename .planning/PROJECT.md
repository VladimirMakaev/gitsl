# GitSL

## What This Is

A Python package that acts as a git CLI shim, intercepting git commands and translating them to equivalent Sapling (sl) commands. Designed to allow tools that expect git (like get-shit-done) to work transparently with Sapling repositories.

**Architecture:**
- `gitsl.py` — Entry point only (receives argv, dispatches to command handlers)
- `common.py` — Shared logic (parsing, subprocess handling, debug mode)
- One file per command (e.g., `cmd_status.py`, `cmd_commit.py`)

## Core Value

Git commands used by get-shit-done execute correctly against Sapling repos without the calling tool knowing the difference.

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] Script intercepts git commands from argv
- [ ] `git status` translates to `sl status`
- [ ] `git status --short` emulates git's short format from sl output
- [ ] `git status --porcelain` emulates git's porcelain format exactly
- [ ] `git add <files>` translates to `sl add <files>`
- [ ] `git add -u` emulates by finding modified tracked files and adding them
- [ ] `git add -A` translates to `sl addremove`
- [ ] `git commit -m "msg"` translates to `sl commit -m "msg"`
- [ ] `git log` translates to `sl log`
- [ ] `git log -N` translates to `sl log -l N`
- [ ] `git log --oneline` emulates git's oneline format from sl output
- [ ] `git diff` translates to `sl diff` (pass-through)
- [ ] `git rev-parse --short HEAD` translates to `sl whereami`
- [ ] `git init` translates to `sl init`
- [ ] Unsupported commands print original command to stderr and exit 0

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
| Exit 0 on unsupported commands | Prevent calling CLI from failing | — Pending |
| Emulate porcelain exactly | GSD may parse this output | — Pending |
| Pass-through diff output | User confirmed no parsing of diff | — Pending |

---
*Last updated: 2026-01-17 after initialization*
