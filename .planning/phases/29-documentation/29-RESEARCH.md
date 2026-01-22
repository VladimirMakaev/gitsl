# Phase 29: Documentation - Research

**Researched:** 2026-01-22
**Domain:** README documentation, flag compatibility matrix, staging area limitations
**Confidence:** HIGH

## Summary

This phase updates the gitsl README with comprehensive flag compatibility documentation for all 25 supported git commands. Since v1.3 Flag Compatibility milestone implemented 217 requirements across 9 phases (20-28), the README needs significant updates to reflect the current state of flag support.

The current README is outdated: it lists `--graph` and `--format` as "Not implemented" when they are now implemented, and lacks documentation for most new flags (commit --amend, log --stat, diff --name-only, stash@{n} syntax, etc.). The documentation phase must create a comprehensive flag compatibility matrix and update all per-command tables.

Key challenge: Balance between comprehensive documentation and maintainability. The research recommends grouping flags by translation type (direct pass-through, translated, warning-only, unsupported) rather than listing every flag individually.

**Primary recommendation:** Restructure README with a "Flag Compatibility" section containing categorized flag tables for each command, plus a dedicated section explaining staging area limitations and other fundamental Sapling differences.

## Standard Stack

The established patterns for this documentation:

### Core
| Tool | Purpose | Why Standard |
|------|---------|--------------|
| Markdown tables | Flag matrices | Native GitHub rendering, easy to update |
| Category grouping | Organization | Reduces repetition, shows patterns |
| Inline code | Flag/command references | Visual distinction, copyable |

### Documentation Structure
| Section | Purpose | Location |
|---------|---------|----------|
| Command Support Matrix | High-level overview | Early in README |
| Per-Command Flag Tables | Detailed reference | After quick start |
| Staging Area Limitations | Explain fundamental differences | Dedicated section |
| Translation Notes | Explain why translations differ | Per-flag or grouped |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Per-command tables | Single mega-table | Harder to navigate, too wide |
| Categories (translated/warning) | Alphabetical flags | Loses semantic grouping |
| README sections | Separate docs/ folder | Overkill, splits reference |

## Architecture Patterns

### Recommended Documentation Structure
```
README.md (updated sections)
├── Supported Commands (update status column)
├── Command Reference (expand per-command sections)
│   ├── git log (add LOG-01 to LOG-20 flags)
│   ├── git diff (add DIFF-01 to DIFF-12 flags)
│   ├── git status (add STAT-01 to STAT-05 flags)
│   ├── git add (add ADD-01 to ADD-05 flags)
│   ├── git commit (add COMM-01 to COMM-08 flags)
│   ├── git branch (add BRAN-01 to BRAN-09 flags)
│   ├── git stash (add STSH-01 to STSH-10 flags)
│   ├── git checkout/switch/restore (add CHKT-01 to CHKT-11)
│   ├── git grep (add GREP-01 to GREP-14 flags)
│   ├── git blame (add BLAM-01 to BLAM-07 flags)
│   ├── git clone (add CLON-01 to CLON-09 flags)
│   ├── git rm (add RM-01 to RM-05 flags)
│   ├── git mv (add MV-01 to MV-04 flags)
│   ├── git clean (add CLEN-01 to CLEN-04 flags)
│   ├── git config (add CONF-01 to CONF-08 flags)
│   └── git rev-parse (add REVP-01 to REVP-07 flags)
├── Staging Area Limitations (new section)
└── Translation Reference (new section)
```

### Pattern 1: Categorized Flag Table
**What:** Group flags by translation behavior
**When to use:** Commands with many flags
**Example:**
```markdown
### git log

**Direct pass-through:**
| Flag | Translation |
|------|-------------|
| `--stat` | `sl log --stat` |
| `--patch/-p` | `sl log -p` |
| `--all` | `sl log --all` |

**Translated:**
| Flag | Translation | Notes |
|------|-------------|-------|
| `--author=<pattern>` | `-u <pattern>` | |
| `--grep=<pattern>` | `-k <pattern>` | |
| `--graph` | `-G` | |
| `--since/--after` | `-d ">date"` | |
| `--until/--before` | `-d "<date"` | |

**Warning only (not supported):**
| Flag | Behavior |
|------|----------|
| `-S/-G` (pickaxe) | Prints warning, continues |
```

