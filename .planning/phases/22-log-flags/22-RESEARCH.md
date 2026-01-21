# Phase 22: Log Flags - Research

**Researched:** 2026-01-21
**Domain:** Git log flag translation to Sapling equivalents
**Confidence:** HIGH

## Summary

Git `log` is a heavily-used command with numerous flags for filtering, formatting, and customizing commit history output. The current gitsl implementation supports only `-n/--max-count` and `--oneline`. This phase expands support to include 18 additional flags commonly used by developers and tools.

Research confirms that Sapling's `sl log` command has direct equivalents for most git log flags, with some requiring translation (e.g., `--author` to `-u`, `--grep` to `-k`) and others requiring date format conversion (`--since`/`--until` to `-d`). The `--pretty/--format` flag presents the most complexity as git's format placeholders must be mapped to Sapling template keywords.

**Primary recommendation:** Extend the existing cmd_log.py handle() function with flag detection and translation logic. Group related flags (display flags, filter flags, date flags, format flags) for maintainability. Complex flags like `--pretty` should support common presets while passing through simple formats.

## Standard Stack

The established libraries/tools for this domain:

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| re | stdlib | Regex for flag parsing | Handle `-n5`, `-S"string"` attached formats |
| subprocess | stdlib | Execute sl commands | For complex output transformation if needed |
| common.ParsedCommand | internal | Argument parsing | Existing gitsl pattern |
| common.run_sl | internal | Execute sl with passthrough | Standard execution for most flags |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| sys | stdlib | stderr output | Warning messages for unsupported options |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| String manipulation | Dedicated template library | Overkill for simple format mapping |
| dateutil parsing | Manual date string pass-through | Date parsing adds complexity; sl handles git date formats adequately |

**Installation:**
No additional dependencies required - stdlib only.

## Architecture Patterns

### Recommended Command Structure
```
cmd_log.py
handle()
    # Flag categories for translation:
    # 1. Direct pass-through flags (same flag name)
    # 2. Renamed flags (--author -> -u)
    # 3. Date flags (--since/--until -> -d with format)
    # 4. Format flags (--pretty -> -T with template)
    # 5. Output modifier flags (--name-only, --name-status)
```

### Pattern 1: Flag Translation Table
**What:** Define mappings from git flags to sl flags in a structured way
**When to use:** For straightforward flag renames
**Example:**
```python
# Source: https://sapling-scm.com/docs/commands/log/
FLAG_TRANSLATIONS = {
    '--graph': '-G',
    '--stat': '--stat',      # pass-through
    '--patch': '-p',
    '-p': '-p',              # pass-through
    '--author': '-u',        # requires value
    '--grep': '-k',          # requires value
    '--no-merges': '-M',
    '--all': '--all',        # pass-through
    '--follow': '-f',
    '--first-parent': '-r "first(ancestors(.))"',  # revset
    '--reverse': '--rev',    # Note: sl uses different semantics
}
```

### Pattern 2: Value-Attached Flag Parsing
**What:** Handle flags that take values in various forms
**When to use:** --author=pattern, --since="date", -S"string"
**Example:**
```python
# Handle --author=<pattern> or --author <pattern>
if arg.startswith('--author='):
    pattern = arg.split('=', 1)[1]
    sl_args.extend(['-u', pattern])
elif arg == '--author':
    if i + 1 < len(args):
        sl_args.extend(['-u', args[i + 1]])
        i += 1
```

### Pattern 3: Date Range Translation
**What:** Convert git's --since/--after and --until/--before to sl's -d format
**When to use:** Date-based filtering
**Example:**
```python
# Source: https://www.selenic.com/mercurial/hg.1.html (date formats)
# Git: --since="2024-01-01" --until="2024-06-01"
# sl:  -d "2024-01-01 to 2024-06-01"
#
# Git: --since="1 week ago"
# sl:  -d ">-7"  (within 7 days)
#
# Note: For simple cases, sl accepts git-style date strings directly:
# sl log -d ">2024-01-01"  # after date
# sl log -d "<2024-06-01"  # before date
```

### Pattern 4: Template Format Mapping
**What:** Map git's --pretty/--format placeholders to sl template keywords
**When to use:** --pretty=format:"..." or --format="..."
**Example:**
```python
# Source: https://manpages.ubuntu.com/manpages/noble/en/man1/hg.1.html (template keywords)
GIT_TO_SL_PLACEHOLDERS = {
    '%H': '{node}',           # full hash
    '%h': '{node|short}',     # short hash
    '%s': '{desc|firstline}', # subject
    '%b': '{desc}',           # body (full desc for now)
    '%an': '{author|person}', # author name
    '%ae': '{author|email}',  # author email
    '%ad': '{date|isodate}',  # author date
    '%ar': '{date|age}',      # relative date
    '%d': '{bookmarks}',      # ref names (closest equivalent)
    '%n': '\\n',              # newline
}

# Preset formats
PRETTY_PRESETS = {
    'oneline': '{node|short} {desc|firstline}\\n',
    'short': '{node|short}\\n{author|person}\\n\\n    {desc|firstline}\\n',
    'medium': '{node|short}\\nAuthor: {author}\\nDate:   {date|isodate}\\n\\n    {desc|firstline}\\n',
    'full': '{node}\\nAuthor: {author}\\nCommit: {author}\\n\\n    {desc}\\n',
}
```

