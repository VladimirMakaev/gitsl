# Phase 14: Documentation - Research

**Researched:** 2026-01-19
**Domain:** README documentation, Markdown formatting, shields.io badges, CLI documentation patterns
**Confidence:** HIGH

## Summary

This phase creates production-quality README documentation for gitsl, a Git-to-Sapling CLI shim. The README must serve multiple audiences: users who want quick installation and usage, developers who need to understand command support, and tools/bots that parse badges for status information.

The documentation pattern follows established Python CLI tool conventions (Black, Ruff): badges at top, installation first, quick start example, then detailed reference tables. For command compatibility documentation, we use a command matrix table showing supported/unsupported commands, followed by per-command flag documentation with support status and translation notes.

**Primary recommendation:** Structure the README with badges (CI, PyPI version, Python versions), installation via pip, quick start example, command support matrix, per-command flag tables, and explanation of unsupported command behavior.

## Standard Stack

The established tools for Python CLI documentation:

### Core
| Tool | Purpose | Why Standard |
|------|---------|--------------|
| shields.io | Badge generation | Industry standard, dynamic updates |
| Markdown tables | Command matrices | Native GitHub rendering, copyable |
| Code blocks | Usage examples | Syntax highlighting, easy to follow |

### Badge Services
| Badge | URL Pattern | Purpose |
|-------|-------------|---------|
| CI Status | `https://img.shields.io/github/actions/workflow/status/{owner}/{repo}/{workflow}` | Build status |
| PyPI Version | `https://img.shields.io/pypi/v/{package}` | Current version |
| Python Versions | `https://img.shields.io/pypi/pyversions/{package}` | Compatibility |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| shields.io | GitHub native badges | Less customizable, fewer options |
| Markdown tables | HTML tables | Harder to maintain, same rendering |
| Single README | docs/ folder | Overkill for single-purpose CLI |

## Architecture Patterns

### Recommended README Structure
```
README.md
├── Badges (CI, PyPI, Python)
├── One-line description
├── Installation
│   └── pip install gitsl
├── Quick Start
│   └── 2-3 example commands
├── Command Support Matrix
│   └── Table: command | status | notes
├── Flag Documentation (per command)
│   └── Sub-tables for each command
├── Unsupported Commands
│   └── Behavior explanation
├── Debug Mode
│   └── GITSL_DEBUG usage
├── How It Works
│   └── Brief architecture explanation
└── Contributing / License
```

### Pattern 1: Badge Row at Top
**What:** Horizontal row of badges immediately after title
**When to use:** All open-source Python packages
**Example:**
```markdown
# gitsl

[![CI](https://img.shields.io/github/actions/workflow/status/owner/gitsl/ci.yml?branch=master)](https://github.com/owner/gitsl/actions)
[![PyPI](https://img.shields.io/pypi/v/gitsl)](https://pypi.org/project/gitsl/)
[![Python](https://img.shields.io/pypi/pyversions/gitsl)](https://pypi.org/project/gitsl/)

Git to Sapling CLI shim - translates git commands to their Sapling (sl) equivalents.
```

### Pattern 2: Command Support Matrix
**What:** Table showing all git commands and their support status
**When to use:** Compatibility/shim documentation
**Example:**
```markdown
## Supported Commands

| Git Command | Status | Notes |
|-------------|--------|-------|
| `git status` | Supported | Full porcelain/short output emulation |
| `git log` | Supported | --oneline and -N flags translated |
| `git diff` | Supported | Direct passthrough to `sl diff` |
| `git init` | Supported | Direct passthrough to `sl init` |
| `git add` | Supported | -A/--all and -u/--update handled |
| `git commit` | Supported | Direct passthrough to `sl commit` |
| `git rev-parse` | Partial | Only `--short HEAD` supported |
| `git branch` | Not supported | Use `sl bookmark` directly |
| `git checkout` | Not supported | Use `sl goto` directly |
```

### Pattern 3: Per-Command Flag Documentation
**What:** Detailed flag support for each command
**When to use:** When commands have partial flag support
**Example:**
```markdown
### git status

| Flag | Supported | Translation |
|------|-----------|-------------|
| (no flags) | Yes | `sl status` |
| `--porcelain` | Yes | Output transformed to git format |
| `--short` / `-s` | Yes | Output transformed to git format |
| `--branch` | No | Not implemented |
```

### Pattern 4: Quick Start with Progressive Disclosure
**What:** Minimal example first, then link to details
**When to use:** CLI tools with many options
**Example:**
```markdown
## Quick Start

```bash
# In a Sapling repository, use git commands:
gitsl status
gitsl log --oneline -5
gitsl diff
```

See [Command Reference](#supported-commands) for full documentation.
```

### Anti-Patterns to Avoid
- **Wall of text before examples:** Users want to see usage immediately
- **Undocumented partial support:** Explicitly state what flags ARE and ARE NOT supported
- **Missing unsupported command behavior:** Document that unsupported commands print to stderr and exit 0
- **Broken badge links:** Use correct owner/repo values (update from template)

