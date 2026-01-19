# Phase 10: Cleanup - Research

**Researched:** 2026-01-19
**Domain:** Codebase hygiene / documentation cleanup
**Confidence:** HIGH

## Summary

This research identifies all external tool references in the gitsl codebase that need to be removed or updated to make the project self-contained and generic.

The codebase was originally developed for integration with a specific external tool called "get-shit-done" (GSD). While the **Python source code is already clean** (no references found), the **planning documentation** contains 83+ references across 24+ files that mention:
- "get-shit-done" as a use case or integration target
- "@~/.claude/get-shit-done/" file paths (workflow references)
- "GSD", "gsd-verifier", "gsd-integration" identifiers
- "/gsd:plan-phase" commands

**Primary recommendation:** Remove or generalize these references in planning docs. The Python source code requires NO changes.

## Scope Clarification

### Requirements Analysis

- **CLEAN-01**: Remove external tool references from codebase
  - Python source files: **ALREADY CLEAN** (0 references)
  - Only planning docs need cleanup

- **CLEAN-02**: Remove external tool references from comments/docs
  - Planning documentation: **83+ references across 24+ files**

### Success Criteria Verification

1. "No references to external tools remain in Python source files" - **ALREADY SATISFIED**
2. "No references to external tools remain in comments or docstrings" - Python docstrings are clean, planning docs need work
3. "Codebase is clean and self-contained" - After planning doc cleanup

## Detailed Findings

### Category 1: Python Source Files (0 references)

**Status:** ALREADY CLEAN

Searched all `.py` files in repository for patterns:
- `get-shit-done`, `get_shit_done`
- `GSD`, `gsd`
- `glittercowboy`

**Result:** No matches found. The production code is self-contained.

### Category 2: Planning Documentation References

#### Pattern A: "get-shit-done" text references (43 occurrences, 20 files)

Files with occurrence counts:

| File | Count | Type |
|------|-------|------|
| `.planning/MILESTONES.md` | 1 | Project description |
| `.planning/INTEGRATION.md` | 1 | Integration context |
| `.planning/milestones/v1.0-REQUIREMENTS.md` | 1 | Use case mention |
| `.planning/milestones/v1.0-ROADMAP.md` | 2 | Use case mentions |
| `.planning/phases/01-script-skeleton/01-01-PLAN.md` | 2 | Workflow refs |
| `.planning/phases/02-e2e-test-infrastructure/02-01-PLAN.md` | 2 | Workflow refs |
| `.planning/phases/02-e2e-test-infrastructure/02-02-PLAN.md` | 2 | Workflow refs |
| `.planning/phases/03-execution-pipeline/03-01-PLAN.md` | 2 | Workflow refs |
| `.planning/phases/03-execution-pipeline/03-02-PLAN.md` | 2 | Workflow refs |
| `.planning/phases/04-direct-command-mappings/04-01-PLAN.md` | 2 | Workflow refs |
| `.planning/phases/04-direct-command-mappings/04-02-PLAN.md` | 2 | Workflow refs |
| `.planning/phases/05-file-operation-commands/05-01-PLAN.md` | 2 | Workflow refs |
| `.planning/phases/06-status-output-emulation/06-01-PLAN.md` | 3 | Workflow refs + use case |
| `.planning/phases/06-status-output-emulation/06-RESEARCH.md` | 3 | Use case context |
| `.planning/phases/06-status-output-emulation/06-VERIFICATION.md` | 2 | Integration tests |
| `.planning/phases/07-log-output-emulation/07-01-PLAN.md` | 3 | Workflow refs + use case |
| `.planning/phases/08-add-u-emulation/08-01-PLAN.md` | 3 | Workflow refs + use case |
| `.planning/phases/09-unsupported-command-handling/09-01-PLAN.md` | 3 | Workflow refs + use case |
| `.planning/phases/09-unsupported-command-handling/09-01-SUMMARY.md` | 2 | Design rationale |
| `.planning/phases/09-unsupported-command-handling/09-RESEARCH.md` | 3 | Design context |

#### Pattern B: Workflow file path references (24 occurrences, 12 files)

Pattern: `@~/.claude/get-shit-done/workflows/` and `@~/.claude/get-shit-done/templates/`

These are file include directives in PLAN.md files. They reference external workflow configuration files.

All 12 PLAN.md files contain exactly 2 lines each:
```
@~/.claude/get-shit-done/workflows/execute-plan.md
@~/.claude/get-shit-done/templates/summary.md
```

Files affected:
- All `*-PLAN.md` files in phases 01-09 (12 files total)

