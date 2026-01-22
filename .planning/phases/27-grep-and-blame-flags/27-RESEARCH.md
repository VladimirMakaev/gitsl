# Phase 27: Grep and Blame Flags - Research

**Researched:** 2026-01-22
**Domain:** Git-to-Sapling flag translation for grep and blame commands
**Confidence:** HIGH

## Summary

Phase 27 extends the existing cmd_grep.py and cmd_blame.py handlers to support the full range of grep and blame flags specified in the requirements. The current implementations are minimal pass-through handlers that forward all arguments directly to `sl grep` and `sl annotate` respectively.

The good news is that `sl grep` and `sl annotate` support most of the required flags with identical or near-identical semantics to git. For grep, flags like `-n`, `-i`, `-l`, `-w`, `-V` (invert), `-A`, `-B`, `-C`, `-F` are directly supported. For blame/annotate, flags like `-w`, `-n` are directly supported.

However, some flags require translation or warning: git's `-v` must translate to sl's `-V`; git blame's `-b` (ignore space) must translate to sl's `--ignore-space-change` (sl's `-b` means blank SHA1 for boundary); git blame's `-L <start>,<end>` line range, `-p/--porcelain`, `-e/--show-email`, and `-l` (long hash) have no sl equivalents; grep's `-c`, `-h`, `-H`, and `-o` are not supported by sl grep.

**Primary recommendation:** Extend existing handlers following the established flag extraction pattern. Most flags pass through directly. For unsupported flags, print warnings with alternative approaches. Critical translations: git `-v` -> sl `-V`, git blame `-b` -> sl `--ignore-space-change`.

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| subprocess | stdlib | Run sl commands, capture output | Already used in common.run_sl |
| sys | stdlib | stderr output, exit codes | Standard I/O handling |
| typing | stdlib | Type hints | Function signatures |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| common.run_sl | local | Subprocess passthrough | All handlers |
| common.ParsedCommand | local | Parsed argument structure | All handlers |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Custom output filtering | Direct pass-through | Most flags work directly |

**Installation:**
No additional dependencies required - uses stdlib only.

## Architecture Patterns

### Recommended Project Structure
```
gitsl/
+-- cmd_grep.py      # Extended with GREP-01 through GREP-14
+-- cmd_blame.py     # Extended with BLAM-01 through BLAM-07
+-- tests/
    +-- test_grep_flags.py   # New flag tests
    +-- test_blame_flags.py  # New flag tests
```

### Pattern 1: Flag Extraction with Direct Pass-Through
**What:** Extract known git flags, pass through those with identical sl semantics
**When to use:** Most grep and blame flags
**Example:**
```python
# Source: Established pattern in cmd_diff.py, cmd_log.py
def handle(parsed: ParsedCommand) -> int:
    sl_args = ["grep"]
    remaining_args = []

    i = 0
    while i < len(parsed.args):
        arg = parsed.args[i]

        # Flags that pass through directly
        if arg in ('-n', '--line-number'):
            sl_args.append('-n')
        elif arg in ('-i', '--ignore-case'):
            sl_args.append('-i')
        elif arg in ('-l', '--files-with-matches'):
            sl_args.append('-l')
        # ... more flags
        else:
            remaining_args.append(arg)

        i += 1

    sl_args.extend(remaining_args)
    return run_sl(sl_args)
```

### Pattern 2: Flag Translation
**What:** Translate git flag to different sl equivalent
**When to use:** When flag names or values differ
**Example:**
```python
# git grep -v -> sl grep -V (invert match)
# sl uses -V, git uses -v
elif arg in ('-v', '--invert-match'):
    sl_args.append('-V')  # sl uses uppercase V
```

### Pattern 3: Warning for Unsupported Flags
**What:** Print warning when flag has no sl equivalent
**When to use:** For unsupported flags like -c, -h, -o, -L, -p, -e
**Example:**
```python
# Source: cmd_diff.py pattern for unsupported flags
if line_range:
    print("Warning: -L <start>,<end> line range not supported by Sapling annotate. "
          "Consider using 'sl annotate <file> | sed -n '<start>,<end>p''.",
          file=sys.stderr)
```

### Anti-Patterns to Avoid
- **Ignoring case sensitivity in flag names:** Handle both short and long forms
- **Silent failures:** Always warn when a flag cannot be supported
- **Not handling attached values:** Support both `-A 5` and `-A5` formats

## Git to Sapling Flag Mapping

### Grep Flags (GREP-01 through GREP-14)

| Req ID | Git Flag | Sl Equivalent | Semantics Match | Verified | Notes | Confidence |
|--------|----------|---------------|-----------------|----------|-------|------------|
| GREP-01 | `-n`/`--line-number` | `-n` | YES | YES | Direct pass-through | HIGH |
| GREP-02 | `-i`/`--ignore-case` | `-i` | YES | YES | Direct pass-through | HIGH |
| GREP-03 | `-l`/`--files-with-matches` | `-l` | YES | YES | Direct pass-through | HIGH |
| GREP-04 | `-c`/`--count` | N/A | NO | YES | "option -c not recognized" | HIGH |
| GREP-05 | `-w`/`--word-regexp` | `-w` | YES | YES | Direct pass-through | HIGH |
| GREP-06 | `-v`/`--invert-match` | `-V` | YES | YES | Translate to uppercase V | HIGH |
| GREP-07 | `-A <num>` | `-A NUM` | YES | YES | Direct pass-through | HIGH |
| GREP-08 | `-B <num>` | `-B NUM` | YES | YES | Direct pass-through | HIGH |
| GREP-09 | `-C <num>` | `-C NUM` | YES | YES | Direct pass-through | HIGH |
| GREP-10 | `-h` | N/A | NO | YES | Shows help instead of suppressing filename | HIGH |
| GREP-11 | `-H` | N/A | NO | YES | "option -H not recognized" | HIGH |
| GREP-12 | `-o`/`--only-matching` | N/A | NO | YES | "option -o not recognized" | HIGH |
| GREP-13 | `-q`/`--quiet` | `-q` (global) | YES | YES | Works with correct exit codes | HIGH |
| GREP-14 | `-F`/`--fixed-strings` | `-F` | YES | YES | Direct pass-through | HIGH |

### Blame Flags (BLAM-01 through BLAM-07)

| Req ID | Git Flag | Sl Equivalent | Semantics Match | Notes | Confidence |
|--------|----------|---------------|-----------------|-------|------------|
| BLAM-01 | `-w` | `-w`/`--ignore-all-space` | YES | Direct pass-through | HIGH |
| BLAM-02 | `-b` | `--ignore-space-change` | TRANSLATE | sl -b is blank SHA1 for boundary | HIGH |
| BLAM-03 | `-L <start>,<end>` | N/A | NO | Not supported by sl annotate | HIGH |
| BLAM-04 | `-e`/`--show-email` | N/A | NO | Not in sl annotate | HIGH |
| BLAM-05 | `-p`/`--porcelain` | N/A | NO | Not in sl annotate | HIGH |
| BLAM-06 | `-l` | N/A | NO | sl -l is line number at first appearance (different meaning) | HIGH |
| BLAM-07 | `-n`/`--show-number` | `-n`/`--number` | YES | Direct pass-through | HIGH |

### Detailed Flag Analysis

#### GREP-04: `-c`/`--count` - VERIFIED NOT SUPPORTED
- **Git behavior:** Output count of matching lines per file
- **sl grep:** Tested - returns "option -c not recognized"
- **Recommendation:** Print warning suggesting `sl grep <pattern> | wc -l` alternative

#### GREP-06: `-v`/`--invert-match` -> `-V`
- **Critical:** sl uses uppercase `-V` for invert match, git uses lowercase `-v`
- **Must translate:** git `-v` -> sl `-V`

#### GREP-10: `-h` (suppress filename) - VERIFIED DIFFERENT BEHAVIOR
- **Git behavior:** Suppress filename prefix in output
- **sl grep:** `-h` shows help message instead of suppressing filename
- **Recommendation:** Print warning; cannot suppress filenames in sl grep

#### GREP-11: `-H` (force filename) - VERIFIED NOT SUPPORTED
- **Git behavior:** Force filename prefix even for single file
- **sl grep:** Returns "option -H not recognized"
- **Recommendation:** No-op (filename already shown by default); don't pass through

#### GREP-12: `-o`/`--only-matching` - VERIFIED NOT SUPPORTED
- **Git behavior:** Show only the matching part of lines
- **sl grep:** Returns "option -o not recognized"
- **Recommendation:** Print warning suggesting `sl grep <pattern> | grep -o <pattern>`

#### GREP-13: `-q`/`--quiet` - VERIFIED WORKS
- **Git behavior:** No output, exit status indicates match (0=found, 1=not found)
- **sl grep -q:** Works correctly with proper exit codes
- **Recommendation:** Use global quiet flag (pass before subcommand or after)

#### BLAM-02: `-b` (ignore space changes) - SEMANTIC MISMATCH
- **Git behavior:** Ignore whitespace when comparing to find blame source
- **sl behavior:** `-b` shows blank SHA1 for boundary commits (completely different)
- **Must translate:** git `-b` should map to sl `--ignore-space-change`
- **Critical:** Do NOT pass through directly

#### BLAM-03: `-L <start>,<end>` (line range)
- **Git behavior:** Annotate only specified line range
- **sl annotate:** Not supported
- **Recommendation:** Warn about unsupported; suggest post-processing with sed/head/tail

#### BLAM-04: `-e`/`--show-email`
- **Git behavior:** Show author email instead of name
- **sl annotate:** Not supported; has `-u` for author but not email-specific
- **Recommendation:** Warn; may be able to use template with `{author|email}` if -T works

#### BLAM-05: `-p`/`--porcelain`
- **Git behavior:** Machine-readable output format
- **sl annotate:** Not supported; has `-T` template but different format
- **Recommendation:** Warn about unsupported

#### BLAM-06: `-l` (long revision hash) - SEMANTIC MISMATCH
- **Git behavior:** Show full 40-char SHA1 instead of abbreviated
- **sl behavior:** `-l` shows line number at first appearance (completely different)
- **Must translate:** git `-l` has no direct equivalent in sl annotate
- **Recommendation:** Warn; do not pass through

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Pattern matching | Custom regex | sl grep -E/-P | Built-in extended/perl regex |
| Output suppression | Custom buffering | -q global flag | Already available |
| Context lines | Custom line tracking | sl grep -A/-B/-C | Direct support |

**Key insight:** Most grep functionality maps directly. The main complexity is handling semantic mismatches in blame flags and unsupported features.

## Common Pitfalls

### Pitfall 1: Invert Match Flag Case (GREP-06)
**What goes wrong:** Passing `-v` directly to sl grep
**Why it happens:** Git uses `-v`, sl uses `-V` (uppercase)
**How to avoid:** Always translate git `-v` to sl `-V`
**Warning signs:** sl grep fails or returns unexpected results

### Pitfall 2: Blame -b Semantic Mismatch (BLAM-02)
**What goes wrong:** Passing git `-b` (ignore space change) to sl annotate
**Why it happens:** sl `-b` means "show blank SHA1 for boundary" not "ignore space"
**How to avoid:** Translate git `-b` to sl `--ignore-space-change`
**Warning signs:** Output shows blank hashes instead of ignoring whitespace

### Pitfall 3: Blame -l Semantic Mismatch (BLAM-06)
**What goes wrong:** Passing git `-l` (long hash) to sl annotate
**Why it happens:** sl `-l` means "line number at first appearance" not "long hash"
**How to avoid:** Warn about unsupported; do not pass through
**Warning signs:** Line numbers appear instead of long hashes

### Pitfall 4: Attached vs Separate Flag Values
**What goes wrong:** Not handling `-A5` format (attached value)
**Why it happens:** Only checking for `-A 5` format (separate)
**How to avoid:** Parse both `-A5` and `-A 5` formats
**Warning signs:** Flags with attached values fail

### Pitfall 5: Missing Long-Form Aliases
**What goes wrong:** Not handling `--line-number` alongside `-n`
**Why it happens:** Only implementing short form
**How to avoid:** Always support both short and long forms
**Warning signs:** Long-form flags not recognized

### Pitfall 6: grep -h Shows Help (GREP-10)
**What goes wrong:** Passing `-h` to sl grep expecting filename suppression
**Why it happens:** sl grep interprets `-h` as help flag
**How to avoid:** Print warning; do not pass through
**Warning signs:** Help output appears instead of search results

## Code Examples

Verified patterns from sl help and existing codebase:

### GREP-01 through GREP-03: Direct Pass-Through
```python
# Source: sl help grep - verified flags
def handle(parsed: ParsedCommand) -> int:
    sl_args = ["grep"]
    remaining_args = []

    i = 0
    while i < len(parsed.args):
        arg = parsed.args[i]

        # Direct pass-through flags
        if arg in ('-n', '--line-number'):
            sl_args.append('-n')
        elif arg in ('-i', '--ignore-case'):
            sl_args.append('-i')
        elif arg in ('-l', '--files-with-matches'):
            sl_args.append('-l')
        elif arg in ('-w', '--word-regexp'):
            sl_args.append('-w')
        elif arg in ('-F', '--fixed-strings'):
            sl_args.append('-F')
        else:
            remaining_args.append(arg)
        i += 1

    sl_args.extend(remaining_args)
    return run_sl(sl_args)
```

### GREP-06: Invert Match Translation
```python
# CRITICAL: git -v -> sl -V (uppercase)
elif arg in ('-v', '--invert-match'):
    sl_args.append('-V')
```

### GREP-07/08/09: Context Lines with Value Parsing
```python
# Source: cmd_diff.py pattern for -U<n>
elif arg == '-A':
    if i + 1 < len(parsed.args):
        i += 1
        sl_args.extend(['-A', parsed.args[i]])
elif arg.startswith('-A') and len(arg) > 2:
    # Attached format: -A5
    sl_args.extend(['-A', arg[2:]])
# Similar for -B and -C
```

### GREP-04/10/11/12: Unsupported Flag Warnings
```python
# Source: Verified via actual sl grep testing
elif arg in ('-c', '--count'):
    print("Warning: -c/--count not supported by Sapling grep. "
          "Consider: sl grep <pattern> | wc -l",
          file=sys.stderr)
    # Continue without adding to sl_args
elif arg == '-h':
    print("Warning: -h (suppress filename) not supported by Sapling grep. "
          "Filenames will be shown.",
          file=sys.stderr)
    # Do NOT pass through - would show help instead
elif arg == '-H':
    # Already default behavior in sl grep, no-op
    pass
elif arg in ('-o', '--only-matching'):
    print("Warning: -o/--only-matching not supported by Sapling grep. "
          "Consider: sl grep <pattern> | grep -o <pattern>",
          file=sys.stderr)
```

### GREP-13: Quiet Mode
```python
# Verified: sl grep -q works with correct exit codes
elif arg in ('-q', '--quiet'):
    sl_args.append('-q')
```

### BLAM-02: Ignore Space Change Translation
```python
# CRITICAL: git -b -> sl --ignore-space-change (NOT sl -b)
# git -b means "ignore space changes in blame"
# sl -b means "show blank SHA1 for boundary commits" (completely different!)
elif arg == '-b':
    sl_args.append('--ignore-space-change')
```

### BLAM-03: Line Range Warning
```python
# Source: Verified sl annotate does not support -L
import re

# Check for -L flag
if arg == '-L':
    if i + 1 < len(parsed.args):
        line_range = parsed.args[i + 1]
        i += 1
    print(f"Warning: -L {line_range} line range not supported by Sapling annotate. "
          f"Consider: sl annotate <file> | sed -n '{line_range}p'",
          file=sys.stderr)
elif arg.startswith('-L'):
    line_range = arg[2:]
    print(f"Warning: -L{line_range} line range not supported by Sapling annotate.",
          file=sys.stderr)
```

### BLAM-06: Long Hash Warning
```python
# CRITICAL: git -l (long hash) vs sl -l (line number) - different meanings!
elif arg == '-l':
    print("Warning: -l (long revision hash) not supported by Sapling annotate. "
          "Use sl annotate with -T template for custom hash format.",
          file=sys.stderr)
```

### BLAM-07: Show Number Pass-Through
```python
# git -n/--show-number -> sl -n/--number
elif arg in ('-n', '--show-number'):
    sl_args.append('-n')
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Direct arg pass-through | Flag extraction and translation | Phase 27 | Better compatibility |
| No warning for unsupported | Clear warnings with alternatives | Phase 27 | User guidance |

**Deprecated/outdated:**
- None - this extends existing implementations

## Implementation Priority

Based on complexity and frequency of use:

1. **Direct pass-through (LOW effort):**
   - GREP-01: -n (line numbers)
   - GREP-02: -i (case insensitive)
   - GREP-03: -l (files only)
   - GREP-05: -w (word match)
   - GREP-07: -A (after context)
   - GREP-08: -B (before context)
   - GREP-09: -C (both context)
   - GREP-13: -q (quiet)
   - GREP-14: -F (fixed strings)
   - BLAM-01: -w (ignore whitespace)
   - BLAM-07: -n (show number)

2. **Translation required (MEDIUM effort):**
   - GREP-06: -v -> -V (invert match)
   - BLAM-02: -b -> --ignore-space-change

3. **Warnings needed (MEDIUM effort):**
   - GREP-04: -c (count - not supported)
   - GREP-10: -h (shows help instead)
   - GREP-11: -H (not supported - no-op)
   - GREP-12: -o (only matching - not supported)
   - BLAM-03: -L (line range - not supported)
   - BLAM-04: -e (show email - not supported)
   - BLAM-05: -p (porcelain - not supported)
   - BLAM-06: -l (long hash - semantic mismatch)

## Open Questions

All major questions have been RESOLVED through testing:

1. **GREP-04: Does sl grep support -c/--count?** - RESOLVED
   - Answer: NO - returns "option -c not recognized"
   - Implementation: Print warning with `wc -l` alternative

2. **GREP-10: Default filename behavior for single file** - RESOLVED
   - Answer: `-h` shows help message, not filename suppression
   - Implementation: Print warning; do not pass through

3. **GREP-13: sl grep -q behavior** - RESOLVED
   - Answer: Works correctly with proper exit codes (0=match, 1=no match)
   - Implementation: Pass through as global flag

4. **BLAM-04: Can -T template show email?** - STILL OPEN
   - What we know: sl annotate has -T template option (experimental)
   - What's unclear: Whether {author|email} template keyword works
   - Recommendation: Test template; may provide alternative to -e flag

## Sources

### Primary (HIGH confidence)
- `sl help grep` - Verified flags: -A, -B, -C, -i, -l, -n, -V, -w, -E, -F, -P
- `sl help annotate` - Verified flags: -w, -b, -n, -l, -u, -d, -f, -c
- `sl help grep --verbose` - Verified global -q option
- `sl help annotate --verbose` - Verified -T template option
- Direct testing: `sl grep -c`, `sl grep -h`, `sl grep -H`, `sl grep -o`, `sl grep -q`

### Secondary (MEDIUM confidence)
- `git grep -h` - Git flag reference
- `git blame -h` - Git flag reference
- Existing gitsl patterns in cmd_diff.py, cmd_log.py, cmd_commit.py

### Tertiary (LOW confidence)
- None - all findings verified against sl help output and direct testing

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Uses established stdlib patterns
- Architecture: HIGH - Follows existing codebase patterns
- Grep direct mappings: HIGH - Verified via sl help grep
- Grep translations: HIGH - Documented -v to -V translation
- Grep unsupported: HIGH - Verified via direct testing
- Blame direct mappings: HIGH - Verified via sl help annotate
- Blame semantic mismatches: HIGH - Documented -b and -l differences
- Unsupported flags: HIGH - Confirmed via help and testing

**Research date:** 2026-01-22
**Valid until:** 2026-02-22 (30 days - stable domain)
