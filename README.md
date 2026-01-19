# gitsl

[![CI](https://img.shields.io/github/actions/workflow/status/owner/gitsl/ci.yml?branch=master)](https://github.com/owner/gitsl/actions)
[![PyPI](https://img.shields.io/pypi/v/gitsl)](https://pypi.org/project/gitsl/)
[![Python](https://img.shields.io/pypi/pyversions/gitsl)](https://pypi.org/project/gitsl/)

Git to Sapling CLI shim - translates git commands to their Sapling (sl) equivalents.

## Installation

```bash
pip install gitsl
```

Requires Python 3.8 or later. Requires [Sapling](https://sapling-scm.com/) to be installed and available as `sl`.

## Quick Start

Use familiar git commands in any Sapling repository:

```bash
# Check status (outputs git-compatible format)
gitsl status --porcelain

# View recent commits
gitsl log --oneline -5

# Stage and commit changes
gitsl add -A
gitsl commit -m "Your message"
```

gitsl translates these to equivalent Sapling commands automatically.

## Supported Commands

| Command | Status | Translation |
|---------|--------|-------------|
| `init` | Full | `sl init` |
| `status` | Full | `sl status` with output transformation |
| `log` | Full | `sl log` with flag translation |
| `diff` | Full | `sl diff` |
| `add` | Full | `sl add` / `sl addremove` |
| `commit` | Full | `sl commit` |
| `rev-parse` | Partial | Only `--short HEAD` via `sl whereami` |

Commands not listed are unsupported.

## Command Reference

### git status

| Flag | Supported | Behavior |
|------|-----------|----------|
| (none) | Yes | Passthrough to `sl status` |
| `--porcelain` | Yes | Output transformed to git XY format |
| `--short` / `-s` | Yes | Output transformed to git XY format |
| other flags | Partial | Passed through to sl |

**Status code translation:**

| Sapling | Git | Meaning |
|---------|-----|---------|
| `M` | ` M` | Modified in working tree |
| `A` | `A ` | Added (staged) |
| `R` | `D ` | Removed (staged deletion) |
| `?` | `??` | Untracked |
| `!` | ` D` | Missing (deleted from disk) |

### git log

| Flag | Supported | Translation |
|------|-----------|-------------|
| (none) | Yes | `sl log` |
| `--oneline` | Yes | `sl log -T "{node\|short} {desc\|firstline}\n"` |
| `-N` (e.g., `-5`) | Yes | `sl log -l N` |
| `-n N` | Yes | `sl log -l N` |
| `-nN` | Yes | `sl log -l N` |
| `--max-count=N` | Yes | `sl log -l N` |
| `--format` | No | Not implemented |
| `--graph` | No | Not implemented |

### git add

| Flag | Supported | Translation |
|------|-----------|-------------|
| `<files>` | Yes | `sl add <files>` |
| `-A` / `--all` | Yes | `sl addremove` |
| `-u` / `--update` | Yes | Marks deleted files with `sl remove --mark` |
| `-p` / `--patch` | No | Not implemented |

### git diff, git init, git commit

All flags passed through to sl equivalents unchanged.

### git rev-parse

| Flag | Supported | Translation |
|------|-----------|-------------|
| `--short HEAD` | Yes | `sl whereami` (truncated to 7 chars) |
| other variants | No | Returns error |