### Pattern 2: Staging Area Limitations Section
**What:** Dedicated section explaining staging area differences
**When to use:** Once in README, referenced from multiple commands
**Example:**
```markdown
## Staging Area Limitations

Sapling does not have a staging area (index). This affects several git flags:

| Flag | Behavior |
|------|----------|
| `diff --staged/--cached` | Prints warning (no staging area) |
| `restore --staged/-S` | Prints warning (no staging area) |
| `stash --keep-index` | Prints warning (no staging area) |
| `commit -a` | **Removed** (sl -A adds untracked files - safety) |
| `rm --cached` | Prints warning (no staging area) |

When you see a staging area warning, use Sapling's workflow:
- Edit files directly (no staging step)
- Commit all changes with `sl commit`
- Use `sl shelve` to set aside changes temporarily
```

### Pattern 3: Translation Reference Table
**What:** Quick reference for flag translations
**When to use:** Users migrating from git
**Example:**
```markdown
## Common Flag Translations

| Git Flag | Sapling Equivalent | Commands |
|----------|-------------------|----------|
| `-a/--all` | `--all` | log |
| `--author=` | `-u` | log, commit |
| `-b <branch>` | `-u <bookmark>` | clone |
| `-d/--detach` | `--inactive` | switch, checkout |
| `-f/--force` | `-C` | checkout, switch (goto) |
| `--global` | `--user` | config |
| `--graph` | `-G` | log |
| `-n` (limit) | `-l` | log |
| `--unset` | `--delete` | config |
| `-v` (invert) | `-V` | grep |
```

### Anti-Patterns to Avoid
- **Incomplete flag tables:** Document ALL supported flags, not just common ones
- **Missing translation notes:** Explain WHY translations differ
- **Outdated status:** Keep "Not implemented" entries current
- **Generic "passed through":** Be specific about what each flag does

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Flag inventory | Manual list | Extract from REQUIREMENTS.md | Single source of truth |
| Status tracking | Manual | Link to requirement IDs | Traceability |
| Translation details | Guess | Reference plan files | Verified behavior |

**Key insight:** Use the 217 validated requirements as the source of truth for documentation.

## Complete Flag Inventory

### Phase 20: Safety Fixes (SAFE-01 to SAFE-04)
| Requirement | Flag | Behavior |
|-------------|------|----------|
| SAFE-01 | `commit -a/--all` | **Removed** (prints warning) |
| SAFE-02 | `checkout -f/--force` | Translated to `sl goto -C` |
| SAFE-03 | `checkout -m/--merge` | Translated to `sl goto -m` |
| SAFE-04 | `branch -D` | Translated to `-d` (safety) |

### Phase 21: Rev-Parse Expansion (REVP-01 to REVP-07)
| Requirement | Flag | Translation |
|-------------|------|-------------|
| REVP-01 | `--show-toplevel` | `sl root` |
| REVP-02 | `--git-dir` | Returns `.sl` or `.hg` directory |
| REVP-03 | `--is-inside-work-tree` | `sl root` check |
| REVP-04 | `--abbrev-ref HEAD` | `sl log -r . --template {activebookmark}` |
| REVP-05 | `--verify` | `sl log -r <ref>` validation |
| REVP-06 | `--symbolic` | Echo back ref |
| REVP-07 | `--short HEAD` | `sl whereami` |

