---
phase: 27
plan: 01
subsystem: grep-blame-flags
tags: [grep, blame, annotate, flag-translation, warnings]
completed: 2026-01-22
duration: 3m

dependency-graph:
  requires: [26-stash-checkout-flags]
  provides: [grep-flag-support, blame-flag-support]
  affects: [27-02-tests]

tech-stack:
  added: []
  patterns: [flag-extraction-loop, value-parsing, warning-messages]

key-files:
  created: []
  modified:
    - cmd_grep.py
    - cmd_blame.py

decisions:
  - id: GREP-V-TRANSLATION
    choice: "Translate git -v to sl -V for invert match"
    reason: "sl uses uppercase V, git uses lowercase v"
  - id: BLAME-B-TRANSLATION
    choice: "Translate git -b to sl --ignore-space-change"
    reason: "sl -b means blank SHA1 for boundary (completely different semantics)"
  - id: BLAME-L-NO-PASSTHROUGH
    choice: "Do not pass through -l flag, print warning instead"
    reason: "sl -l means line number at first appearance, git -l means long hash"
  - id: GREP-H-NO-PASSTHROUGH
    choice: "Do not pass through -h flag, print warning instead"
    reason: "sl -h shows help message, git -h suppresses filename"

metrics:
  requirements-validated: 21
  lines-added: 214
---

# Phase 27 Plan 01: Grep and Blame Flags Implementation Summary

Grep and blame flag support with critical translations for sl semantic differences

## Summary

Extended cmd_grep.py and cmd_blame.py to support the full range of grep and blame flags specified in requirements GREP-01 through GREP-14 and BLAM-01 through BLAM-07. The implementation follows the established flag extraction pattern from cmd_diff.py, with careful attention to semantic differences between git and Sapling flags.

**Critical translations implemented:**
- git grep -v (invert match) -> sl grep -V (sl uses uppercase V)
- git blame -b (ignore space changes) -> sl annotate --ignore-space-change (sl -b means blank SHA1)

**Flags that must NOT be passed through:**
- git grep -h (suppress filename) - sl -h shows help instead
- git blame -l (long hash) - sl -l shows line number at first appearance

## Tasks Completed

| Task | Name | Commit | Files Modified |
|------|------|--------|----------------|
| 1 | Extend cmd_grep.py with Flag Support | e1e4639 | cmd_grep.py |
| 2 | Extend cmd_blame.py with Flag Support | f2c564f | cmd_blame.py |
| 3 | Verify Handler Integration | (verification) | - |

## Implementation Details

### cmd_grep.py (142 lines)

**Direct pass-through flags:**
- GREP-01: -n/--line-number
- GREP-02: -i/--ignore-case
- GREP-03: -l/--files-with-matches
- GREP-05: -w/--word-regexp
- GREP-13: -q/--quiet
- GREP-14: -F/--fixed-strings

**Context line flags with value parsing:**
- GREP-07: -A <num> (handles both -A 5 and -A5 formats)
- GREP-08: -B <num> (handles both formats)
- GREP-09: -C <num> (handles both formats)

**Translation required:**
- GREP-06: -v/--invert-match -> -V (CRITICAL: sl uses uppercase V)

**Unsupported flags (with warnings):**
- GREP-04: -c/--count - suggests `sl grep | wc -l`
- GREP-10: -h - warns about help display instead of filename suppression
- GREP-11: -H - no-op (already default behavior)
- GREP-12: -o/--only-matching - suggests `sl grep | grep -o`

### cmd_blame.py (100 lines)

**Direct pass-through flags:**
- BLAM-01: -w/--ignore-all-space
- BLAM-07: -n/--show-number

**Translation required:**
- BLAM-02: -b -> --ignore-space-change (CRITICAL: sl -b means blank SHA1 for boundary)

**Unsupported flags (with warnings):**
- BLAM-03: -L <start>,<end> - suggests `sl annotate | sed -n 'range p'`
- BLAM-04: -e/--show-email - author names shown by default
- BLAM-05: -p/--porcelain - suggests -T template
- BLAM-06: -l - warns about semantic mismatch (short hashes by default)

## Decisions Made

| Decision | Choice | Rationale |
|----------|--------|-----------|
| GREP-V-TRANSLATION | Translate -v to -V | sl uses uppercase V for invert match |
| BLAME-B-TRANSLATION | Translate -b to --ignore-space-change | sl -b has completely different meaning |
| BLAME-L-NO-PASSTHROUGH | Warn and skip -l | sl -l means line number, not long hash |
| GREP-H-NO-PASSTHROUGH | Warn and skip -h | sl -h shows help, not filename suppression |

## Verification Results

All verification tests passed:

1. **Module imports:** Both cmd_grep and cmd_blame import correctly
2. **Handler integration:** gitsl.py dispatch works correctly
3. **Flag translation tests:**
   - grep -v correctly translates to sl grep -V
   - grep -A5 correctly parses to sl grep -A 5
   - grep -c prints warning with wc -l alternative
   - blame -b correctly translates to sl annotate --ignore-space-change
   - blame -L prints warning with sed alternative
   - blame -l prints warning and does NOT pass through

## Deviations from Plan

None - plan executed exactly as written.

## Files Changed

| File | Lines | Change Type |
|------|-------|-------------|
| cmd_grep.py | 142 | Extended with flag extraction loop |
| cmd_blame.py | 100 | Extended with flag extraction loop |

## Next Phase Readiness

**Phase 27-02:** Grep and Blame Flags Tests
- Ready for test implementation
- All handlers have been extended with proper flag handling
- Critical translations verified working via mock tests
- Test patterns established in existing test_grep.py and test_blame.py
