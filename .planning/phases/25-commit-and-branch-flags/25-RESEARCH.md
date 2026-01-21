# Phase 25: Commit and Branch Flags - Research

**Researched:** 2026-01-21
**Domain:** Git commit/branch flag translation to Sapling (sl commit/amend/bookmark)
**Confidence:** HIGH

## Summary

This research covers flag compatibility for git commit and git branch commands translating to Sapling equivalents. The commit command maps to `sl commit` for regular commits and `sl amend` for amending. The branch command maps to `sl bookmark` with various flag translations.

Most flags have direct Sapling equivalents with minor syntax differences. Three flags require special handling due to lack of native Sapling support: `--no-verify` (bypass hooks), `--signoff` (trailer appending), and `--copy` (duplicate branch).

**Primary recommendation:** Implement flag translation following established patterns from cmd_log.py and cmd_status.py. Use warnings for unsupported flags, custom implementations for signoff/copy, and config-based workarounds for --no-verify.

## Standard Stack

The established libraries/tools for this domain:

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| subprocess | stdlib | Run sl commands | Direct process execution |
| sys | stdlib | stderr output, exit codes | Standard I/O handling |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| typing | stdlib | Type hints | Function signatures |
| tempfile | stdlib | Config override files | --no-verify workaround |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| tempfile for config | Environment variable | Env vars cleaner but HGRCPATH more complex |

**Installation:**
No additional dependencies required - uses stdlib only.

## Architecture Patterns

### Recommended Project Structure
```
gitsl/
├── cmd_commit.py     # Extended with new flag handlers
├── cmd_branch.py     # Extended with new flag handlers
└── tests/
    ├── test_commit.py   # Extended with flag tests
    └── test_branch.py   # Extended with flag tests
```

### Pattern 1: Flag Extraction and Translation
**What:** Extract git flags, translate to sl equivalents, filter remaining args
**When to use:** All flag translation handlers
**Example:**
```python
# Source: cmd_status.py pattern
def handle(parsed: ParsedCommand) -> int:
    args = list(parsed.args)

    # Extract flags
    amend = '--amend' in args
    no_edit = '--no-edit' in args
    signoff = '-s' in args or '--signoff' in args

    # Filter processed flags
    args = [a for a in args if a not in ('--amend', '--no-edit', '-s', '--signoff')]

    # Build sl command
    if amend:
        cmd = ['amend']
        if not no_edit:
            cmd.append('-e')  # sl amend defaults to no-edit
    else:
        cmd = ['commit']

    return run_sl(cmd + args)
```

### Pattern 2: Value Flag Extraction
**What:** Extract flags that take values (like --author "Name")
**When to use:** -F/--file, --author, --date flags
**Example:**
```python
# Source: cmd_log.py pattern
i = 0
while i < len(args):
    arg = args[i]
    if arg in ('--author', '-u'):
        if i + 1 < len(args):
            author = args[i + 1]
            i += 2
            continue
    elif arg.startswith('--author='):
        author = arg.split('=', 1)[1]
        i += 1
        continue
    remaining.append(arg)
    i += 1
```

### Pattern 3: Custom Message Manipulation
**What:** Modify commit message content programmatically
**When to use:** --signoff implementation
**Example:**
```python
def add_signoff_trailer(message: str, name: str, email: str) -> str:
    """Append Signed-off-by trailer to commit message."""
    trailer = f"\nSigned-off-by: {name} <{email}>"
    if trailer.strip() not in message:
        return message.rstrip() + "\n" + trailer
    return message
```

### Anti-Patterns to Avoid
- **Passing unsupported flags directly:** Always filter or translate flags before passing to sl
- **Ignoring sl amend semantics:** sl amend defaults to reusing message; git commit --amend opens editor
- **Assuming staging area exists:** Sapling has no staging; all changes commit together

## Git to Sapling Flag Mapping

### Commit Flags (COMM-01 through COMM-08)

| Git Flag | Sl Equivalent | Notes | Confidence |
|----------|---------------|-------|------------|
| --amend | `sl amend` (separate command) | NOT a flag, different command | HIGH |
| --no-edit (with amend) | (default behavior) | sl amend reuses message by default; use -e to edit | HIGH |
| -F/--file \<file\> | -l \<file\> or --logfile | Same semantics | HIGH |
| --author "\<author\>" | -u "\<author\>" or --user | Same semantics | HIGH |
| --date "\<date\>" | -d "\<date\>" or --date | Same semantics | HIGH |
| -v/--verbose | Warning only | sl -v shows repo info, not diff in editor | MEDIUM |
| -s/--signoff | Custom implementation | Append "Signed-off-by:" trailer manually | HIGH |
| -n/--no-verify | Config workaround or warning | No native sl flag; see detailed notes | HIGH |