### Phase 22: Log Flags (LOG-01 to LOG-20)
| Requirement | Flag | Translation | Notes |
|-------------|------|-------------|-------|
| LOG-01 | `--graph` | `-G` | |
| LOG-02 | `--stat` | `--stat` | Direct |
| LOG-03 | `--patch/-p` | `-p` | Direct |
| LOG-04 | `--author=` | `-u <pattern>` | |
| LOG-05 | `--grep=` | `-k <pattern>` | |
| LOG-06 | `--no-merges` | `--no-merges` | Direct |
| LOG-07 | `--all` | `--all` | Direct |
| LOG-08 | `--follow` | `-f` | |
| LOG-09 | `--since/--after` | `-d ">date"` | |
| LOG-10 | `--until/--before` | `-d "<date"` | |
| LOG-11 | `--name-only` | Template output | |
| LOG-12 | `--name-status` | Template output | |
| LOG-13 | `--decorate` | Template with bookmarks | |
| LOG-14 | `--pretty/--format` | `-T` with preset mapping | |
| LOG-15 | `--first-parent` | Revset approximation | |
| LOG-16 | `--reverse` | Revset approximation | |
| LOG-17 | `-S` (pickaxe) | Warning | No sl equivalent |
| LOG-18 | `-G` (pickaxe regex) | Warning | No sl equivalent |
| LOG-19 | `-n/--max-count` | `-l` | |
| LOG-20 | `--oneline` | Template | |

### Phase 23: Diff and Show Flags
**Diff (DIFF-01 to DIFF-12):**
| Requirement | Flag | Translation | Notes |
|-------------|------|-------------|-------|
| DIFF-01 | `--stat` | `--stat` | Direct |
| DIFF-02 | `-w/--ignore-all-space` | `-w` | Direct |
| DIFF-03 | `-b/--ignore-space-change` | `-b` | Direct |
| DIFF-04 | `-U<n>/--unified=<n>` | `-U` | Direct |
| DIFF-05 | `--name-only` | `sl status -mard` | Working dir |
| DIFF-06 | `--name-status` | `sl status -mard` | Working dir |
| DIFF-07 | `--staged/--cached` | Warning | No staging area |
| DIFF-08 | `--raw` | `--raw` | Direct |
| DIFF-09 | `-M/--find-renames` | `-M` | Direct |
| DIFF-10 | `-C/--find-copies` | `-C` | Direct |
| DIFF-11 | `--word-diff` | `--word-diff` | Direct |
| DIFF-12 | `--color-moved` | Warning | Not supported |

**Show (SHOW-01 to SHOW-08):**
| Requirement | Flag | Translation | Notes |
|-------------|------|-------------|-------|
| SHOW-01 | `--stat` | `--stat` | Direct |
| SHOW-02 | `-U<n>` | `-U<n>` | Direct |
| SHOW-03 | `-w` | `-w` | Direct |
| SHOW-04 | `--name-only` | Template | |
| SHOW-05 | `--name-status` | Template | |
| SHOW-06 | `--pretty/--format` | `-T` | |
| SHOW-07 | `-s/--no-patch` | `-s` | Direct |
| SHOW-08 | `--oneline` | Template | |

### Phase 24: Status and Add Flags
**Status (STAT-01 to STAT-05):**
| Requirement | Flag | Translation | Notes |
|-------------|------|-------------|-------|
| STAT-01 | `--ignored` | `-i` | |
| STAT-02 | `-b/--branch` | Template header | |
| STAT-03 | `-v/--verbose` | Note | sl -v differs |
| STAT-04 | `--porcelain/--short` | Output transformation | |
| STAT-05 | `-u/--untracked-files[=<mode>]` | `-mard` modes | |

**Add (ADD-01 to ADD-05):**
| Requirement | Flag | Translation | Notes |
|-------------|------|-------------|-------|
| ADD-01 | `-A/--all` | `sl addremove` | |
| ADD-02 | `-u/--update` | Modified tracked files | |
| ADD-03 | `--dry-run/-n` | `--dry-run` | Direct |
| ADD-04 | `-f/--force` | Warning | Cannot add ignored |
| ADD-05 | `-v/--verbose` | `-v` | Direct |