### Pattern 5: Pickaxe Search Translation
**What:** Handle -S and -G for diff content searching
**When to use:** Finding commits that add/remove specific strings or match patterns
**Example:**
```python
# Git: -S"function_name"  -> sl: -k is keyword search, not pickaxe
# Sapling does NOT have direct equivalent to git's -S/-G pickaxe
# Options:
# 1. Use sl log with -p and grep (complex, not recommended)
# 2. Warn user and suggest alternative
# 3. Pass through and let sl error

# Recommended: Warn and suggest sl grep
if arg.startswith('-S') or arg.startswith('-G'):
    print(f"Warning: {arg[:2]} pickaxe search not directly supported in Sapling.",
          file=sys.stderr)
    print("Consider: sl log -p | grep 'pattern' or sl grep", file=sys.stderr)
    # Optionally: Convert to keyword search as rough approximation
```

### Anti-Patterns to Avoid
- **Over-engineering format parsing:** Don't try to support all git format placeholders; focus on common ones.
- **Silent flag dropping:** If a flag can't be translated, warn the user rather than silently ignoring.
- **Complex date parsing:** Let sl handle date formats when possible; only transform when necessary.
- **Ignoring flag order:** Some sl flags must come before file arguments; maintain proper ordering.

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Date format parsing | Python dateutil conversion | sl's native date handling | sl accepts most git date formats directly |
| Commit graph rendering | ASCII art generation | sl log -G | Built-in graph support identical to git |
| Diffstat generation | Line counting logic | sl log --stat | Built-in diffstat identical to git |
| Author pattern matching | Regex on output | sl log -u pattern | sl handles author matching natively |
| Keyword search | Output parsing | sl log -k pattern | sl handles keyword search natively |

**Key insight:** Most git log flags have direct or near-direct sl equivalents. The translation layer should be thin, primarily renaming flags rather than reimplementing functionality.

## Common Pitfalls

### Pitfall 1: --reverse Semantic Difference
**What goes wrong:** `--reverse` in git reverses chronological order; sl doesn't have this flag
**Why it happens:** sl's log always shows newest first
**How to avoid:** Use revset with `reverse()` function or post-process output
**Warning signs:** Users expect oldest-first output but get newest-first

### Pitfall 2: Date Format Compatibility
**What goes wrong:** sl rejects git's relative date formats like "1 week ago"
**Why it happens:** sl uses different date specification syntax
**How to avoid:** Test with common date formats; transform relative dates to sl format
**Warning signs:** "invalid date" errors from sl

### Pitfall 3: --decorate vs Bookmarks
**What goes wrong:** git's `--decorate` shows branches/tags/HEAD; sl shows bookmarks differently
**Why it happens:** Sapling uses bookmarks instead of branches; different display format
**How to avoid:** Document the behavioral difference; optionally emulate with template
**Warning signs:** Users expect "(HEAD -> main, origin/main)" format

### Pitfall 4: Pickaxe Search Missing
**What goes wrong:** -S and -G don't work because sl lacks this feature
**Why it happens:** Sapling doesn't have git's pickaxe search
**How to avoid:** Warn user clearly; suggest sl grep as alternative
**Warning signs:** Users expecting diff content search get no results or errors

### Pitfall 5: --pretty=format Placeholder Gaps
**What goes wrong:** Some git format placeholders have no sl equivalent
**Why it happens:** Git has more format options than sl templates
**How to avoid:** Map supported placeholders; pass through unknown with warning
**Warning signs:** Output contains literal %x placeholders instead of values

### Pitfall 6: Flag Value Attachment Variations
**What goes wrong:** Fails to parse `--author=name`, `--author name`, and `--author="name with spaces"`
**Why it happens:** Git allows multiple syntaxes for value flags
**How to avoid:** Handle both `=` attached and space-separated values
**Warning signs:** "Unknown flag" errors for valid git syntax

## Code Examples

Verified patterns from official sources:

### Simple Flag Translation
```python
# Source: https://sapling-scm.com/docs/commands/log/
# Direct mappings verified against sl help log

def handle(parsed: ParsedCommand) -> int:
    sl_args = ["log"]
    i = 0
    while i < len(parsed.args):
        arg = parsed.args[i]

        # LOG-01: --graph -> -G
        if arg == '--graph':
            sl_args.append('-G')

        # LOG-02: --stat passes through
        elif arg == '--stat':
            sl_args.append('--stat')

        # LOG-03: --patch/-p passes through
        elif arg in ('--patch', '-p'):
            sl_args.append('-p')

        # ... continue for other flags
        i += 1

    return run_sl(sl_args)
```

### Author/Grep Filter Translation
```python
# LOG-04: --author=<pattern> -> -u <pattern>
# LOG-05: --grep=<pattern> -> -k <pattern>
# Source: https://sapling-scm.com/docs/commands/log/

if arg.startswith('--author='):
    pattern = arg.split('=', 1)[1]
    sl_args.extend(['-u', pattern])
elif arg == '--author':
    if i + 1 < len(parsed.args):
        i += 1
        sl_args.extend(['-u', parsed.args[i]])

if arg.startswith('--grep='):
    pattern = arg.split('=', 1)[1]
    sl_args.extend(['-k', pattern])
elif arg == '--grep':
    if i + 1 < len(parsed.args):
        i += 1
        sl_args.extend(['-k', parsed.args[i]])
```

### Date Range Translation
```python
# LOG-09/LOG-10: --since/--after/--until/--before -> -d
# Source: https://www.selenic.com/mercurial/hg.1.html (date ranges)

# sl -d accepts:
#   ">DATE" for after
#   "<DATE" for before
#   "DATE to DATE" for range

since_date = None
until_date = None

if arg.startswith('--since=') or arg.startswith('--after='):
    since_date = arg.split('=', 1)[1]
elif arg in ('--since', '--after'):
    if i + 1 < len(parsed.args):
        i += 1
        since_date = parsed.args[i]

if arg.startswith('--until=') or arg.startswith('--before='):
    until_date = arg.split('=', 1)[1]
elif arg in ('--until', '--before'):
    if i + 1 < len(parsed.args):
        i += 1
        until_date = parsed.args[i]

# Build sl -d argument
if since_date and until_date:
    sl_args.extend(['-d', f'{since_date} to {until_date}'])
elif since_date:
    sl_args.extend(['-d', f'>{since_date}'])
elif until_date:
    sl_args.extend(['-d', f'<{until_date}'])
```

### Name-Only/Name-Status Output
```python
# LOG-11: --name-only produces filename-only output
# LOG-12: --name-status produces status+filename output
# Source: sl log templates

# sl doesn't have direct --name-only flag; use template
if '--name-only' in args:
    # Template that shows commit + files
    sl_args.extend(['-T', '{node|short} {file_adds} {file_dels} {file_mods}\\n'])
    # Note: This is approximate; may need post-processing for exact git format

if '--name-status' in args:
    # Similar approach with status indicators
    # This requires more complex template or post-processing
    pass
```

### Pretty Format Translation
```python
# LOG-14: --pretty/--format -> -T template
# Source: https://manpages.ubuntu.com/manpages/noble/en/man1/hg.1.html

PRETTY_PRESETS = {
    'oneline': '{node|short} {desc|firstline}\\n',
    'short': 'commit {node|short}\\nAuthor: {author}\\n\\n    {desc|firstline}\\n\\n',
    'medium': 'commit {node|short}\\nAuthor: {author}\\nDate:   {date|isodate}\\n\\n    {desc|firstline}\\n\\n',
    'full': 'commit {node}\\nAuthor: {author}\\nCommit: {author}\\n\\n    {desc}\\n\\n',
}

if arg.startswith('--pretty=') or arg.startswith('--format='):
    format_spec = arg.split('=', 1)[1]

    # Handle preset names
    if format_spec in PRETTY_PRESETS:
        sl_args.extend(['-T', PRETTY_PRESETS[format_spec]])

    # Handle format:... custom format
    elif format_spec.startswith('format:'):
        custom = format_spec[7:]
        # Translate git placeholders to sl template
        translated = translate_format_placeholders(custom)
        sl_args.extend(['-T', translated])
```

