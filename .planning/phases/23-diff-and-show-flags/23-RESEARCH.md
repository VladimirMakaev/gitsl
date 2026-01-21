# Phase 23: Diff and Show Flags - Research

**Researched:** 2026-01-21
**Domain:** Git diff/show flag translation to Sapling equivalents
**Confidence:** HIGH

## Summary

This phase extends gitsl's `diff` and `show` commands with flag translation support, following the patterns established in Phase 22 (log flags). The current implementations are minimal pass-through handlers. Research confirms that Sapling's `sl diff` and `sl show` commands have direct equivalents for core flags (--stat, -w, -b, -U), while advanced git features (--word-diff, --color-moved, -M/-C rename/copy detection) have no Sapling equivalent and require warnings.

The key insight is that git's staging area concept (--staged/--cached) has no Sapling equivalent since Sapling doesn't have a staging area. This requires a clear warning message. For output formatting flags like --name-only and --name-status on show, templates can approximate the behavior similar to the log command approach.

**Primary recommendation:** Extend cmd_diff.py and cmd_show.py with flag parsing following the cmd_log.py pattern. Group flags by category (whitespace, context, output format, advanced). Use templates for --name-only/--name-status on show. Warn for unsupported features (--word-diff, --color-moved, -M/-C, --staged/--cached).

## Standard Stack

The established libraries/tools for this domain:

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| re | stdlib | Regex for flag parsing | Handle `-U<n>` attached formats |
| sys | stdlib | stderr output | Warning messages for unsupported options |
| common.ParsedCommand | internal | Argument parsing | Existing gitsl pattern |
| common.run_sl | internal | Execute sl with passthrough | Standard execution for most flags |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| subprocess | stdlib | Process execution | Used by run_sl internally |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Flag-by-flag parsing | argparse | argparse is overkill; simple string matching is cleaner |
| Custom diff coloring | External library | Not needed; sl handles coloring |

**Installation:**
No additional dependencies required - stdlib only.

## Architecture Patterns

### Recommended Command Structure
```
cmd_diff.py / cmd_show.py
handle()
    # Flag categories for translation:
    # 1. Direct pass-through flags (--stat, -w, -b, -p)
    # 2. Context flags (-U<n> with value parsing)
    # 3. Output format flags (--name-only, --name-status via template)
    # 4. Warning flags (--staged/--cached, --word-diff, --color-moved, -M/-C)
    # 5. Remaining args pass-through
```

### Pattern 1: Flag Translation with Value Parsing
**What:** Handle flags that take optional or required values in attached format
**When to use:** -U<n>, -M[<n>], -C[<n>] flags
**Example:**
```python
# Source: https://sapling-scm.com/docs/commands/diff/
# Handle -U<n> or --unified=<n>
if arg.startswith('-U') and len(arg) > 2:
    # Attached value: -U5
    context_lines = arg[2:]
    sl_args.extend(['-U', context_lines])
elif arg == '-U':
    # Separate value: -U 5
    if i + 1 < len(parsed.args):
        i += 1
        sl_args.extend(['-U', parsed.args[i]])
elif arg.startswith('--unified='):
    context_lines = arg.split('=', 1)[1]
    sl_args.extend(['-U', context_lines])
```

### Pattern 2: Warning for Unsupported Flags
**What:** Print warning to stderr and continue execution when flag has no sl equivalent
**When to use:** --staged/--cached, --word-diff, --color-moved, -M/-C
**Example:**
```python
# DIFF-07: --staged/--cached warns about no staging area
if arg in ('--staged', '--cached'):
    print("Warning: Sapling has no staging area. --staged/--cached has no effect.",
          file=sys.stderr)
    print("All uncommitted changes are shown with 'sl diff'.", file=sys.stderr)
    # Do NOT add to sl_args - flag is meaningless in sl
```