### Phase 25: Commit and Branch Flags
**Commit (COMM-01 to COMM-08):**
| Requirement | Flag | Translation | Notes |
|-------------|------|-------------|-------|
| COMM-01 | `--amend` | `sl amend` | |
| COMM-02 | `--no-edit` | Omit `-e` | sl amend default |
| COMM-03 | `-F/--file` | `-l` (logfile) | |
| COMM-04 | `--author=` | `-u` | |
| COMM-05 | `--date=` | `-d` | |
| COMM-06 | `-v/--verbose` | Warning | Different semantics |
| COMM-07 | `-s/--signoff` | Custom trailer | |
| COMM-08 | `-n/--no-verify` | Warning | No hook bypass |

**Branch (BRAN-01 to BRAN-09):**
| Requirement | Flag | Translation | Notes |
|-------------|------|-------------|-------|
| BRAN-01 | `-m <old> <new>` | `-m` | Direct |
| BRAN-02 | `-a/--all` | `--all` | |
| BRAN-03 | `-r/--remotes` | `--remote` | |
| BRAN-04 | `-v/--verbose` | Template | |
| BRAN-05 | `-l/--list` | Filter output | |
| BRAN-06 | `--show-current` | Template query | |
| BRAN-07 | `-t/--track` | `-t` | Direct |
| BRAN-08 | `-f/--force` | `-f` | Direct |
| BRAN-09 | `-c/--copy` | Two-step | Get hash + create |

### Phase 26: Stash and Checkout/Switch/Restore Flags
**Stash (STSH-01 to STSH-10):**
| Requirement | Flag | Translation | Notes |
|-------------|------|-------------|-------|
| STSH-01 | `-u/--include-untracked` | `-u` | Direct |
| STSH-02 | `-m/--message` | `-m` | Direct |
| STSH-03 | `show --stat` | `--stat` | Direct |
| STSH-04 | `stash@{n}` | Shelve name lookup | |
| STSH-05 | `-p/--patch` | `-i` (interactive) | |
| STSH-06 | `-k/--keep-index` | Warning | No staging area |
| STSH-07 | `-a/--all` | `-u` + note | |
| STSH-08 | `-q/--quiet` | Suppress output | |
| STSH-09 | `push <pathspec>` | Pass through | |
| STSH-10 | `branch <name>` | Bookmark + unshelve | |

**Checkout/Switch/Restore (CHKT-01 to CHKT-11):**
| Requirement | Flag | Command | Translation | Notes |
|-------------|------|---------|-------------|-------|
| CHKT-01 | `-c/--create` | switch | `sl bookmark` + `goto` | |
| CHKT-02 | `-C/--force-create` | switch | `sl bookmark -f` + `goto` | |
| CHKT-03 | `-s/--source=` | restore | `-r <rev>` | |
| CHKT-04 | `--staged/-S` | restore | Warning | No staging area |
| CHKT-05 | `--detach` | checkout | `--inactive` | |
| CHKT-06 | `-t/--track` | checkout | Note | Limited emulation |
| CHKT-07 | `-d/--detach` | switch | `--inactive` | |
| CHKT-08 | `-f/--force/--discard-changes` | switch | `-C` | |
| CHKT-09 | `-m/--merge` | switch | `-m` | Direct |
| CHKT-10 | `-q/--quiet` | restore | Suppress output | |
| CHKT-11 | `-W/--worktree` | restore | Default (skip) | |

### Phase 27: Grep and Blame Flags
**Grep (GREP-01 to GREP-14):**
| Requirement | Flag | Translation | Notes |
|-------------|------|-------------|-------|
| GREP-01 | `-n/--line-number` | `-n` | Direct |
| GREP-02 | `-i/--ignore-case` | `-i` | Direct |
| GREP-03 | `-l/--files-with-matches` | `-l` | Direct |
| GREP-04 | `-c/--count` | Warning | Not supported |
| GREP-05 | `-w/--word-regexp` | `-w` | Direct |
| GREP-06 | `-v/--invert-match` | `-V` | **Critical: uppercase** |
| GREP-07 | `-A <num>` | `-A` | Direct |
| GREP-08 | `-B <num>` | `-B` | Direct |
| GREP-09 | `-C <num>` | `-C` | Direct |
| GREP-10 | `-h` | Warning | Would show help |
| GREP-11 | `-H` | No-op | Already default |
| GREP-12 | `-o/--only-matching` | Warning | Not supported |
| GREP-13 | `-q/--quiet` | `-q` | Direct |
| GREP-14 | `-F/--fixed-strings` | `-F` | Direct |

