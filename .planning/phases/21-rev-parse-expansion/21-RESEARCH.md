# Phase 21: Rev-Parse Expansion - Research

**Researched:** 2026-01-21
**Domain:** Git rev-parse command translation to Sapling equivalents
**Confidence:** HIGH

## Summary

Git `rev-parse` is a critical utility command used extensively by tools, scripts, and CI/CD pipelines to query repository metadata. The current gitsl implementation only supports `--short HEAD`. This phase expands support to include the most commonly used flags that tools depend on: `--show-toplevel`, `--git-dir`, `--is-inside-work-tree`, `--abbrev-ref HEAD`, `--verify`, and `--symbolic`.

The research confirms that Sapling provides direct equivalents or simple workarounds for all required flags. The `sl root` command handles repository root detection, templates provide bookmark/ref information, and `sl log -r <ref>` validates references. The implementation approach follows the existing pattern in cmd_rev_parse.py.

**Primary recommendation:** Implement each flag as a conditional check in the handle() function, using subprocess calls to sl commands where needed and Python-based detection for simpler checks like --is-inside-work-tree.

## Standard Stack

The established libraries/tools for this domain:

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| subprocess | stdlib | Execute sl commands | Standard Python subprocess handling |
| sys | stdlib | stdout/stderr output | CLI output handling |
| common.ParsedCommand | internal | Argument parsing | Existing gitsl pattern |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| os.path | stdlib | Path manipulation | Building .sl/.hg directory paths |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| subprocess.run | common.run_sl | run_sl passes through output; rev-parse needs to capture and transform output |

**Note:** Most rev-parse operations need `capture_output=True` to transform/filter output, so direct subprocess.run is appropriate (matching existing --short HEAD pattern).

## Architecture Patterns

### Recommended Command Structure
```
cmd_rev_parse.py
├── handle()                      # Main dispatch based on flags
├── _handle_show_toplevel()       # sl root
├── _handle_git_dir()             # sl root + /.sl or /.hg
├── _handle_is_inside_work_tree() # sl root exit code check
├── _handle_abbrev_ref()          # sl log -r <ref> -T '{activebookmark}'
├── _handle_verify()              # sl log -r <ref> validation
├── _handle_symbolic()            # symbolic name output
└── _handle_short()               # existing: sl whereami
```

### Pattern 1: Flag Detection and Dispatch
**What:** Check for specific flags in parsed.args and dispatch to handlers
**When to use:** Each rev-parse flag has different behavior
**Example:**
```python
def handle(parsed: ParsedCommand) -> int:
    args = parsed.args

    if "--show-toplevel" in args:
        return _handle_show_toplevel()

    if "--git-dir" in args:
        return _handle_git_dir()

    if "--is-inside-work-tree" in args:
        return _handle_is_inside_work_tree()

    # ... etc
```

### Pattern 2: sl root for Repository Detection
**What:** Use `sl root` to get repository root path and detect if inside repo
**When to use:** --show-toplevel, --git-dir, --is-inside-work-tree
**Example:**
```python
# Source: sl help root
def _handle_show_toplevel() -> int:
    result = subprocess.run(
        ["sl", "root"],
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        print(result.stdout.strip())
    else:
        sys.stderr.write(result.stderr)
    return result.returncode
```

### Pattern 3: Template-Based Bookmark Detection
**What:** Use `sl log -r <ref> -T '{activebookmark}'` to get current bookmark name
**When to use:** --abbrev-ref HEAD
**Example:**
```python
# Source: sl help templates - activebookmark keyword
def _handle_abbrev_ref(ref: str) -> int:
    if ref == "HEAD":
        result = subprocess.run(
            ["sl", "log", "-r", ".", "-T", "{activebookmark}"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            bookmark = result.stdout.strip()
            if bookmark:
                print(bookmark)
            else:
                # No active bookmark - output HEAD (detached state equivalent)
                print("HEAD")
        return result.returncode
    # Handle other refs
    return _handle_verify(ref)
```

### Pattern 4: Reference Validation with sl log
**What:** Use `sl log -r <ref>` to validate if a reference exists
**When to use:** --verify flag
**Example:**
```python
# Source: Observed behavior - sl log -r returns 255 for invalid refs
def _handle_verify(ref: str) -> int:
    result = subprocess.run(
        ["sl", "log", "-r", ref, "-T", "{node}", "-l", "1"],
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        print(result.stdout.strip())
        return 0
    else:
        sys.stderr.write(f"fatal: Needed a single revision\n")
        return 128  # Match git exit code
```