### Pattern 3: Template-Based Output Formatting for Show
**What:** Use sl's -T template flag to produce --name-only/--name-status output
**When to use:** show --name-only, show --name-status
**Example:**
```python
# Source: cmd_log.py patterns
# SHOW-04: --name-only uses template
SHOW_NAME_ONLY_TEMPLATE = "{node|short} {desc|firstline}\\n{files}\\n"

# SHOW-05: --name-status uses template with status indicators
SHOW_NAME_STATUS_TEMPLATE = ("{node|short} {desc|firstline}\\n"
                              "{file_adds % 'A\\t{file}\\n'}"
                              "{file_dels % 'D\\t{file}\\n'}"
                              "{file_mods % 'M\\t{file}\\n'}\\n")

if '--name-only' in args:
    sl_args.extend(['-T', SHOW_NAME_ONLY_TEMPLATE])
```

### Pattern 4: Pretty/Format Template Translation for Show
**What:** Map git's --pretty/--format to sl's -T template
**When to use:** show --pretty=<format>, show --format=<format>
**Example:**
```python
# Reuse the format translation infrastructure from cmd_log.py
# SHOW-06: --pretty/--format maps to template formatting
# Import or duplicate the GIT_TO_SL_PLACEHOLDERS and PRETTY_PRESETS from cmd_log.py

if arg.startswith('--pretty=') or arg.startswith('--format='):
    format_spec = arg.split('=', 1)[1]
    if format_spec in PRETTY_PRESETS:
        custom_template = PRETTY_PRESETS[format_spec]
    elif format_spec.startswith('format:'):
        custom_template = translate_format_placeholders(format_spec[7:])
```

### Anti-Patterns to Avoid
- **Silent flag dropping:** If a flag can't be translated, warn the user rather than silently ignoring.
- **Implementing rename detection manually:** Don't try to build -M/-C detection; just warn.
- **Complex word-diff emulation:** Don't try to post-process output; just warn.
- **Assuming staging area exists:** Sapling doesn't have it; be explicit about this.

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Diffstat generation | Line counting logic | sl diff --stat | Built-in, matches git format |
| Whitespace handling | Custom diff filtering | sl diff -w/-b | Native flags work identically |
| Context lines | Output post-processing | sl diff -U<n> | Direct flag translation |
| File filtering | Path parsing | sl diff <paths> | Pass-through works |
| Rename detection | Similarity algorithm | Warning message | sl doesn't support; too complex |
| Word-level diff | Text analysis | Warning message | sl doesn't support; external tools exist |

**Key insight:** Most core git diff/show flags have direct sl equivalents. Advanced features (rename detection, word diff, color-moved) don't exist in sl and shouldn't be emulated - just warn the user.

## Common Pitfalls

### Pitfall 1: Staging Area Confusion
**What goes wrong:** User runs `git diff --staged` expecting to see staged changes, gets unexpected output
**Why it happens:** Sapling has no staging area; all uncommitted changes are in the working directory
**How to avoid:** Clear warning message explaining Sapling's model
**Warning signs:** Users complaining about "wrong" diff output
```python
# DIFF-07: Explicit warning
if arg in ('--staged', '--cached'):
    print("Warning: Sapling has no staging area. Use 'sl diff' to see all uncommitted changes.",
          file=sys.stderr)
```

### Pitfall 2: -U Value Attachment Variations
**What goes wrong:** Fails to parse `-U5`, `-U 5`, `--unified=5`
**Why it happens:** Git allows multiple syntaxes for context line count
**How to avoid:** Handle all three formats explicitly
**Warning signs:** "Unknown flag" errors for valid git syntax

### Pitfall 3: --name-only on Diff vs Show
**What goes wrong:** Different behavior expected for diff --name-only vs show --name-only
**Why it happens:** git diff --name-only shows changed files; git show --name-only shows files in commit
**How to avoid:** For diff, may need different approach than show (sl diff has limited template support)
**Warning signs:** Missing or incorrect file listings

### Pitfall 4: Rename Detection Expectation
**What goes wrong:** User expects -M to detect renames, nothing happens
**Why it happens:** sl doesn't have automatic rename detection like git
**How to avoid:** Clear warning; suggest using sl mv before committing
**Warning signs:** Users seeing "deleted + added" instead of "renamed"

