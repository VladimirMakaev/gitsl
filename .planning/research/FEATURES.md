# Features Research: Git-to-Sapling CLI Shim

**Domain:** CLI shim/wrapper for version control command translation
**Researched:** 2026-01-17
**Confidence:** MEDIUM-HIGH (based on Sapling official docs + git wrapper patterns)

## Executive Summary

A git-to-Sapling shim needs to translate commands and flags between two VCS tools with similar but distinct interfaces. The core challenge is that Sapling intentionally differs from git in philosophy (no staging area, different undo model) while maintaining conceptual similarity. The shim must bridge these differences transparently for tools expecting git output.

---

## Table Stakes

Essential features without which the shim would not function for its intended purpose.

### 1. Command Routing

| Feature | Why Essential | Implementation Notes |
|---------|---------------|---------------------|
| **Subcommand dispatch** | Must route `git status` to appropriate handler | Parse first non-flag argument as subcommand |
| **Unknown command passthrough** | Tools may call git commands we haven't mapped | Either error gracefully or pass to `sl` directly |
| **Exit code preservation** | Calling tools check exit codes for success/failure | Return subprocess exit code unchanged |

**Source:** Hub wrapper pattern - "your normal git commands will all work" requires transparent routing.

### 2. Core Command Mapping

The project specifies these commands must work:

| Git Command | Sapling Equivalent | Notes |
|-------------|-------------------|-------|
| `git status` | `sl status` | Nearly identical, but flag differences exist |
| `git add` | `sl add` | Similar behavior, Sapling has no staging area concept |
| `git commit` | `sl commit` | `-a` flag behavior differs (Sapling always commits all) |
| `git log` | `sl log` | `--oneline` must be emulated via `--template` |
| `git diff` | `sl diff` | Similar flags available |
| `git rev-parse` | `sl whereami` / custom | Sapling has `whereami` for HEAD, but not full rev-parse |
| `git init` | `sl init` | Similar behavior |

