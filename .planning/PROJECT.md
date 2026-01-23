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

**Shipped:** v1.3 (2026-01-23)
**PyPI:** https://pypi.org/project/gitsl/
**Lines of Code:** 3,247 Python (source), 7,169 tests
**Tests:** 480 passing (parallel, cross-platform)

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

**v1.2 More Commands Support:**
- ✓ `git show [commit]` translates to `sl show` — v1.2
- ✓ `git blame <file>` translates to `sl annotate` — v1.2
- ✓ `git rm <files>` translates to `sl remove` — v1.2
- ✓ `git mv <src> <dst>` translates to `sl rename` — v1.2
- ✓ `git clean -f [-d]` translates to `sl purge` with safety validation — v1.2
- ✓ `git clone <url> [dir]` translates to `sl clone` — v1.2
- ✓ `git grep <pattern>` translates to `sl grep` — v1.2
- ✓ `git config [options]` translates to `sl config` — v1.2
- ✓ `git stash` translates to `sl shelve` — v1.2
- ✓ `git stash pop` translates to `sl unshelve` — v1.2
- ✓ `git stash list` translates to `sl shelve --list` — v1.2
- ✓ `git stash drop` translates to `sl shelve --delete` — v1.2
- ✓ `git stash apply` translates to `sl unshelve --keep` — v1.2
- ✓ `git checkout <commit>` translates to `sl goto` — v1.2
- ✓ `git checkout <file>` translates to `sl revert <file>` — v1.2
- ✓ `git checkout -b <branch>` translates to `sl bookmark <name>` + `sl goto` — v1.2
- ✓ `git switch <branch>` translates to `sl goto` — v1.2
- ✓ `git restore <file>` translates to `sl revert <file>` — v1.2
- ✓ `git branch` lists bookmarks via `sl bookmark` — v1.2
- ✓ `git branch <name>` creates bookmark via `sl bookmark <name>` — v1.2
- ✓ `git branch -d/-D <name>` deletes bookmark safely (D→d translation) — v1.2
- ✓ Checkout disambiguates between commit/branch/file correctly — v1.2

**v1.3 Flag Compatibility:**
- ✓ 191 flags implemented across 19 git commands — v1.3
- ✓ Critical safety: commit -a removed, checkout -f→-C, checkout -m→-m — v1.3
- ✓ Rev-parse expansion: --show-toplevel, --git-dir, --is-inside-work-tree, --abbrev-ref HEAD — v1.3
- ✓ Log flags: --graph, --stat, --author, --since/--until, --pretty/--format, 20 flags total — v1.3
- ✓ Diff/show flags: --name-only, --name-status, staging area warnings, 20 flags total — v1.3
- ✓ Stash/checkout/switch/restore: stash@{n} syntax, 21 flags — v1.3
- ✓ Grep/blame: -v→-V translation, -b→--ignore-space-change, 21 flags — v1.3
- ✓ Clone/rm/mv/clean/config: --branch, --depth, --unset, 30 flags — v1.3
- ✓ Complete README flag documentation with staging area limitations — v1.3

### Active

**v1.4 Planning:**
- [ ] User feedback and v1.4 planning (potential: worktree support, remote operations)

## Current Milestone: v1.4 (Planning)

**Goal:** User feedback and improvements based on v1.3 usage.

**Potential scope:**
- Worktree support
- Remote operation improvements
- User-requested features

### Out of Scope

- Matching git diff output format exactly — pass-through is sufficient
- OAuth/authentication handling — Sapling handles this
- Remote operations (push/pull/fetch) — Sapling model differs fundamentally
- Interactive commands (rebase -i, add -p) — require terminal control
- `git merge` — Sapling prefers rebase workflow
- `git rebase` — complex flag translation, use sl rebase directly

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
| `git show` | `sl show` | Direct |
| `git blame` | `sl annotate` | Different command |
| `git rm` | `sl remove` | Different command |
| `git mv` | `sl rename` | Different command |
| `git clean` | `sl purge` | Different command |
| `git clone` | `sl clone` | Direct |
| `git grep` | `sl grep` | Direct |
| `git config` | `sl config` | Direct |
| `git stash` | `sl shelve` | Different command |
| `git stash pop` | `sl unshelve` | Different command |
| `git checkout <commit>` | `sl goto` | Different command |
| `git checkout <file>` | `sl revert` | Different semantics |
| `git switch` | `sl goto` | Different command |
| `git restore` | `sl revert` | Different command |
| `git branch` | `sl bookmark` | Different model |

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
| Safety validation for clean | Enforce -f/-n before sl purge | ✓ Good |
| Translate -D to -d for branch delete | Prevent sl bookmark -D from stripping commits | ✓ Good |
| Subcommand dispatch for stash | Handle push/pop/apply/list/drop patterns | ✓ Good |
| Checkout disambiguation via sl log -r | Use exit code to validate revision | ✓ Good |
| Error on ambiguity (file=revision) | Explicit error better than silent priority | ✓ Good |
| Remove -a/--all from commit | Semantic difference too dangerous (would add untracked) | ✓ Good |
| Translate checkout -f to -C | Match sl goto -C semantics | ✓ Good |
| Parse stash@{n} and lookup shelve name | Map git index notation to sl shelve names | ✓ Good |
| Translate grep -v to -V | sl uses uppercase V for invert match | ✓ Good |
| Translate blame -b to --ignore-space-change | sl -b means blank SHA1, not ignore blanks | ✓ Good |
| Translate config --global to --user | sl uses --user for user-level config | ✓ Good |
| Translate clone -b to -u | sl uses -u for checkout bookmark | ✓ Good |

---
*Last updated: 2026-01-23 after v1.3 milestone shipped*
