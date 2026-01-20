# v1.3 Flag Compatibility Research Summary

**Project:** GitSL (Git-to-Sapling CLI Wrapper)
**Milestone:** v1.3 Flag Compatibility
**Domain:** CLI compatibility layer
**Researched:** 2026-01-20
**Confidence:** HIGH

## Executive Summary

GitSL v1.3 aims to achieve exhaustive flag coverage for all 25 git commands (21 distinct handlers plus stash subcommands). Research reveals that git commands expose approximately 400+ unique flags across these commands, but the realistic scope is significantly smaller: roughly 50+ flags pass through unchanged, 12 require simple translation, 25+ need emulation or explicit handling, and 8 have critical semantic differences requiring careful treatment.

The fundamental architectural challenge is Sapling's elimination of the git staging area. Flags like `--staged`, `--cached`, and `-a` (commit) have no direct equivalent and represent a category of features that cannot be emulated. The recommended approach is to implement high-impact flag translations first (those users actually use regularly), document staging-related limitations clearly, and prioritize safety over compatibility for destructive operations like `branch -D`.

Key risks include: (1) the `git commit -a` flag which could unexpectedly add untracked files if naively translated to `sl commit -A`, (2) output format differences for tooling that parses git output (already partially addressed for `--porcelain`), and (3) interactive flags (`-p`, `-i`) that may behave differently between systems. The mitigation strategy involves removing problematic flags rather than translating them, since Sapling's no-staging model often makes the flag unnecessary anyway.

## Key Findings

### Current Implementation State

From CURRENT-FLAGS.md:
- **21 command handlers** implementing **24 unique command/subcommand combinations**
- **18 flags** with explicit transformation
- **9 flags** stripped/filtered for safety or compatibility
- **10 commands** with pure pass-through (no explicit flag handling)

**Implementation patterns identified:**
1. Pure passthrough (10 commands)
2. Command translation only (4 commands: blame->annotate, mv->rename, etc.)
3. Flag filtering (2 commands: rm strips -r, branch converts -D to -d)
4. Flag translation (4 commands: log, clean, config, switch)
5. Output transformation (1 command: status --porcelain)
6. Complex routing (3 commands: stash, checkout, add)

### Recommended Stack

No new tooling required for v1.3. The existing Python implementation with command dispatch pattern is well-suited for flag handling expansion.

**Recommended approach:**
- Expand existing cmd_*.py handlers with flag-aware logic
- Add flag validation layer before pass-through
- Implement output transformers where needed
- Add comprehensive test coverage per flag

### Expected Features

**Must have (table stakes):**
- `commit -a` safe handling (currently broken, would add untracked files)
- `checkout -f/--force` translation to `goto -C`
- `status --ignored` pass-through
- `log --graph` translation (sl log -G)
- `log --author`, `--since`, `--until` translation
- `stash -u/--include-untracked` pass-through
- `branch -m` rename translation

**Should have (user experience):**
- `restore --source` translation
- `branch -a`, `-r` listing flags
- `log --stat`, `--patch` pass-through verification
- Stash reference format translation (`stash@{n}` to shelve names)

**Defer (v2+):**
- `--porcelain=v2` format (v1 sufficient for most tools)
- Complex log format template mapping (`--pretty=format:`)
- Interactive mode parity (`-p`, `-i` for patch selection)
- Flags with no Sapling equivalent (document as unsupported)

**Document as unsupported:**
- All `--staged`/`--cached` flags (no staging area)
- `--index` flag on stash pop/apply
- `commit --fixup`/`--squash` (different workflow in Sapling)
- Interactive rebase (not translatable)

### Architecture Approach

The existing command dispatch pattern is appropriate. Each command handler should:
1. Parse incoming git flags
2. Validate against known patterns (pass-through, translate, block, warn)
3. Transform as needed
4. Execute sl command
5. Transform output if needed

**Major components:**
1. **Flag Registry** - Centralized knowledge of flag compatibility per command
2. **Flag Translator** - Transform git flags to sl equivalents
3. **Output Transformer** - Convert sl output to git-compatible format
4. **Safety Layer** - Block or warn on dangerous flag combinations

### Critical Pitfalls

1. **commit -a adding untracked files** - git `-a` stages tracked modified/deleted only; sl `-A` runs addremove (adds untracked). **Fix: Remove -a flag entirely** - sl commits all tracked changes without it.

2. **branch -D data destruction** - git `-D` force deletes label only; sl `-D` strips commits (destructive). **Already handled: Always translate to -d.**

3. **Staging area assumption** - Many git flags assume staging exists (`--staged`, `--cached`, `--index`). **Cannot emulate; must document and warn.**