**Blame (BLAM-01 to BLAM-07):**
| Requirement | Flag | Translation | Notes |
|-------------|------|-------------|-------|
| BLAM-01 | `-w` | `-w` | Direct |
| BLAM-02 | `-b` | `--ignore-space-change` | **Critical: sl -b differs** |
| BLAM-03 | `-L <start>,<end>` | Warning | Not supported |
| BLAM-04 | `-e/--show-email` | Warning | Not supported |
| BLAM-05 | `-p/--porcelain` | Warning | Not supported |
| BLAM-06 | `-l` | Warning | **Don't pass through** |
| BLAM-07 | `-n/--show-number` | `-n` | Direct |

### Phase 28: Clone, Rm, Mv, Clean, Config Flags
**Clone (CLON-01 to CLON-09):**
| Requirement | Flag | Translation | Notes |
|-------------|------|-------------|-------|
| CLON-01 | `-b <branch>/--branch` | `-u` | |
| CLON-02 | `--depth` | Warning | Use --shallow |
| CLON-03 | `--single-branch` | Warning | Limited support |
| CLON-04 | `-o/--origin` | Warning | Not supported |
| CLON-05 | `-n/--no-checkout` | `-U` | |
| CLON-06 | `--recursive` | Warning | Not supported |
| CLON-07 | `--no-tags` | Warning | Not supported |
| CLON-08 | `-q/--quiet` | `-q` | Direct |
| CLON-09 | `-v/--verbose` | `-v` | Direct |

**Rm (RM-01 to RM-05):**
| Requirement | Flag | Translation | Notes |
|-------------|------|-------------|-------|
| RM-01 | `-f/--force` | `-f` | Direct |
| RM-02 | `--cached` | Warning | No staging area |
| RM-03 | `-n/--dry-run` | Warning | Not supported |
| RM-04 | `-q/--quiet` | Suppress output | |
| RM-05 | `-r/--recursive` | Filtered | sl recursive by default |

**Mv (MV-01 to MV-04):**
| Requirement | Flag | Translation | Notes |
|-------------|------|-------------|-------|
| MV-01 | `-f/--force` | `-f` | Direct |
| MV-02 | `-k` | Warning | Not supported |
| MV-03 | `-v/--verbose` | `-v` | Direct |
| MV-04 | `-n/--dry-run` | `-n` | Direct |

**Clean (CLEN-01 to CLEN-04):**
| Requirement | Flag | Translation | Notes |
|-------------|------|-------------|-------|
| CLEN-01 | `-x` | `--ignored` | Remove ignored too |
| CLEN-02 | `-X` | Warning | Use `--ignored` only |
| CLEN-03 | `-e <pattern>` | `-X` (exclude) | |
| CLEN-04 | `-f/-d/-n` | Existing | Already implemented |

**Config (CONF-01 to CONF-08):**
| Requirement | Flag | Translation | Notes |
|-------------|------|-------------|-------|
| CONF-01 | `--get` | No-op | Default behavior |
| CONF-02 | `--unset` | `--delete --local` | |
| CONF-03 | `--list/-l` | (no key) | Default behavior |
| CONF-04 | `--global` | `--user` | |
| CONF-05 | `--local` | `--local` | Direct |
| CONF-06 | `--system` | `--system` | Direct |
| CONF-07 | `--show-origin` | `--debug` | |
| CONF-08 | `--all` | Warning | Not supported |

## Common Pitfalls

### Pitfall 1: Outdated Documentation
**What goes wrong:** README says "--graph: Not implemented" but it IS implemented
**Why it happens:** README not updated after Phase 22
**How to avoid:** Update all per-command tables based on requirements
**Warning signs:** User confusion, issue reports