### Pitfall 5: Raw Format Complexity
**What goes wrong:** git diff --raw output format doesn't match sl output
**Why it happens:** Git's raw format is unique; sl uses different internal format
**How to avoid:** Either emulate with template or warn about differences
**Warning signs:** Scripts depending on exact raw format break

### Pitfall 6: Show Format Priority
**What goes wrong:** Multiple format flags given, wrong one takes precedence
**Why it happens:** Need to handle flag priority correctly
**How to avoid:** Follow same priority pattern as cmd_log.py: custom_template > name_status > name_only > oneline
**Warning signs:** Unexpected output format

## Code Examples

Verified patterns from official sources:

### Diff Flag Translation
```python
# Source: https://sapling-scm.com/docs/commands/diff/
# Verified: sl diff supports --stat, -w, -b, -U

def handle(parsed: ParsedCommand) -> int:
    """Handle 'git diff' command with flag translation."""
    sl_args = ["diff"]
    remaining_args = []

    i = 0
    while i < len(parsed.args):
        arg = parsed.args[i]

        # DIFF-01: --stat passes through
        if arg == '--stat':
            sl_args.append('--stat')

        # DIFF-02: -w/--ignore-all-space passes through
        elif arg in ('-w', '--ignore-all-space'):
            sl_args.append('-w')

        # DIFF-03: -b/--ignore-space-change passes through
        elif arg in ('-b', '--ignore-space-change'):
            sl_args.append('-b')

        # DIFF-04: -U<n>/--unified=<n> with value parsing
        elif arg.startswith('-U') and len(arg) > 2:
            sl_args.extend(['-U', arg[2:]])
        elif arg == '-U':
            if i + 1 < len(parsed.args):
                i += 1
                sl_args.extend(['-U', parsed.args[i]])
        elif arg.startswith('--unified='):
            sl_args.extend(['-U', arg.split('=', 1)[1]])

        # ... continue for other flags
        else:
            remaining_args.append(arg)

        i += 1

    sl_args.extend(remaining_args)
    return run_sl(sl_args)
```

### Name-Only/Name-Status via Template (for diff)
```python
# DIFF-05: --name-only and DIFF-06: --name-status
# sl diff does NOT directly support these; need template or post-processing
# Option 1: Use sl status for file names with changes
# Option 2: Use sl log -r 'wdir()' with template (not applicable for diff)
# Option 3: Post-process sl diff output to extract file names

# For simplicity, recommend: run sl diff and extract filenames from output
# or run sl status for pending changes

if '--name-only' in args:
    # For working directory diff, sl status provides file names
    # This is a semantic match, not exact format match
    sl_args = ["status", "-mard"]  # modified, added, removed, deleted
    # Or extract from diff header lines (more complex)

if '--name-status' in args:
    # sl status already shows status codes (M, A, R, !)
    sl_args = ["status", "-mard"]
```

### Warning for Unsupported Flags
```python
# DIFF-07: --staged/--cached
if arg in ('--staged', '--cached'):
    print("Warning: Sapling has no staging area.", file=sys.stderr)
    print("Use 'sl diff' to see all uncommitted changes.", file=sys.stderr)
    # Skip this flag - don't add to sl_args

# DIFF-09: -M/--find-renames
if arg in ('-M', '--find-renames') or arg.startswith('-M'):
    print("Warning: Sapling doesn't support automatic rename detection (-M).",
          file=sys.stderr)
    print("Use 'sl mv' to track renames before committing.", file=sys.stderr)

# DIFF-10: -C/--find-copies
if arg in ('-C', '--find-copies') or arg.startswith('-C'):
    print("Warning: Sapling doesn't support automatic copy detection (-C).",
          file=sys.stderr)
    print("Use 'sl copy' to track copies before committing.", file=sys.stderr)

# DIFF-11: --word-diff
if arg.startswith('--word-diff'):
    print("Warning: Sapling doesn't support word-level diff (--word-diff).",
          file=sys.stderr)
    print("Consider using external tools like 'diff-so-fancy' or 'delta'.",
          file=sys.stderr)

# DIFF-12: --color-moved
if arg.startswith('--color-moved'):
    print("Warning: Sapling doesn't support --color-moved.", file=sys.stderr)
```