4. **Stash reference format** - git uses `stash@{0}`, sl uses named shelves. **Implement lookup translation or error with helpful message.**

5. **Date format differences** - git `--since`/`--until` uses different format than sl `-d`. **Validate common formats; warn on complex date expressions.**

## Implications for Roadmap

Based on research, suggested phase structure:

### Phase 1: Critical Safety Fixes
**Rationale:** Safety issues must be fixed before expanding flag support
**Delivers:** Correct behavior for potentially destructive flags
**Addresses:**
- Fix `commit -a` to not use sl -A (remove flag instead)
- Verify branch -D translation coverage is complete
- Add checkout -f/--force translation to goto -C
**Avoids:** Data loss, unexpected file additions
**Estimated scope:** 3-5 flags, high test coverage

### Phase 2: High-Impact Pass-Through Flags
**Rationale:** Many sl flags are identical to git; verify and document
**Delivers:** Working support for commonly-used flags
**Addresses:**
- `log --graph`, `--stat`, `--patch`, `--author`, `--no-merges`, `--follow`
- `diff -w`, `-b`, `-U<n>`, `--stat`
- `status --ignored`
- `stash -u/--include-untracked`
- `grep -n`, `-i`, `-l`, `-c`, `-w`
- `show --stat`, `-U<n>`, `-w`
**Tests:** Verify each flag produces expected output
**Estimated scope:** 30+ flags, mostly verification

### Phase 3: Flag Translation Layer
**Rationale:** Flags with different names but same semantics
**Delivers:** Transparent git-to-sl flag mapping
**Addresses:**
- `log --author=X` -> `sl log -u X`
- `log --since/--until` -> `sl log -d` (with format translation)
- `branch -m` -> `sl bookmark -m`
- `branch -a/-r` -> `sl bookmark -a/--remote`
- `restore --source` -> `sl revert -r`
- `config` flag translations (`--global` -> `--user`)
**Estimated scope:** 12-15 flags

### Phase 4: Output Transformation
**Rationale:** Some git flags require transforming sl output
**Delivers:** Tool-compatible output formats
**Addresses:**
- `log --name-only`, `--name-status` output formatting
- `status -b/--branch` to show branch info
- Stash reference format translation (`stash@{n}`)
- Consider `log --decorate` using templates
**Estimated scope:** 5-8 transformation rules

### Phase 5: Documentation and Unsupported Flags
**Rationale:** Clear documentation prevents user confusion
**Delivers:** Complete documentation of flag support status
**Addresses:**
- Document all staging-related flags as unsupported (with explanation)
- Document interactive mode differences
- Create flag compatibility matrix in README/docs
- Add helpful error messages for unsupported flags
**Estimated scope:** Documentation-heavy, minimal code

### Phase Ordering Rationale

- **Safety first:** Phase 1 addresses the most dangerous gaps that could cause data loss or unexpected behavior
- **Value early:** Phase 2 enables the most commonly-used flags with minimal implementation effort (mostly pass-through)
- **Build on foundation:** Phase 3 translation layer benefits from Phase 2 verification
- **Polish last:** Output transformation and documentation are less urgent than core functionality

### Research Flags

Phases likely needing deeper research during planning:
- **Phase 3 (Date Translation):** git and sl use different date parsing; need to validate format compatibility
- **Phase 4 (Stash References):** Need to design reference translation strategy

Phases with standard patterns (skip research-phase):
- **Phase 1:** Well-defined fixes based on semantic analysis
- **Phase 2:** Straightforward pass-through verification
- **Phase 5:** Documentation only

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Current State | HIGH | Audited from source code directly |
| Git Flags | HIGH | Official git-scm.com documentation |
| Sapling Flags | HIGH | Verified via `sl help --verbose` locally |
| Gap Analysis | HIGH | Cross-referenced both systems thoroughly |
| Semantic Differences | HIGH | Tested/verified critical differences |

**Overall confidence:** HIGH

### Gaps to Address

- **Date format parsing:** Need to test specific date formats with both systems during Phase 3
- **Interactive mode parity:** Unclear how different `-p`/`-i` behavior is in practice; may need user feedback
- **Porcelain v2 demand:** Unknown if any tools require v2 format specifically

## Sources

### Primary (HIGH confidence)
- GitSL source code audit (`cmd_*.py` files)
- [git-scm.com/docs](https://git-scm.com/docs) - official git documentation
- `sl help <command> --verbose` - local Sapling documentation

### Secondary (MEDIUM confidence)
- [sapling-scm.com/docs](https://sapling-scm.com/docs) - Sapling official docs
- [sapling-scm.com/docs/introduction/differences-git](https://sapling-scm.com/docs/introduction/differences-git)

---
*Research completed: 2026-01-20*
*Ready for roadmap: yes*
