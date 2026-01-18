# Features Research: v1.1 Polish & Documentation

**Domain:** CLI shim packaging and documentation
**Researched:** 2026-01-18
**Research Mode:** Features dimension for v1.1 milestone
**Confidence:** MEDIUM-HIGH

---

## Executive Summary

v1.1 focuses on making gitsl production-ready through comprehensive documentation, improved developer experience, and proper packaging. This research identifies what features and documentation patterns are expected for a well-polished CLI translation tool. The emphasis is on **documentation completeness** and **ease of adoption** rather than new command implementations.

---

## Table Stakes

Features every well-documented CLI package must have. Missing these makes the project feel incomplete or amateur.

### 1. README Structure

| Element | Why Essential | Example |
|---------|---------------|---------|
| **One-liner description** | Instant understanding of purpose | "Git CLI shim that translates commands to Sapling" |
| **Installation instructions** | Users can't use what they can't install | `pip install gitsl` + PATH setup |
| **Quick start example** | First success in < 30 seconds | `git status` works in Sapling repo |
| **Command support matrix** | Know what works before trying | Table showing supported commands |
| **License** | Legal clarity | MIT/Apache 2.0 |

**Source:** [GitHub README guide](https://www.markepear.dev/blog/github-readme-guide), [GitHub CLI patterns](https://cli.github.com/manual/gh)

### 2. Command Support Matrix

A table showing what git commands are supported and their translation status.

**Required columns:**
| Column | Purpose |
|--------|---------|
| Git Command | What user types |
| Status | Supported / Partial / Unsupported |
| Sapling Equivalent | What gets executed |
| Notes | Flags supported, limitations |

**Example format:**
```markdown
| Git Command | Status | Sapling Equivalent | Notes |
|-------------|--------|-------------------|-------|
| `git status` | Full | `sl status` | --porcelain, --short emulated |
| `git add` | Full | `sl add` | -u emulated, -A supported |
| `git commit` | Full | `sl commit` | -m supported |
| `git push` | None | - | Unsupported: different model |
```

### 3. Flag Support Documentation

For each supported command, document which flags work:

**Format per command:**
```markdown
### git status

**Sapling equivalent:** `sl status`

| Flag | Support | Notes |
|------|---------|-------|
| `--porcelain` | Emulated | Output reformatted to git format |
| `--short`, `-s` | Emulated | Same as --porcelain |
| `-u`, `--untracked-files` | Pass-through | Maps to sl -u |
| `--ignored` | Unsupported | Sapling has no equivalent |
```

### 4. Installation Documentation

Multiple installation methods for different users:

| Method | Audience | Required |
|--------|----------|----------|
| `pip install gitsl` | Python users | YES (primary) |
| Manual PATH setup | Power users | YES (documented) |
| Prerequisites (Python 3.8+, Sapling) | All users | YES |

### 5. Error Messages & Help

| Feature | Why Essential |
|---------|---------------|
| `--help` output | Standard CLI expectation |
| `--version` output | Debugging, issue reporting |
| Clear error on unsupported command | User knows what to do next |

**Current status:** v1.0 already has basic --help and --version. Unsupported commands print to stderr and exit 0.

---

## Documentation Patterns

### README Section Structure

Based on best practices from [GitHub README guide](https://www.markepear.dev/blog/github-readme-guide) and [gh cli manual](https://cli.github.com/manual/gh):

```markdown
# gitsl

> Git CLI shim that translates commands to Sapling

[Badges: version, tests, license]

## What is this?

[1-2 paragraph explanation]

## Installation

[pip install + PATH setup]

## Quick Start

[3-step example showing it works]

## Supported Commands

[Command support matrix table]

## Command Reference

[Detailed per-command documentation]

## How It Works

[Brief architecture explanation]

## Development

[How to run tests, contribute]

## License

[MIT]
```

### Command Reference Format

For detailed documentation, use hierarchical structure like gh cli:

```markdown
## Command Reference

### git status

Translates to `sl status` with output format emulation.

**Supported flags:**
- `--porcelain` - Machine-readable output (emulated)
- `--short`, `-s` - Short format (emulated)
- `-u`, `--untracked-files` - Include untracked files

**Examples:**
    git status --porcelain
    git status -s

**Notes:**
- Porcelain output reformats Sapling status codes to git format
- Sapling has no staging area, so index column is always empty
```

### Badges to Include

| Badge | Purpose | Provider |
|-------|---------|----------|
| Version | Current release | PyPI / shields.io |
| Tests | CI status | GitHub Actions |
| License | Legal clarity | shields.io |
| Python version | Compatibility | shields.io |

---

## Git Command Coverage

Based on [common git commands research](https://www.upgrad.com/blog/git-commands-for-developers/) and [GeeksforGeeks command list](https://www.geeksforgeeks.org/git/all-git-commands-you-should-know/), here are ~30 common commands to document:

### Tier 1: Currently Implemented (v1.0)

| # | Command | v1.0 Status | Notes |
|---|---------|-------------|-------|
| 1 | `git status` | Full | --porcelain, --short emulated |
| 2 | `git add` | Full | -u emulated, -A supported |
| 3 | `git commit` | Full | -m supported |
| 4 | `git log` | Full | --oneline emulated, -N supported |
| 5 | `git diff` | Pass-through | Direct mapping |
| 6 | `git init` | Full | Direct mapping |
| 7 | `git rev-parse` | Partial | --short HEAD, basic support |

### Tier 2: High Priority for Documentation (common, likely translatable)

| # | Command | Sapling Equivalent | Translation Notes |
|---|---------|-------------------|-------------------|
| 8 | `git clone` | `sl clone` | Direct mapping |
| 9 | `git pull` | `sl pull` | Direct mapping |
| 10 | `git push` | `sl push` | Direct mapping, may have differences |
| 11 | `git fetch` | `sl pull` | Semantics differ (Sapling pull = git fetch+merge) |
| 12 | `git checkout` | `sl goto` / `sl revert` | Context-dependent |
| 13 | `git switch` | `sl goto` | Modern checkout replacement |
| 14 | `git restore` | `sl revert` | Modern checkout replacement |
| 15 | `git branch` | `sl bookmark` | Different branching model |
| 16 | `git merge` | `sl merge` | Direct mapping |
| 17 | `git rebase` | `sl rebase` | Direct mapping |
| 18 | `git stash` | `sl shelve` | Direct mapping |
| 19 | `git show` | `sl show` | Direct mapping |
| 20 | `git blame` | `sl annotate` | Alias exists: sl blame |
| 21 | `git reset` | `sl uncommit` / `sl revert` | Context-dependent |

### Tier 3: Medium Priority (less common but used)

| # | Command | Sapling Equivalent | Translation Notes |
|---|---------|-------------------|-------------------|
| 22 | `git tag` | `sl bookmark` | Tags are bookmarks in Sapling |
| 23 | `git cherry-pick` | `sl graft` | Direct mapping |
| 24 | `git rm` | `sl remove` | Direct mapping |
| 25 | `git mv` | `sl move` | Direct mapping |
| 26 | `git clean` | `sl clean` | Direct mapping |
| 27 | `git config` | `sl config` | Direct mapping |

### Tier 4: Low Priority / Out of Scope

| # | Command | Why Out of Scope |
|---|---------|-----------------|
| 28 | `git rebase -i` | Interactive mode requires terminal control |
| 29 | `git add -p` | Interactive mode requires terminal control |
| 30 | `git bisect` | Complex workflow, Sapling equivalent unclear |
| 31 | `git worktree` | `sl worktree` exists but different model |
| 32 | `git submodule` | Sapling has different approach |
| 33 | `git filter-branch` | History rewriting, use native Sapling tools |
| 34 | `git reflog` | Sapling uses `sl journal` |

### Documentation Scope for v1.1

**Document ALL 34 commands** with status:
- **Implemented**: Full documentation with flag support
- **Planned**: Sapling equivalent documented, marked for future
- **Out of Scope**: Reason documented, Sapling alternative suggested

This gives users a complete picture of what works now and what to expect.

**Source:** [Sapling commands](https://sapling-scm.com/docs/category/commands/), [Git-Sapling differences](https://sapling-scm.com/docs/introduction/differences-git/)

---

## Differentiators

What makes a CLI shim excellent beyond table stakes.

### 1. Transparent Operation

| Feature | Value |
|---------|-------|
| **Zero config** | Works immediately after PATH setup |
| **Invisible translation** | Tools don't know they're using Sapling |
| **Exact output format** | Porcelain output byte-for-byte identical to git |

**Current status:** v1.0 already achieves this for supported commands.

### 2. Excellent Debug Mode

| Feature | Value |
|---------|-------|
| `GITSL_DEBUG=1` shows translation | Users understand what happens |
| Clear unsupported command messages | No silent failures |
| Version includes both gitsl and sl versions | Issue reporting easier |

**Current status:** GITSL_DEBUG exists. Could enhance version output.

### 3. Comprehensive Command Matrix

Most CLI shims have incomplete documentation. A complete matrix covering:
- Every common git command
- Each command's flags
- Explicit "unsupported" status with reasons
- Sapling alternative suggestions

**This is v1.1's main differentiator.**

### 4. Test Runner UX

| Feature | Value |
|---------|-------|
| `./test` runs all tests | Simple CI-like experience |
| `./test status` runs specific command tests | Fast iteration |
| Clear output | Easy to understand results |

**Current status:** Uses pytest. v1.1 should add convenient wrappers.

### 5. Cross-Platform CI

| Feature | Value |
|---------|-------|
| GitHub Actions for macOS/Linux/Windows | Trust it works everywhere |
| Badges showing status | Visual confidence |

---

## Anti-Features

Things to explicitly avoid in v1.1.

### 1. Implementing More Commands

**Why avoid:** v1.1 is about polish, not expansion.

- v1.0 covers the essential commands
- Adding commands increases maintenance burden
- Documentation is the priority

**Instead:** Document what's supported, planned, and out of scope.

### 2. Complex Installation Methods

**Why avoid:**
- Homebrew tap requires maintenance
- Conda package adds complexity
- Shell scripts are fragile

**Instead:** Focus on `pip install` and clear manual PATH instructions.

### 3. Automatic Updates

**Why avoid:**
- Adds network calls
- Security concerns
- Complexity for minimal value

**Instead:** Document version checking with `pip list --outdated`.

### 4. Extensive Configuration

**Why avoid:**
- Users expect git config, not custom config
- Configuration files add complexity
- Per-repo configuration is maintenance burden

**Instead:** Environment variables for the few settings needed (GITSL_DEBUG).

### 5. GUI/TUI Components

**Why avoid:**
- Violates CLI-only scope
- Dependency on terminal libraries
- Complexity for edge case

**Instead:** Focus on command-line excellence.

### 6. Logo/Branding Investment

**Why avoid for v1.1:**
- Time spent on logos is time not spent on documentation
- Project is functional, not a product needing marketing

**Instead:** Simple text README with clear documentation.

---

## v1.1 Feature Prioritization

### P0 - Must Have (Core Deliverables)

| Feature | Rationale |
|---------|-----------|
| **Command support matrix in README** | Primary user need |
| **Per-command flag documentation** | Users need to know what works |
| **PyPI package** | `pip install gitsl` |
| **Test runner convenience** | `./test` and `./test <cmd>` |
| **GitHub Actions CI** | Build trust, catch regressions |

### P1 - Should Have

| Feature | Rationale |
|---------|-----------|
| **Badges in README** | Visual trust signals |
| **Contributing guide** | Community growth |
| **Architecture section** | Developer onboarding |
| **Installation troubleshooting** | Common issues documented |

### P2 - Nice to Have

| Feature | Rationale |
|---------|-----------|
| **GIF demo in README** | Visual quick-start |
| **Changelog** | Track versions |
| **Comparison with alternatives** | Why gitsl vs git-to-sl |

---

## Sources

- [GitHub README guide](https://www.markepear.dev/blog/github-readme-guide) - README structure patterns
- [gh CLI manual](https://cli.github.com/manual/gh) - Command documentation format
- [Top 28 Git Commands](https://www.upgrad.com/blog/git-commands-for-developers/) - Common command list
- [All Git Commands](https://www.geeksforgeeks.org/git/all-git-commands-you-should-know/) - Categorized command reference
- [Sapling commands](https://sapling-scm.com/docs/category/commands/) - Sapling command reference
- [Sapling basic commands](https://sapling-scm.com/docs/overview/basic-commands/) - Core Sapling operations
- [Sapling differences from Git](https://sapling-scm.com/docs/introduction/differences-git/) - Translation guidance
- [GitHub CLI topics](https://github.com/topics/cli-tool) - CLI documentation patterns