#### Pattern C: GSD identifier references (16 occurrences, 12 files)

Patterns: `gsd-verifier`, `gsd-integration`, `GSD`

| File | Pattern | Context |
|------|---------|---------|
| `.planning/INTEGRATION.md` | `GSD Workflow`, `GSD workflow` | Flow names |
| `.planning/milestones/v1.0-REQUIREMENTS.md` | `GSD commands`, `GSD` | Scope limitations |
| `.planning/milestones/v1.0-MILESTONE-AUDIT.md` | `GSD Workflow`, `gsd-integration-checker` | Verifier names |
| `.planning/STATE.md` | `/gsd:plan-phase 10` | Command reference |
| 9 VERIFICATION.md files | `gsd-verifier` | Verifier attribution |

#### Pattern D: State file command references (1 occurrence, 1 file)

File: `.planning/STATE.md`
Line: `Resume with: /gsd:plan-phase 10`

This references an external workflow command format.

### Category 3: No References Found

- No "glittercowboy" references (GitHub org name not present)
- No external tool references in test files
- No external tool references in Python docstrings

## Recommended Approach

### Decision: Remove vs Replace

Since this is historical planning documentation (v1.0 is shipped), there are two options:

**Option A: Delete workflow reference lines entirely**
- Remove `@~/.claude/get-shit-done/*` lines from all PLAN.md files
- Pros: Simple, clean
- Cons: Loses context that plans had execution workflows

**Option B: Replace with generic placeholder**
- Replace with comment like `# [Execution workflow removed - v1.0 plans are archived]`
- Pros: Explains why lines were removed
- Cons: More work, adds visual noise

**Recommendation:** Option A (delete entirely). These plans are completed and archived.

### Cleanup Strategy by File Type

| File Type | Strategy | Action |
|-----------|----------|--------|
| PLAN.md files (12) | Automated | Delete `@~/.claude/get-shit-done/*` lines |
| RESEARCH.md files (3) | Manual | Replace "get-shit-done" with generic "external tools" |
| VERIFICATION.md files (9) | Automated | Replace "gsd-verifier" with "Claude verifier" |
| INTEGRATION.md | Manual | Replace "GSD Workflow" with "Git Workflow" |
| MILESTONES.md | Manual | Generalize tool description |
| v1.0-REQUIREMENTS.md | Manual | Replace "GSD" with generic term |
| v1.0-ROADMAP.md | Manual | Generalize mentions |
| v1.0-MILESTONE-AUDIT.md | Manual | Update verifier names |
| STATE.md | Manual | Remove/update command reference |
| SUMMARY.md files (2) | Manual | Generalize tool references |

### Automation Feasibility

**Can be automated (search-replace):**
1. Delete lines containing `@~/.claude/get-shit-done/` - exact match, safe to delete entire line
2. Replace `(gsd-verifier)` with `(Claude verifier)` - exact match
3. Replace `gsd-integration-checker` with `integration-checker` - exact match

**Requires manual review:**
1. "get-shit-done" in prose - context varies, some may need rewording
2. "GSD" as abbreviation - may need full replacement or deletion based on context
3. `/gsd:plan-phase` command - needs to be removed or replaced

## File Inventory

### Files Requiring Changes (24 total)