### Show Flag Translation
```python
# Source: https://sapling-scm.com/docs/commands/show/
# Verified: sl show supports --stat, -U, -w, -T (template)

def handle(parsed: ParsedCommand) -> int:
    """Handle 'git show' command with flag translation."""
    sl_args = ["show"]
    remaining_args = []
    use_oneline = False
    no_patch = False
    custom_template = None
    name_only = False
    name_status = False

    i = 0
    while i < len(parsed.args):
        arg = parsed.args[i]

        # SHOW-01: --stat passes through
        if arg == '--stat':
            sl_args.append('--stat')

        # SHOW-02: -U<n> passes through
        elif arg.startswith('-U') and len(arg) > 2:
            sl_args.extend(['-U', arg[2:]])
        elif arg == '-U':
            if i + 1 < len(parsed.args):
                i += 1
                sl_args.extend(['-U', parsed.args[i]])

        # SHOW-03: -w passes through
        elif arg in ('-w', '--ignore-all-space'):
            sl_args.append('-w')

        # SHOW-04: --name-only
        elif arg == '--name-only':
            name_only = True

        # SHOW-05: --name-status
        elif arg == '--name-status':
            name_status = True

        # SHOW-06: --pretty/--format
        elif arg.startswith('--pretty=') or arg.startswith('--format='):
            format_spec = arg.split('=', 1)[1]
            custom_template = translate_format_for_show(format_spec)

        # SHOW-07: -s/--no-patch
        elif arg in ('-s', '--no-patch'):
            no_patch = True

        # SHOW-08: --oneline
        elif arg == '--oneline':
            use_oneline = True

        else:
            remaining_args.append(arg)

        i += 1

    # Apply template based on priority
    # ... similar to cmd_log.py logic

    sl_args.extend(remaining_args)
    return run_sl(sl_args)
```

### Raw Format Handling
```python
# DIFF-08: --raw produces raw format output
# Git raw format is complex: :100644 100644 <sha1> <sha1> M<TAB>filename
# sl doesn't have direct equivalent
# Options:
# 1. Warn and skip
# 2. Approximate with sl status output
# 3. Parse sl diff output and reformat

if arg == '--raw':
    print("Warning: --raw format may differ from git's exact output.",
          file=sys.stderr)
    # Could use sl status -mard for approximation
    # Or just let sl diff run and accept different output
```

## Git to Sapling Flag Mapping Tables

### Diff Flags

| Git Flag | Sapling Equivalent | Notes | Confidence |
|----------|-------------------|-------|------------|
| `--stat` | `--stat` | Direct pass-through | HIGH |
| `-w/--ignore-all-space` | `-w` | Direct pass-through | HIGH |
| `-b/--ignore-space-change` | `-b` | Direct pass-through | HIGH |
| `-U<n>/--unified=<n>` | `-U <n>` | Value translation | HIGH |
| `--name-only` | `sl status -mard` or template | Semantic equivalent | MEDIUM |
| `--name-status` | `sl status -mard` | Already shows status codes | MEDIUM |
| `--staged/--cached` | Warning | No staging area in sl | HIGH |
| `--raw` | Warning + pass-through | Different format | LOW |
| `-M/--find-renames` | Warning | Not supported | HIGH |
| `-C/--find-copies` | Warning | Not supported | HIGH |
| `--word-diff` | Warning | Not supported | HIGH |
| `--color-moved` | Warning | Not supported | HIGH |

### Show Flags