**Source:** [Sapling Git Cheat Sheet](https://sapling-scm.com/docs/introduction/git-cheat-sheet/)

### 3. Flag Translation

Flags that must work because tools commonly use them:

| Git Flag | Context | Sapling Handling | Priority |
|----------|---------|------------------|----------|
| `--porcelain` | `status` | **MUST EMULATE** - Sapling has no equivalent | CRITICAL |
| `--short` | `status` | **MUST EMULATE** - Sapling uses `-n/--no-status` differently | CRITICAL |
| `-u` / `--untracked-files` | `status` | Maps to `-u/--unknown` in Sapling | HIGH |
| `--oneline` | `log` | **MUST EMULATE** via `--template` | CRITICAL |
| `-n` / `--max-count` | `log` | Maps to `-l/--limit` in Sapling | HIGH |
| `-m` | `commit` | Direct equivalent exists | HIGH |

**Source:** [Sapling status docs](https://sapling-scm.com/docs/commands/status/), [Sapling log docs](https://sapling-scm.com/docs/commands/log/)

### 4. Output Format Emulation

When Sapling output differs from git, the shim must transform it:

| Scenario | Git Output | Sapling Output | Transformation Needed |
|----------|------------|----------------|----------------------|
| `status --porcelain` | `XY PATH` (2-char code + path) | Status letter differs | Capture and reformat |
| `status --short` | `XY PATH` | Similar to porcelain | May need reformatting |
| `log --oneline` | `<hash7> <subject>` | No equivalent flag | Use `--template '{node|short} {desc|firstline}\n'` |
| `rev-parse HEAD` | Full SHA | `sl whereami` returns hash | Likely compatible |
| `rev-parse --show-toplevel` | Repo root path | No direct equivalent | Must implement |

**Source:** [Git status porcelain format](https://git-scm.com/docs/git-status)

### 5. Standard I/O Handling

| Feature | Why Essential |
|---------|---------------|
| **stdout passthrough** | Calling tools parse stdout |
| **stderr passthrough** | Error messages must propagate |
| **stdin passthrough** | Interactive commands need input (e.g., commit message editor) |
| **TTY detection** | Some flags change behavior based on TTY |

---

## Nice-to-Have

Would improve robustness and user experience but not strictly required for MVP.

### 1. Enhanced Compatibility

| Feature | Benefit | Complexity |
|---------|---------|------------|
| **`parse_known_args` pattern** | Handle unknown flags gracefully | LOW |
| **Flag aliasing** | Map `-s` to `--short`, `-p` to `--porcelain` | LOW |
| **Environment variable passthrough** | `GIT_DIR`, `GIT_WORK_TREE` handling | MEDIUM |
| **Config file support** | Custom mappings per-repository | HIGH |

### 2. Diagnostic Features

| Feature | Benefit | Complexity |
|---------|---------|------------|
| **`--debug` flag** | Show what command would be executed | LOW |
| **`--dry-run`** | Preview without execution | LOW |
| **Verbose mode** | Log translation decisions | LOW |
| **Version reporting** | `git --version` returns shim version + sl version | LOW |

### 3. Graceful Degradation

| Feature | Benefit | Complexity |
|---------|---------|------------|
| **Unsupported command warnings** | Tell user what's not implemented | LOW |
| **Fallback to `sl git`** | Sapling's built-in git translation | LOW |
| **Command suggestions** | "Did you mean `sl goto`?" | MEDIUM |

### 4. Extended Command Support

Beyond the MVP commands, these would be useful:

| Command | Use Case | Mapping Complexity |
|---------|----------|-------------------|
| `git push` | `sl push` | LOW (direct mapping) |
| `git pull` | `sl pull` | LOW (direct mapping) |
| `git fetch` | `sl pull` | LOW (note: different semantics) |
| `git checkout` | `sl goto` / `sl revert` | MEDIUM (context-dependent) |
| `git branch` | `sl bookmark` | MEDIUM (different model) |
| `git stash` | `sl shelve` | LOW (direct mapping) |
| `git show` | `sl show` | LOW (direct mapping) |

**Source:** [Sapling Git Cheat Sheet](https://sapling-scm.com/docs/introduction/git-cheat-sheet/)

---

## Anti-Features

Things to deliberately NOT build. Over-engineering traps for a simple shim.

### 1. Full Git Compatibility Layer

**Why avoid:** Git has hundreds of commands and thousands of flag combinations. Attempting full compatibility would be:
- Massive scope creep
- Impossible to maintain
- Defeat the purpose (just use git)

**Instead:** Support the specific commands and flags needed for the target use case. Document what's supported.

### 2. Output Caching

**Why avoid:**
- Stale data is worse than slow data for VCS
- Adds complexity for minimal benefit
- Cache invalidation is hard

**Instead:** Pass through to Sapling every time.

### 3. Git Repository Detection/Switching

**Why avoid:**
- The shim should be used in Sapling repos only
- Auto-detecting and switching between git/Sapling adds failure modes
- Confusing behavior when mixed repos exist

**Instead:** Assume Sapling. Fail clearly if not a Sapling repo.

### 4. Custom Argument Parsing Library

**Why avoid:**
- Python's `argparse` or `sys.argv` parsing is sufficient
- Third-party deps violate single-file requirement
- Complex parsers add overhead for simple translation

**Instead:** Minimal parsing, maximum passthrough.

### 5. Interactive Mode Emulation

**Why avoid:**
- `git add -i`, `git rebase -i` are complex interactive workflows
- Sapling has different interactive models (`sl commit -i`)
- Screen/terminal handling is fragile

**Instead:** Either pass through or document as unsupported.

### 6. Configuration File System

**Why avoid:**
- Adds file I/O complexity
- Needs config file location logic
- Users expect git config, not custom config

**Instead:** Hardcode translations. If customization needed, use environment variables.

### 7. Plugin/Extension System

**Why avoid:**
- Single-file constraint
- Adds import complexity
- Maintenance burden

**Instead:** Keep it simple. Fork for custom needs.

---

## Flag Emulation Strategies

How other tools handle flag translation when target tool lacks equivalent flags.

### Strategy 1: Output Transformation

**Pattern:** Run target command, capture output, transform to expected format.

```python
# Example: Emulating git status --porcelain
output = subprocess.run(['sl', 'status'], capture_output=True)
transformed = transform_to_porcelain(output.stdout)
print(transformed)
```

**When to use:** Target command produces similar data in different format.

**Used by:** Many git wrappers for format standardization.

### Strategy 2: Template/Format Flags

**Pattern:** Use target tool's formatting options to approximate source format.

```python
# Example: Emulating git log --oneline
# Sapling has --template for custom output
subprocess.run(['sl', 'log', '--template', '{node|short} {desc|firstline}\n'])
```

**When to use:** Target tool has flexible output formatting.

**Sapling supports:** `--template` for log, which is powerful enough to emulate most git log formats.

**Source:** [Sapling log docs](https://sapling-scm.com/docs/commands/log/)

### Strategy 3: Direct Flag Mapping

**Pattern:** Translate flag name but preserve semantics.

```python
# Example: -u in git status -> -u in sl status (both mean untracked)
flag_map = {'-u': '-u', '--untracked-files': '-u'}
```

**When to use:** Same concept, different flag name.

### Strategy 4: Semantic Translation

**Pattern:** Translate intent, not syntax. May require multiple commands.

```python
# Example: git checkout can mean goto OR revert
# Need to detect which based on arguments
if is_file_path(args):
    run(['sl', 'revert', args])
else:
    run(['sl', 'goto', args])
```

**When to use:** Source command overloaded, target commands are specific.

**Source:** [Sapling differences from Git](https://sapling-scm.com/docs/introduction/differences-git/)

### Strategy 5: Stub/No-Op Handling

**Pattern:** Accept flag but ignore it (with optional warning).

```python
# Example: --color=always (Sapling may handle color differently)
if '--color=always' in args:
    args.remove('--color=always')  # Sapling handles color automatically
```

**When to use:** Flag is cosmetic or has sensible default in target tool.

### Strategy 6: Error with Guidance

**Pattern:** Fail with helpful message for unsupported flags.

```python
if '--interactive' in args:
    print("Error: git add --interactive not supported. Use 'sl commit -i' instead.",
          file=sys.stderr)
    sys.exit(1)
```

**When to use:** Feature genuinely unsupported, user needs guidance.

---

## Specific Translation Requirements

Based on the project context, here are detailed translation requirements.

### `git status --porcelain`

**Git format:**
```
XY PATH
XY ORIG -> PATH  (for renames)
```
Where XY is a 2-character status code (index status + worktree status).

**Sapling format:**
```
X PATH
```
Single character status code.

**Translation needed:**
- Sapling has no staging area, so "index status" is always empty/clean
- Map: `M` (Sapling) -> ` M` or `M ` (git, depending on whether staged)
- Map: `A` (Sapling) -> `A ` (git, newly added file)
- Map: `?` (Sapling) -> `??` (git, untracked)
- Map: `!` (Sapling, missing) -> ` D` (git, deleted in worktree)

**Source:** [Git status porcelain](https://git-scm.com/docs/git-status), [Sapling status](https://sapling-scm.com/docs/commands/status/)

### `git log --oneline`

**Git format:**
```
a1b2c3d Subject line here
```
(7-char hash + subject)

**Sapling approach:**
```bash
sl log --template '{node|short} {desc|firstline}\n'
```

**Notes:**
- `{node|short}` gives 12-char hash by default; may need truncation
- `{desc|firstline}` gives first line of commit message

### `git rev-parse HEAD`

**Git behavior:** Returns full SHA of HEAD.

**Sapling equivalent:** `sl whereami` returns commit hash.

**Potential gaps:**
- `rev-parse --show-toplevel` (repo root path) - needs custom handling
- `rev-parse --git-dir` (git directory) - needs custom handling
- `rev-parse --is-inside-work-tree` - needs custom handling

---

## MVP Feature Prioritization

Based on project context "needs to handle: status, add, commit, log, diff, rev-parse, init":

### P0 - Must Work

1. **`git status`** - with `--porcelain`, `--short`, `-u` emulation
2. **`git add`** - direct passthrough with file arguments
3. **`git commit`** - with `-m` flag support
4. **`git log`** - with `--oneline` emulation
5. **`git diff`** - direct passthrough
6. **`git rev-parse HEAD`** - via `sl whereami`
7. **`git init`** - direct passthrough

### P1 - Should Work

1. **Exit code preservation** for all commands
2. **stderr passthrough** for error visibility
3. **Unknown flag passthrough** for flags we don't recognize

### P2 - Nice to Have

1. **`git rev-parse --show-toplevel`** - repo root detection
2. **Debug mode** for troubleshooting
3. **Additional log format flags** (`-n`, `--pretty`)

---

## Sources

- [Sapling Differences from Git](https://sapling-scm.com/docs/introduction/differences-git/)
- [Sapling Git Cheat Sheet](https://sapling-scm.com/docs/introduction/git-cheat-sheet/)
- [Sapling status command](https://sapling-scm.com/docs/commands/status/)
- [Sapling log command](https://sapling-scm.com/docs/commands/log/)
- [Sapling diff command](https://sapling-scm.com/docs/commands/diff/)
- [Sapling commit command](https://sapling-scm.com/docs/commands/commit/)
- [Sapling add command](https://sapling-scm.com/docs/commands/add/)
- [Sapling init command](https://sapling-scm.com/docs/commands/init/)
- [Git status porcelain format](https://git-scm.com/docs/git-status)
- [Git wrapper topic on GitHub](https://github.com/topics/git-wrapper)
- [g wrapper architecture](https://dev.to/pcdevil/g-a-wrapper-around-git-with-additional-feature-extension-3m11)
- [git-wrapper PyPI](https://pypi.org/project/git-wrapper/)