```
.planning/
├── INTEGRATION.md                    # 3 references (GSD Workflow, get-shit-done)
├── MILESTONES.md                     # 1 reference (get-shit-done)
├── STATE.md                          # 1 reference (/gsd:plan-phase)
├── milestones/
│   ├── v1.0-MILESTONE-AUDIT.md       # 2 references (GSD, gsd-integration)
│   ├── v1.0-REQUIREMENTS.md          # 3 references (GSD, get-shit-done)
│   └── v1.0-ROADMAP.md               # 2 references (get-shit-done)
└── phases/
    ├── 01-script-skeleton/
    │   ├── 01-01-PLAN.md             # 2 refs (@~/.claude lines)
    │   └── 01-VERIFICATION.md        # 1 ref (gsd-verifier)
    ├── 02-e2e-test-infrastructure/
    │   ├── 02-01-PLAN.md             # 2 refs (@~/.claude lines)
    │   ├── 02-02-PLAN.md             # 2 refs (@~/.claude lines)
    │   └── 02-VERIFICATION.md        # 1 ref (gsd-verifier)
    ├── 03-execution-pipeline/
    │   ├── 03-01-PLAN.md             # 2 refs (@~/.claude lines)
    │   ├── 03-02-PLAN.md             # 2 refs (@~/.claude lines)
    │   └── 03-VERIFICATION.md        # 1 ref (gsd-verifier)
    ├── 04-direct-command-mappings/
    │   ├── 04-01-PLAN.md             # 2 refs (@~/.claude lines)
    │   ├── 04-02-PLAN.md             # 2 refs (@~/.claude lines)
    │   └── 04-VERIFICATION.md        # 1 ref (gsd-verifier)
    ├── 05-file-operation-commands/
    │   ├── 05-01-PLAN.md             # 2 refs (@~/.claude lines)
    │   └── 05-VERIFICATION.md        # 1 ref (gsd-verifier)
    ├── 06-status-output-emulation/
    │   ├── 06-01-PLAN.md             # 4 refs (workflow + use case)
    │   ├── 06-RESEARCH.md            # 3 refs (use case context)
    │   └── 06-VERIFICATION.md        # 3 refs (gsd-verifier + integration)
    ├── 07-log-output-emulation/
    │   ├── 07-01-PLAN.md             # 4 refs (workflow + use case)
    │   └── 07-VERIFICATION.md        # 1 ref (gsd-verifier)
    ├── 08-add-u-emulation/
    │   ├── 08-01-PLAN.md             # 4 refs (workflow + use case)
    │   └── 08-VERIFICATION.md        # 1 ref (gsd-verifier)
    └── 09-unsupported-command-handling/
        ├── 09-01-PLAN.md             # 4 refs (workflow + use case)
        ├── 09-01-SUMMARY.md          # 2 refs (design rationale)
        ├── 09-RESEARCH.md            # 3 refs (design context)
        └── 09-VERIFICATION.md        # 1 ref (gsd-verifier)
```

### Files Already Clean

All Python source files (15 total):
- `gitsl.py`, `common.py`
- `cmd_*.py` (7 files)
- All `tests/*.py` files (11 files)

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Line deletion | Custom script | `grep -v` or Python file edit | One-time operation, keep simple |
| Bulk replacement | Complex regex | Simple `sed` or Python `replace()` | Replacements are exact strings |

## Common Pitfalls

### Pitfall 1: Incomplete search patterns
**What goes wrong:** Missing case variations (GSD vs gsd)
**How to avoid:** Search for all case variations: `get-shit-done`, `GSD`, `gsd`, `Gsd`
**Prevention:** Verify with case-insensitive grep after cleanup

### Pitfall 2: Breaking markdown formatting
**What goes wrong:** Deleting lines leaves orphaned list items or broken tables
**How to avoid:** Review changes in context, not just diff
**Prevention:** Render markdown after changes to verify formatting

### Pitfall 3: Removing too much context
**What goes wrong:** Historical documentation loses meaning
**How to avoid:** Replace rather than delete where prose context exists
**Prevention:** Keep enough context for future readers to understand design rationale

## Verification Strategy

Post-cleanup verification:

```bash
# Verify no references remain
grep -ri "get-shit-done" .planning/ && echo "FAIL" || echo "PASS"
grep -ri "@~/.claude/get-shit-done" .planning/ && echo "FAIL" || echo "PASS"
grep -ri "gsd-verifier" .planning/ && echo "FAIL" || echo "PASS"
grep -ri "gsd-integration" .planning/ && echo "FAIL" || echo "PASS"
grep -r "/gsd:" .planning/ && echo "FAIL" || echo "PASS"

# Verify Python files still clean
grep -ri "get-shit-done\|gsd\|glittercowboy" *.py tests/ && echo "FAIL" || echo "PASS"
```

## Effort Estimate

| Category | Files | Time Estimate |
|----------|-------|---------------|
| Automated line deletion | 12 PLAN.md files | 5 min |
| Automated replacement | 9 VERIFICATION.md files | 5 min |
| Manual prose updates | 8 files | 20 min |
| Verification | All files | 5 min |
| **Total** | **24 files** | **~35 min** |

## Sources

### Primary (HIGH confidence)
- Direct codebase grep analysis
- File content review

### Verification Performed
- Python source files: Exhaustive grep, 0 matches
- Planning docs: Pattern-based grep with counts
- Case variations checked: get-shit-done, GSD, gsd, glittercowboy

## Metadata

**Confidence breakdown:**
- Python source file status: HIGH - exhaustive search, verified clean
- Planning doc inventory: HIGH - grep counts verified per file
- Recommended approach: HIGH - straightforward text replacement

**Research date:** 2026-01-19
**Valid until:** Phase completion (one-time cleanup)