### First-Parent and Reverse
```python
# LOG-15: --first-parent follows only first parent
# LOG-16: --reverse shows commits in reverse order
# Source: sl help revsets

if '--first-parent' in args:
    # Use revset to follow first parent only
    # This is complex; may need to wrap the existing rev selection
    pass  # Complex implementation needed

if '--reverse' in args:
    # sl doesn't have --reverse; need to collect output and reverse
    # Or use revset: sl log -r "reverse(ancestors(.))"
    # Note: This changes performance characteristics
    pass  # Complex implementation needed
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Only -n/--oneline | Full flag support | Phase 22 | Users can use familiar git log flags |
| Pass-through only | Flag translation | Phase 22 | Proper semantic mapping |

**Deprecated/outdated:**
- None for this phase - expanding existing implementation

## Git to Sapling Flag Mapping Table

| Git Flag | Sapling Equivalent | Notes | Confidence |
|----------|-------------------|-------|------------|
| `--graph` | `-G` | Direct mapping | HIGH |
| `--stat` | `--stat` | Pass-through | HIGH |
| `--patch/-p` | `-p` | Pass-through | HIGH |
| `--author=<pattern>` | `-u <pattern>` | Rename | HIGH |
| `--grep=<pattern>` | `-k <pattern>` | Keyword search | HIGH |
| `--no-merges` | `-M` or `--no-merges` | Both work in sl | HIGH |
| `--all` | `--all` | Pass-through | HIGH |
| `--follow` | `-f` | Direct mapping | HIGH |
| `--since/--after` | `-d ">DATE"` | Format conversion | MEDIUM |
| `--until/--before` | `-d "<DATE"` | Format conversion | MEDIUM |
| `--name-only` | Template-based | Requires template | MEDIUM |
| `--name-status` | Template-based | Requires template + status logic | LOW |
| `--decorate` | Template with {bookmarks} | Partial equivalent | MEDIUM |
| `--pretty/--format` | `-T template` | Placeholder translation | MEDIUM |
| `--first-parent` | Revset expression | Complex | LOW |
| `--reverse` | Revset or post-process | Complex | LOW |
| `-S<string>` | No equivalent | Pickaxe not supported | LOW |
| `-G<regex>` | No equivalent | Pickaxe not supported | LOW |
| `-n/--max-count` | `-l` | Already implemented | HIGH |
| `--oneline` | Template | Already implemented | HIGH |

## Implementation Priority

Based on usage frequency and implementation complexity:

| Priority | Flags | Reason |
|----------|-------|--------|
| HIGH (easy) | --graph, --stat, -p, --author, --grep, --no-merges, --all, --follow | Direct translations |
| MEDIUM (moderate) | --since/--until, --decorate, --pretty presets | Require some transformation |
| LOW (complex) | --name-only, --name-status, --pretty=format:, --first-parent, --reverse | Require template work or revsets |
| DEFER | -S, -G (pickaxe) | No sl equivalent; warn only |

## Open Questions

Things that couldn't be fully resolved:

1. **Date format edge cases**
   - What we know: sl accepts ">DATE" and "<DATE" syntax
   - What's unclear: Does sl parse "1 week ago" correctly?
   - Recommendation: Test with common date formats; add transformation if needed

2. **--name-only exact format**
   - What we know: sl templates can output file lists
   - What's unclear: Can we match git's exact output format?
   - Recommendation: Implement reasonable approximation; document differences

3. **--pretty=format: completeness**
   - What we know: Core placeholders (%H, %h, %s, %an, %ad) can be mapped
   - What's unclear: Which git placeholders have no sl equivalent?
   - Recommendation: Map common ones; pass through unknown with warning

4. **--reverse performance**
   - What we know: sl doesn't have --reverse flag
   - What's unclear: Is revset reverse() performant for large repos?
   - Recommendation: Test with large histories; document if slow

5. **--first-parent semantics**
   - What we know: sl has revset functions for ancestry
   - What's unclear: Exact revset to replicate git --first-parent
   - Recommendation: Research further or simplify to common use case

## Sources

### Primary (HIGH confidence)
- [Sapling log command documentation](https://sapling-scm.com/docs/commands/log/) - Official sl log flags
- [Mercurial man page](https://manpages.ubuntu.com/manpages/noble/en/man1/hg.1.html) - Template keywords (sl inherits from hg)
- [Mercurial date formats](https://www.selenic.com/mercurial/hg.1.html) - Date range syntax

### Secondary (MEDIUM confidence)
- [Git log documentation](https://git-scm.com/docs/git-log/2.43.0.html) - Git flag reference
- [Git log format cheatsheet](https://github.com/rstacruz/cheatsheets/blob/master/git-log-format.md) - Format placeholders
- Existing gitsl cmd_log.py - Current implementation patterns

### Tertiary (LOW confidence)
- Community posts on git log usage patterns

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Using stdlib Python and existing patterns
- Architecture: HIGH - Extends established cmd_log.py patterns
- Flag mappings: MEDIUM - Most verified, some require testing
- Date handling: MEDIUM - sl generally accepts git dates, edge cases unknown
- Pitfalls: HIGH - Well-documented differences between git and sl

**Research date:** 2026-01-21
**Valid until:** 60 days (stable domain, sl log flags unlikely to change)