### Branch Flags (BRAN-01 through BRAN-09)

| Git Flag | Sl Equivalent | Notes | Confidence |
|----------|---------------|-------|------------|
| -m \<old\> \<new\> | -m \<old\> \<new\> or --rename | Identical semantics | HIGH |
| -a/--all | -a or --all | Shows remote + local bookmarks | HIGH |
| -r/--remotes | --remote | Shows only remote bookmarks | HIGH |
| -v/--verbose | Template: `--template "{bookmark}: {node\|short} {desc\|firstline}"` | Custom template for commit info | HIGH |
| -l/--list \<pattern\> | Pattern matching via template | Filter bookmark names | MEDIUM |
| --show-current | `sl log -r . --template "{activebookmark}"` | Special template query | HIGH |
| -t/--track \<bookmark\> | -t \<bookmark\> or --track | Track remote bookmark | HIGH |
| -f/--force | -f or --force | Force move bookmark | HIGH |
| -c/--copy \<old\> \<new\> | Custom implementation | Create new bookmark at same rev | MEDIUM |

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Message file reading | Custom file I/O | sl commit -l | sl handles encoding, validation |
| Date parsing | Custom date parsing | sl commit -d | sl accepts multiple date formats |
| Bookmark listing | Custom sl log parsing | sl bookmark --all | Built-in listing command |
| Current branch | git rev-parse parsing | sl log template | Template gives clean output |

**Key insight:** Sapling has comprehensive templating; prefer templates over output parsing.

## Common Pitfalls

### Pitfall 1: sl amend Opens Editor Unexpectedly
**What goes wrong:** User expects --no-edit behavior but sl amend -e opens editor
**Why it happens:** sl amend defaults to reusing message; git commit --amend defaults to opening editor
**How to avoid:** When translating git commit --amend, add -e flag unless --no-edit is also present
**Warning signs:** Tests fail because editor hangs

### Pitfall 2: --no-verify Has No Sapling Equivalent
**What goes wrong:** Passing -n or --no-verify does nothing or causes error
**Why it happens:** Sapling has no built-in hook bypass flag
**How to avoid:** Either: (a) Print warning that hooks will run, or (b) Use HGRCPATH to provide empty hooks config
**Warning signs:** Pre-commit hooks run when user expected bypass

### Pitfall 3: Signoff Requires User Identity
**What goes wrong:** Signoff produces malformed trailer
**Why it happens:** Need to extract user.name and user.email from git or sl config
**How to avoid:** Query `sl config ui.username` to get configured identity
**Warning signs:** Trailer has empty or malformed name/email

### Pitfall 4: Branch -D Safety Already Implemented
**What goes wrong:** Duplicating -D to -d translation
**Why it happens:** Not checking existing implementation
**How to avoid:** Review cmd_branch.py before implementing new flags
**Warning signs:** Existing tests fail

### Pitfall 5: --copy Has No Direct Equivalent
**What goes wrong:** Assuming sl bookmark has --copy flag
**Why it happens:** Git and Mercurial/Sapling have different branch semantics
**How to avoid:** Implement as two operations: get current rev, create new bookmark at that rev
**Warning signs:** Tests expecting single-command behavior

## Code Examples

Verified patterns from official sources:

### COMM-01: Amend Translation
```python
# When git commit --amend is detected:
def handle_amend(args: List[str], has_no_edit: bool) -> int:
    cmd = ['amend']

    # sl amend reuses message by default (like git --no-edit)
    # Only add -e if user wants to edit (git's default without --no-edit)
    if not has_no_edit:
        cmd.append('-e')

    # Translate other flags
    for i, arg in enumerate(args):
        if arg in ('--author', '-u') and i + 1 < len(args):
            cmd.extend(['-u', args[i + 1]])

    return run_sl(cmd)
```

### COMM-03: File Flag Translation
```python
# -F/--file -> -l/--logfile
if arg in ('-F', '--file'):
    if i + 1 < len(args):
        message_file = args[i + 1]
        sl_args.extend(['-l', message_file])
        i += 2
        continue
elif arg.startswith('--file='):
    message_file = arg.split('=', 1)[1]
    sl_args.extend(['-l', message_file])
```