| Git Flag | Sapling Equivalent | Notes | Confidence |
|----------|-------------------|-------|------------|
| `--stat` | `--stat` | Direct pass-through | HIGH |
| `-U<n>` | `-U <n>` | Value translation | HIGH |
| `-w` | `-w` | Direct pass-through | HIGH |
| `--name-only` | `-T template` | Template-based | MEDIUM |
| `--name-status` | `-T template` | Template-based | MEDIUM |
| `--pretty/--format` | `-T template` | Placeholder translation | MEDIUM |
| `-s/--no-patch` | Template without diff | Suppress diff | MEDIUM |
| `--oneline` | `-T template` | Short format template | HIGH |

## Implementation Priority

Based on usage frequency and implementation complexity:

| Priority | Flags | Reason |
|----------|-------|--------|
| HIGH (easy) | diff: --stat, -w, -b, -U | Direct pass-through |
| HIGH (easy) | show: --stat, -w, -U | Direct pass-through |
| HIGH (warning) | diff: --staged/--cached | Common flag, needs clear explanation |
| MEDIUM (template) | show: --oneline, -s/--no-patch | Template-based, reuse log patterns |
| MEDIUM (template) | show: --name-only, --name-status | Template-based, reuse log patterns |
| MEDIUM (template) | show: --pretty/--format | Reuse translate_format_placeholders |
| MEDIUM (complex) | diff: --name-only, --name-status | May need sl status or post-processing |
| LOW (warning) | diff: --raw | Different format; warn about differences |
| LOW (warning) | diff: -M, -C | No equivalent; warn |
| LOW (warning) | diff: --word-diff, --color-moved | No equivalent; warn |

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Pure pass-through | Flag translation | Phase 23 | Users can use familiar git flags |
| No warnings | Clear warnings for unsupported | Phase 23 | Users understand limitations |

**Deprecated/outdated:**
- None for this phase - extending minimal implementation

## Open Questions

Things that couldn't be fully resolved:

1. **diff --name-only implementation**
   - What we know: sl diff doesn't have --name-only flag
   - What's unclear: Best approach - use sl status, parse diff output, or template?
   - Recommendation: Use `sl status -mard` for working directory diff; for commit diff, parse diff headers

2. **diff --raw exact format**
   - What we know: Git's raw format includes mode, sha, status
   - What's unclear: How close can we get with sl output?
   - Recommendation: Warn about format differences; don't try to emulate exactly

3. **show --no-patch implementation**
   - What we know: Should suppress diff, show only commit info
   - What's unclear: Does sl show have a direct flag, or need template?
   - Recommendation: Use template that shows only commit metadata

4. **Shared code with cmd_log.py**
   - What we know: Many patterns overlap (templates, format translation)
   - What's unclear: Should we extract to common module?
   - Recommendation: Consider extracting PRETTY_PRESETS, GIT_TO_SL_PLACEHOLDERS to common.py if reused

## Sources

### Primary (HIGH confidence)
- [Sapling diff command documentation](https://sapling-scm.com/docs/commands/diff/) - Official sl diff flags
- [Sapling show command documentation](https://sapling-scm.com/docs/commands/show/) - Official sl show flags
- [Mercurial diff documentation](https://www.selenic.com/mercurial/hg.1.html) - hg diff options (sl inherits)

### Secondary (MEDIUM confidence)
- [Git diff-options documentation](https://git-scm.com/docs/diff-options) - Git flag reference
- [Git diff-format documentation](https://git-scm.com/docs/diff-format) - Raw format specification
- [Git show documentation](https://git-scm.com/docs/git-show) - Git show flag reference
- Existing gitsl cmd_log.py - Established patterns for template translation

### Tertiary (LOW confidence)
- Phase 22 Research - Precedent for flag translation approach

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Using stdlib Python and existing patterns
- Direct pass-through flags: HIGH - Verified against official docs
- Template-based flags: MEDIUM - Following cmd_log.py patterns
- Warning flags: HIGH - Clearly unsupported in sl
- name-only/name-status for diff: LOW - Implementation approach unclear

**Research date:** 2026-01-21
**Valid until:** 60 days (stable domain, sl diff/show flags unlikely to change)