### Pitfall 2: Missing Warning Documentation
**What goes wrong:** Users don't understand why flag "does nothing"
**Why it happens:** Warning flags print to stderr but not documented
**How to avoid:** Document all warning-only flags with explanation
**Warning signs:** Support requests about ignored flags

### Pitfall 3: Staging Area Confusion
**What goes wrong:** Users expect --staged/--cached to work
**Why it happens:** Fundamental Sapling difference not explained
**How to avoid:** Dedicated section explaining staging area limitations
**Warning signs:** Repeated questions about staging

### Pitfall 4: Critical Translation Confusion
**What goes wrong:** User passes git grep -v, expects invert match
**Why it happens:** sl -v is verbose, sl -V is invert
**How to avoid:** Highlight CRITICAL translations with notes
**Warning signs:** Wrong results from grep/blame

## Current README Gaps

Based on current README analysis:

| Section | Current State | Needed Update |
|---------|---------------|---------------|
| git log flags | Missing --graph, --stat, --pretty | Add all LOG-01 to LOG-20 |
| git diff flags | Not documented | Add DIFF-01 to DIFF-12 |
| git commit flags | Basic only | Add --amend, --author, -s, etc. |
| git branch flags | Basic only | Add -m, -a, -v, --show-current, etc. |
| git stash flags | Basic only | Add stash@{n}, show --stat, branch |
| git checkout/switch/restore | Basic | Add force, detach, source flags |
| git grep | Not documented | Add all GREP flags |
| git blame | "All flags passed through" | Incorrect - add specifics |
| git clone | Not documented | Add all CLON flags |
| git rm | Basic | Add warning flags |
| git clean | Basic | Add -x, -e flags |
| git config | Basic | Add --unset, --show-origin |
| rev-parse | Incomplete | Add all REVP flags |
| Staging area | Not explained | Add dedicated section |

## Documentation Requirements (DOC-01 to DOC-05)

| Requirement | Content | Approach |
|-------------|---------|----------|
| DOC-01 | Comprehensive flag compatibility matrix | Per-command tables with all flags |
| DOC-02 | Staging-related flags as unsupported | Dedicated "Staging Area Limitations" section |
| DOC-03 | Interactive mode limitations | Note in stash section about -p → -i |
| DOC-04 | Helpful error messages | Document warning messages users will see |
| DOC-05 | Previously undocumented flags | Update all tables from requirements |

## State of the Art

| Old README State | New README State | Change |
|------------------|------------------|--------|
| --graph: "Not implemented" | --graph: `-G` | Phase 22 implemented |
| --format: "Not implemented" | --pretty/--format: Template mapping | Phase 22 implemented |
| rev-parse: "Only --short HEAD" | 7 flags supported | Phase 21 expanded |
| Basic command tables | Comprehensive flag tables | All phases |
| No staging explanation | Dedicated section | New content |

## Open Questions

1. **Table format: categorized vs flat?**
   - What we know: Categorized (pass-through/translated/warning) reduces repetition
   - What's unclear: User preference for finding specific flags
   - Recommendation: Use categorized within each command section

2. **Level of detail for warnings?**
   - What we know: Some warnings suggest alternatives (e.g., "use wc -l")
   - What's unclear: Whether to include all suggestion text
   - Recommendation: Include brief suggestion in Notes column

3. **Separate page vs single README?**
   - What we know: 217 flags is a lot of content
   - What's unclear: Whether README becomes too long
   - Recommendation: Keep in README with good anchor links

## Sources

### Primary (HIGH confidence)
- REQUIREMENTS.md - All 217 requirements with implementation status
- Plan files (20-01 through 28-02) - Exact flag translations and warnings
- Current README.md - Baseline for updates

### Secondary (MEDIUM confidence)
- Phase 14 RESEARCH.md - Documentation patterns and structures

## Metadata

**Confidence breakdown:**
- Flag inventory: HIGH - Derived from validated requirements
- Translation details: HIGH - Verified in plan files
- Documentation structure: HIGH - Established patterns
- Gap analysis: HIGH - Direct README comparison

**Research date:** 2026-01-22
**Valid until:** 2026-02-22 (30 days - until next flag additions)