### COMM-07: Signoff Implementation
```python
def get_user_identity() -> tuple:
    """Get user name and email from sl config."""
    result = subprocess.run(
        ['sl', 'config', 'ui.username'],
        capture_output=True, text=True
    )
    # Format: "Name <email>"
    identity = result.stdout.strip()
    if '<' in identity and '>' in identity:
        name = identity.split('<')[0].strip()
        email = identity.split('<')[1].rstrip('>')
        return name, email
    return identity, ''

def add_signoff(message: str) -> str:
    """Add Signed-off-by trailer to message."""
    name, email = get_user_identity()
    trailer = f"Signed-off-by: {name} <{email}>"
    if trailer not in message:
        return message.rstrip() + "\n\n" + trailer
    return message
```

### COMM-08: No-Verify Warning
```python
# Source: Pattern from cmd_add.py force warning
if no_verify:
    print("Warning: --no-verify not directly supported. "
          "Sapling has no native hook bypass. "
          "Pre-commit hooks will still run.",
          file=sys.stderr)
```

### BRAN-04: Verbose with Template
```python
# Show commit info for each bookmark
def list_bookmarks_verbose() -> int:
    result = subprocess.run(
        ['sl', 'bookmark', '--template',
         '{bookmark}: {node|short} {desc|firstline}\n'],
        capture_output=True, text=True
    )
    sys.stdout.write(result.stdout)
    return result.returncode
```

### BRAN-06: Show Current Branch
```python
def show_current_branch() -> int:
    result = subprocess.run(
        ['sl', 'log', '-r', '.', '--template', '{activebookmark}'],
        capture_output=True, text=True
    )
    if result.stdout.strip():
        print(result.stdout.strip())
    # No output if detached (matches git behavior)
    return 0
```

### BRAN-09: Copy Implementation
```python
def copy_branch(old_name: str, new_name: str) -> int:
    """Copy a branch (create new bookmark at same commit)."""
    # Get the commit the old bookmark points to
    result = subprocess.run(
        ['sl', 'log', '-r', f'bookmark({old_name})', '--template', '{node}'],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        sys.stderr.write(f"error: branch '{old_name}' not found\n")
        return 1

    commit = result.stdout.strip()

    # Create new bookmark at that commit
    return run_sl(['bookmark', new_name, '-r', commit])
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Direct flag passthrough | Flag extraction and translation | v1.3 | Proper semantic mapping |
| Basic bookmark ops | Full bookmark flag support | Phase 25 | Feature parity |

**Deprecated/outdated:**
- None - this is new flag support

## Implementation Priority

Based on complexity and value:

1. **Simple translations (LOW effort):**
   - COMM-03: -F -> -l
   - COMM-04: --author -> -u
   - COMM-05: --date -> -d
   - BRAN-01: -m (already works)
   - BRAN-02: -a (already works)
   - BRAN-03: -r -> --remote
   - BRAN-07: -t (already works)
   - BRAN-08: -f (already works)

2. **Command changes (MEDIUM effort):**
   - COMM-01: --amend -> sl amend
   - COMM-02: --no-edit handling
   - BRAN-04: -v with template
   - BRAN-05: -l with pattern matching
   - BRAN-06: --show-current with template

3. **Custom implementations (HIGH effort):**
   - COMM-07: --signoff (message manipulation)
   - COMM-08: --no-verify (warning or config workaround)
   - BRAN-09: --copy (two-step operation)

4. **Warnings only:**
   - COMM-06: -v/--verbose

## Open Questions

Things that couldn't be fully resolved:

1. **--no-verify implementation approach**
   - What we know: Sapling has no native flag; hooks configured via config.hooks
   - What's unclear: Whether HGRCPATH override is reliable in all environments
   - Recommendation: Start with warning; consider config override if users request

2. **Template syntax variations**
   - What we know: `{activebookmark}` works for current bookmark
   - What's unclear: Edge cases with detached head, multiple bookmarks
   - Recommendation: Test thoroughly; empty output for detached is acceptable

## Sources

### Primary (HIGH confidence)
- `sl help commit` - Verified flags: -m, -l, -d, -u, -M, -e
- `sl help amend` - Verified flags: -m, -l, -d, -u, -e, --rebase
- `sl help bookmark` - Verified flags: -m, -d, -f, -a, --remote, -t, --list-remote
- `sl help config.hooks` - Verified hook configuration format

### Secondary (MEDIUM confidence)
- Sapling documentation at sapling-scm.com/docs - Flag descriptions
- Existing gitsl patterns in cmd_log.py, cmd_diff.py, cmd_status.py, cmd_add.py

### Tertiary (LOW confidence)
- Web search for signoff implementation patterns
- Web search for Sapling hook bypass approaches

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Uses established stdlib patterns
- Architecture: HIGH - Follows existing codebase patterns
- Flag translations: HIGH - Verified via sl help commands
- Custom implementations: MEDIUM - Require testing to validate

**Research date:** 2026-01-21
**Valid until:** 2026-02-21 (30 days - stable domain)