### Anti-Patterns to Avoid
- **Hardcoding .sl path:** Sapling may use `.hg` directory depending on version/mode. Always derive from `sl root`.
- **Assuming bookmark exists:** When no bookmark is active, `{activebookmark}` returns empty string - handle this case.
- **Ignoring git exit codes:** Tools expect specific exit codes (0 for success, 128 for errors) - match git behavior.

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Repository root detection | os.path traversal looking for .sl | `sl root` command | Handles .hg, .sl, nested repos correctly |
| Reference validation | regex matching on hash patterns | `sl log -r <ref>` | Handles all revset expressions, bookmarks, partial hashes |
| Active bookmark detection | parsing `sl bookmark` output | `sl log -T '{activebookmark}'` | Direct template keyword, handles edge cases |
| Inside work tree check | os.path.exists(".sl") | `sl root` exit code | Handles parent directory repos, symlinks |

**Key insight:** Sapling commands and templates handle edge cases (nested repos, various directory structures, partial hashes) that would require significant effort to replicate correctly.

## Common Pitfalls

### Pitfall 1: .sl vs .hg Directory Confusion
**What goes wrong:** Assuming Sapling always uses `.sl` directory
**Why it happens:** Documentation mentions `.sl` but current Sapling versions often use `.hg`
**How to avoid:** Always use `sl root` + path join, or check for both directories
**Warning signs:** Tests pass locally but fail in different Sapling configurations

### Pitfall 2: Empty Active Bookmark
**What goes wrong:** `--abbrev-ref HEAD` returns empty string instead of "HEAD"
**Why it happens:** `{activebookmark}` is empty when no bookmark is active (detached head state)
**How to avoid:** Check if template output is empty, fallback to "HEAD"
**Warning signs:** Tools expecting branch name get empty string

### Pitfall 3: Exit Code Mismatch
**What goes wrong:** Tools break because they expect git's specific exit codes
**Why it happens:** sl uses different exit codes (255 instead of 128)
**How to avoid:** Map sl exit codes to git exit codes (128 for errors in rev-parse)
**Warning signs:** Scripts using `set -e` fail unexpectedly

### Pitfall 4: Multiple Flags Not Handled
**What goes wrong:** `git rev-parse --short --verify HEAD` fails
**Why it happens:** Code only checks for single flag
**How to avoid:** Consider flag combinations, handle multiple flags if sensible
**Warning signs:** Tools passing multiple rev-parse flags fail

### Pitfall 5: Symbolic Output Semantics
**What goes wrong:** `--symbolic` returns hash instead of symbolic name
**Why it happens:** Misunderstanding git's symbolic flag behavior
**How to avoid:** `--symbolic` means output input form (e.g., HEAD stays HEAD, master stays master)
**Warning signs:** Scripts expecting symbolic names get hashes

## Code Examples

Verified patterns from official sources and testing:

### Get Repository Root (--show-toplevel)
```python
# Source: Verified with sl help root
result = subprocess.run(
    ["sl", "root"],
    capture_output=True,
    text=True
)
# Output: /absolute/path/to/repo
# Exit: 0 on success, 255 if not in repo
```

### Detect Work Tree (--is-inside-work-tree)
```python
# Source: Verified behavior - sl root fails outside repo
result = subprocess.run(
    ["sl", "root"],
    capture_output=True,
    text=True
)
if result.returncode == 0:
    print("true")
    return 0
else:
    print("false")
    return 0  # Note: git returns 0 even outside repo
```

### Get Active Bookmark (--abbrev-ref HEAD)
```python
# Source: sl help templates - activebookmark keyword
result = subprocess.run(
    ["sl", "log", "-r", ".", "-T", "{activebookmark}"],
    capture_output=True,
    text=True
)
bookmark = result.stdout.strip()
if bookmark:
    print(bookmark)
else:
    print("HEAD")  # Detached head equivalent
```

### Validate Reference (--verify)
```python
# Source: Observed sl behavior with invalid refs
result = subprocess.run(
    ["sl", "log", "-r", ref, "-T", "{node}", "-l", "1"],
    capture_output=True,
    text=True
)
if result.returncode == 0:
    print(result.stdout.strip())  # 40-char hash
    return 0
else:
    sys.stderr.write("fatal: Needed a single revision\n")
    return 128
```

