---
phase: 22-log-flags
plan: 01
subsystem: cmd-handlers
tags: [log, flags, translation, template]
dependency-graph:
  requires: []
  provides: [git-log-flags, log-format-translation, log-filter-flags]
  affects: [22-02]
tech-stack:
  added: []
  patterns: [flag-translation, template-mapping, revset-usage]
key-files:
  created: []
  modified: [cmd_log.py]
decisions:
  - id: LOG-PICKAXE-WARNING
    choice: "Print warning for -S/-G pickaxe, don't pass flag"
    reason: "Sapling has no equivalent; user needs guidance"
  - id: LOG-REVSET-APPROX
    choice: "Use revset approximations for --first-parent and --reverse"
    reason: "sl lacks direct equivalent flags; revsets provide similar behavior"
  - id: LOG-TEMPLATE-PRIORITY
    choice: "custom_template > name_status > name_only > decorate > oneline"
    reason: "Explicit format should override implicit format flags"
metrics:
  duration: "~5 minutes"
  completed: 2026-01-21
---

# Phase 22 Plan 01: Log Flags Summary

**One-liner:** Comprehensive git log flag translation supporting 18 new flags via direct mapping, template generation, and revset approximation.

## What Was Built

Extended `cmd_log.py` from basic `-n`/`--oneline` support to comprehensive git log flag handling:

### Direct Pass-through and Simple Translation (LOG-01 to LOG-08)
- `--graph` -> `-G` (ASCII commit graph)
- `--stat` -> `--stat` (pass-through)
- `--patch/-p` -> `-p` (pass-through)
- `--no-merges` -> `--no-merges` (pass-through)
- `--all` -> `--all` (pass-through)
- `--follow` -> `-f` (follow file renames)

### Filter Flags with Value Parsing (LOG-04, LOG-05, LOG-09, LOG-10)
- `--author=<pattern>` -> `-u <pattern>`
- `--grep=<pattern>` -> `-k <pattern>`
- `--since/--after` -> `-d ">date"`
- `--until/--before` -> `-d "<date"`
- Date range combines: `-d "date1 to date2"`

### Output Format Flags (LOG-11 to LOG-14)
- `--name-only` -> template with `{files}`
- `--name-status` -> template with `{file_adds}`, `{file_dels}`, `{file_copies}`
- `--decorate` -> template with `{bookmarks}`
- `--pretty/--format` -> `-T template` with:
  - Preset formats: oneline, short, medium, full
  - Custom format placeholder translation: `%H`, `%h`, `%s`, `%an`, `%ae`, `%ad`, `%ar`, `%d`, `%n`

### Complex Flags and Warnings (LOG-15 to LOG-18)
- `--first-parent` -> revset `first(ancestors(.))`
- `--reverse` -> revset `reverse(ancestors(.))`
- `-S<string>` -> warning with grep alternative suggestion
- `-G<regex>` -> warning with grep -E alternative suggestion

## Technical Decisions

### LOG-PICKAXE-WARNING
Sapling has no equivalent to git's pickaxe search (-S/-G for finding commits that change specific strings). Rather than silently failing or erroring, we:
1. Print a warning to stderr explaining the limitation
2. Suggest an alternative: `sl log -p | grep 'pattern'`
3. Continue execution successfully (return 0)

### LOG-REVSET-APPROX
For `--first-parent` and `--reverse`, we use Sapling's revset language:
- `--first-parent` approximated with `first(ancestors(.))` - follows primary lineage
- `--reverse` uses `reverse(ancestors(.))` - shows oldest commits first

Note: These are approximations. `--first-parent` in git has more nuanced behavior for merge commits.

### LOG-TEMPLATE-PRIORITY
When multiple format flags are specified, we apply this priority:
1. `custom_template` (from `--pretty/--format`)
2. `name_status` (from `--name-status`)
3. `name_only` (from `--name-only`)
4. `decorate` (from `--decorate`)
5. `use_oneline` (from `--oneline`)

This ensures explicit format specifications override implicit ones.

## Commits

| Hash | Description |
|------|-------------|
| d7c03d5 | feat(22-01): add direct pass-through and simple translation flags |
| 5605d80 | feat(22-01): add filter flags with value parsing |
| 447acf9 | feat(22-01): add output format flags |
| 22dfd82 | feat(22-01): add complex flags and warnings |

## Deviations from Plan

None - plan executed exactly as written.

## Verification Results

All verification checks passed:
1. `python -c "import cmd_log; print('OK')"` - OK
2. File size: 312 lines (requirement: 150+)
3. Manual verification:
   - `--graph` translates to `-G`
   - `--author=john` translates to `-u john`
   - `--since="2024-01-01"` translates to `-d ">2024-01-01"`
   - `-Sfunction_name` prints warning with grep alternative

## Next Phase Readiness

Plan 22-02 (testing) can proceed. All 18 new flags are implemented with:
- Direct translations working correctly
- Template generation for format flags
- Value parsing for filter flags
- Warning messages for unsupported pickaxe flags
- Revset approximations for complex flags