## Don't Hand-Roll

Problems with existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Dynamic badges | Static images | shields.io dynamic badges | Auto-update on release |
| Badge HTML | Raw HTML | Markdown image syntax | Simpler, portable |
| Version in README | Manual update | Link to PyPI page | Single source of truth |
| Exhaustive docs | Everything in README | Link to Sapling docs | Focus on translation, not git/sl docs |

**Key insight:** README should document WHAT gitsl translates and HOW, not replicate git or Sapling documentation.

## Common Pitfalls

### Pitfall 1: Badge Links Before Repository Exists
**What goes wrong:** Badges show "not found" or fail to load
**Why it happens:** Using placeholder owner/repo values
**How to avoid:** Update badge URLs after confirming final GitHub URL
**Warning signs:** Broken image placeholders in README

### Pitfall 2: Undocumented Unsupported Command Behavior
**What goes wrong:** Users confused when commands "fail silently"
**Why it happens:** Unsupported commands exit 0 to not break tooling
**How to avoid:** Explicitly document this behavior with example
**Warning signs:** Issues filed about "broken" commands

### Pitfall 3: Flag Documentation Drift
**What goes wrong:** README lists flags that don't work, or misses new flags
**Why it happens:** Code changes without doc updates
**How to avoid:** Generate flag tables from code analysis, or add verification
**Warning signs:** User reports of incorrect documentation

### Pitfall 4: Missing Python Version Range
**What goes wrong:** Users on unsupported Python versions file issues
**Why it happens:** pyproject.toml says >=3.8, but README doesn't clarify
**How to avoid:** Include Python version requirement prominently
**Warning signs:** Support requests for Python 3.7 or 2.7

### Pitfall 5: Workflow File Name Mismatch
**What goes wrong:** CI badge shows "not found"
**Why it happens:** Badge URL references wrong workflow filename
**How to avoid:** Verify workflow filename matches (ci.yml not test.yml)
**Warning signs:** Badge loads but shows error state

## Code Examples

Verified patterns from official sources and project analysis:

### Complete Badge Section
```markdown
# gitsl

[![CI](https://img.shields.io/github/actions/workflow/status/OWNER/gitsl/ci.yml?branch=master)](https://github.com/OWNER/gitsl/actions)
[![PyPI](https://img.shields.io/pypi/v/gitsl)](https://pypi.org/project/gitsl/)
[![Python](https://img.shields.io/pypi/pyversions/gitsl)](https://pypi.org/project/gitsl/)
```

Note: Replace `OWNER` with actual GitHub username/organization.

### Installation Section
```markdown
## Installation

```bash
pip install gitsl
```

Requires Python 3.8 or later. Requires [Sapling](https://sapling-scm.com/) to be installed and available as `sl`.
```

### Quick Start Section
```markdown
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
```

### Command Support Matrix (Based on Project Code)
```markdown
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

Commands not listed are unsupported and will print a message to stderr.
```

### Per-Command Flag Table (git status)
```markdown
### git status

| Flag | Supported | Behavior |
|------|-----------|----------|
| (none) | Yes | Passthrough to `sl status` |
| `--porcelain` | Yes | Output transformed to git XY format |
| `--short` / `-s` | Yes | Output transformed to git XY format |
| `--branch` | No | Not implemented |
| `--ignored` | Partial | Passed through, mapping may be incomplete |

**Status code translation:**
| Sapling | Git | Meaning |
|---------|-----|---------|
| `M` | ` M` | Modified (working tree) |
| `A` | `A ` | Added (staged) |
| `R` | `D ` | Removed (staged deletion) |
| `?` | `??` | Untracked |
| `!` | ` D` | Missing (deleted from disk) |
```

### Per-Command Flag Table (git log)
```markdown
### git log

| Flag | Supported | Translation |
|------|-----------|-------------|
| (none) | Yes | `sl log` |
| `--oneline` | Yes | `sl log -T "{node|short} {desc|firstline}\n"` |
| `-N` (e.g., `-5`) | Yes | `sl log -l N` |
| `-n N` | Yes | `sl log -l N` |
| `--max-count=N` | Yes | `sl log -l N` |
| `--format` | No | Not implemented |
| `--graph` | No | Not implemented |
```

### Per-Command Flag Table (git add)
```markdown
### git add

| Flag | Supported | Translation |
|------|-----------|-------------|
| `<files>` | Yes | `sl add <files>` |
| `-A` / `--all` | Yes | `sl addremove` |
| `-u` / `--update` | Yes | Mark deleted files with `sl remove --mark` |
| `-p` / `--patch` | No | Not implemented (use `sl commit -i`) |
```