### Get VCS Directory (--git-dir)
```python
# Source: sl root + directory detection
result = subprocess.run(
    ["sl", "root"],
    capture_output=True,
    text=True
)
if result.returncode == 0:
    root = result.stdout.strip()
    # Check for .sl first, then .hg
    sl_dir = os.path.join(root, ".sl")
    hg_dir = os.path.join(root, ".hg")
    if os.path.isdir(sl_dir):
        print(sl_dir)
    elif os.path.isdir(hg_dir):
        print(hg_dir)
    return 0
return result.returncode
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Only --short HEAD | Expanded flag support | Phase 21 | Tools can query repo metadata |
| Hardcoded .sl path | Dynamic .sl/.hg detection | Current | Works with all Sapling configurations |

**Deprecated/outdated:**
- None for this phase - expanding existing implementation

## Flag Priority by Tool Usage

Based on web research, these are the most commonly used rev-parse flags by tools:

| Flag | Common Usage | Priority |
|------|--------------|----------|
| `--show-toplevel` | Finding repo root for scripts | HIGH - Required (REVP-01) |
| `--is-inside-work-tree` | Guard clauses in git hooks | HIGH - Required (REVP-03) |
| `--git-dir` | Finding .git directory | HIGH - Required (REVP-02) |
| `--verify` | Validating branch/tag existence | HIGH - Required (REVP-05) |
| `--abbrev-ref HEAD` | Getting current branch name | HIGH - Required (REVP-04) |
| `--symbolic` | Preserving symbolic refs | MEDIUM - Required (REVP-06) |
| `--short HEAD` | Getting short commit hash | Already implemented |
| `--show-prefix` | Path from root to cwd | LOW - Not required |
| `--show-cdup` | Relative path to root | LOW - Not required |

## Sapling Command Mappings

| Git Rev-Parse Flag | Sapling Equivalent | Notes |
|-------------------|-------------------|-------|
| `--show-toplevel` | `sl root` | Direct mapping |
| `--git-dir` | `sl root` + `/.sl` or `/.hg` | Derive from root |
| `--is-inside-work-tree` | `sl root` exit code | 0 = true, non-zero = false |
| `--abbrev-ref HEAD` | `sl log -r . -T '{activebookmark}'` | Empty = detached |
| `--verify <ref>` | `sl log -r <ref> -T '{node}'` | Returns hash or error |
| `--symbolic <ref>` | Echo input | Symbolic means keep input form |
| `--short HEAD` | `sl whereami` (first 7 chars) | Already implemented |

## Open Questions

Things that couldn't be fully resolved:

1. **Hybrid Git/Sapling repos**
   - What we know: gitsl project uses `.git/sl` structure
   - What's unclear: How common is this configuration for gitsl users?
   - Recommendation: Detect both `.sl` and `.hg`, prioritize `.sl` if both exist

2. **Flag combinations**
   - What we know: `git rev-parse --short --verify HEAD` is valid
   - What's unclear: Which combinations are commonly used?
   - Recommendation: Start with single flags, add combinations as needed

3. **--symbolic-full-name vs --symbolic**
   - What we know: --symbolic outputs input form, --symbolic-full-name outputs refs/heads/...
   - What's unclear: Is --symbolic-full-name needed for gitsl?
   - Recommendation: Only implement --symbolic (in requirements), defer --symbolic-full-name

## Sources

### Primary (HIGH confidence)
- `sl help root` - Repository root command documentation
- `sl help templates` - Template keywords including activebookmark, node
- `sl help bookmark` - Bookmark management and active bookmark concept
- Git official documentation: https://git-scm.com/docs/git-rev-parse

### Secondary (MEDIUM confidence)
- Git Tower guide on rev-parse: https://redesign-staging.git-tower.com/learn/git/faq/git-rev-parse
- Verified behavior through direct testing with sl commands

### Tertiary (LOW confidence)
- GitHub issue on .sl vs .hg: https://github.com/facebook/sapling/issues/745 (for understanding directory structure)

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Using stdlib Python and existing patterns
- Architecture: HIGH - Follows established cmd_*.py patterns in gitsl
- Sapling mappings: HIGH - Verified through direct testing with sl commands
- Pitfalls: HIGH - Discovered through actual testing and documentation

**Research date:** 2026-01-21
**Valid until:** 60 days (stable domain, sl commands unlikely to change)