### Unsupported Commands Section
```markdown
## Unsupported Commands

Commands not listed above will print a message to stderr and exit with code 0:

```
gitsl: unsupported command: git checkout main
```

This exit behavior prevents gitsl from breaking tools that expect git commands to succeed.

For unsupported operations, use Sapling commands directly. See the [Sapling Git Cheat Sheet](https://sapling-scm.com/docs/introduction/git-cheat-sheet/) for translations.

### Why Some Commands Are Unsupported

| Command | Reason |
|---------|--------|
| `checkout` | Sapling uses `goto` (different semantics) |
| `branch` | Sapling uses bookmarks, different model |
| `merge` | Sapling prefers rebase workflow |
| `rebase` | Complex flag translation, use `sl rebase` |
| `stash` | Use `sl shelve` / `sl unshelve` directly |
| `fetch` / `pull` / `push` | Remote operations differ significantly |
```

### Debug Mode Section
```markdown
## Debug Mode

Set `GITSL_DEBUG=1` to see what command would be executed without running it:

```bash
$ GITSL_DEBUG=1 gitsl status --porcelain
[DEBUG] Command: status
[DEBUG] Args: ['--porcelain']
[DEBUG] Would execute: sl status
```
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| GitHub Actions badge via static URL | shields.io dynamic | 2020+ | Auto-updates |
| img.shields.io/travis | GitHub Actions badges | 2022+ (Travis sunset) | Use new URL pattern |
| Version in README | PyPI badge | Always | Single source of truth |
| Exhaustive README | Link to external docs | Always | Maintainability |

**Deprecated/outdated:**
- Travis CI badges: Travis largely deprecated for open source
- Static version numbers in README: Always use dynamic badges or links
- Codecov for simple projects: Only add if actually tracking coverage

## Documentation Requirements Analysis

Based on project requirements (DOC-01 through DOC-08):

| Requirement | Content Needed |
|-------------|----------------|
| DOC-01: Installation | `pip install gitsl` section |
| DOC-02: Quick start | 3-4 example commands |
| DOC-03: Command matrix | Table of all commands with status |
| DOC-04: Flag documentation | Per-command flag tables |
| DOC-05: Unsupported reasons | Table explaining why commands aren't supported |
| DOC-06: CI badge | shields.io GitHub Actions workflow badge |
| DOC-07: PyPI badge | shields.io pypi/v badge |
| DOC-08: Python badge | shields.io pypi/pyversions badge |

## gitsl-Specific Content

Based on code analysis, document these specific implementations:

### Supported Commands (from gitsl.py)
1. `status` - with porcelain/short output emulation
2. `log` - with --oneline and -N translation
3. `diff` - passthrough
4. `init` - passthrough
5. `rev-parse` - only --short HEAD
6. `add` - with -A and -u handling
7. `commit` - passthrough

### Special Flags
1. `--version` / `-v` - shows gitsl version
2. `--help` / `-h` / `help` - shows usage

### Exit Behavior
- Supported commands: propagate sl exit code
- Unsupported commands: exit 0 (intentional)
- Errors: propagate sl stderr

## Open Questions

Things that couldn't be fully resolved:

1. **Repository owner/URL**
   - What we know: pyproject.toml uses placeholder "owner/gitsl"
   - What's unclear: Actual GitHub username/organization
   - Recommendation: Use placeholder in README, update before publish

2. **Whether to include Sapling installation instructions**
   - What we know: Sapling is a prerequisite
   - What's unclear: How detailed to be (link vs inline)
   - Recommendation: Link to Sapling installation docs, don't duplicate

3. **License section**
   - What we know: pyproject.toml says MIT
   - What's unclear: Whether LICENSE file exists
   - Recommendation: Add brief license mention, verify LICENSE file exists

## Sources

### Primary (HIGH confidence)
- [shields.io badges documentation](https://shields.io/badges/) - Badge URL patterns
- [Sapling Git Cheat Sheet](https://sapling-scm.com/docs/introduction/git-cheat-sheet/) - Official git-to-sl translations
- Project source code analysis - gitsl.py, cmd_*.py files
- [GitHub Actions workflow status badge](https://shields.io/badges/git-hub-actions-workflow-status) - CI badge format

### Secondary (MEDIUM confidence)
- [daily.dev README Badges Best Practices](https://daily.dev/blog/readme-badges-github-best-practices) - Badge organization patterns
- Black and Ruff README structures - Python CLI documentation conventions

### Tertiary (LOW confidence)
- General Markdown documentation patterns

## Metadata

**Confidence breakdown:**
- Badge formats: HIGH - Official shields.io documentation
- README structure: HIGH - Established Python CLI conventions
- Command matrix content: HIGH - Derived from actual source code
- Flag documentation: HIGH - Derived from actual source code
- Unsupported command reasoning: MEDIUM - Inferred from Sapling differences

**Research date:** 2026-01-19
**Valid until:** 2026-03-19 (60 days - documentation patterns are stable)
