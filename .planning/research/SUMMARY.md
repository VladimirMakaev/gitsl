# Project Research Summary

**Project:** GitSL v1.2 More Commands Support
**Domain:** CLI Command Translation (Git to Sapling)
**Researched:** 2026-01-19
**Confidence:** HIGH

## Executive Summary

GitSL v1.2 adds 13 new git commands to the existing shim, translating them to their Sapling equivalents. Research confirms the existing stdlib-only Python architecture scales well for this expansion. The codebase pattern is consistent: each command gets a `cmd_*.py` handler with a `handle(parsed)` function, using shared utilities from `common.py`. No new libraries are required. The key challenge is semantic translation rather than tooling -- understanding how git concepts map to fundamentally different Sapling models.

The commands fall into five complexity categories: (1) simple pass-through (show, clone, grep), (2) command rename (blame->annotate, rm->remove, mv->move, clean->purge), (3) flag translation (config, switch, restore), (4) subcommand routing (stash->shelve, branch->bookmark), and (5) complex disambiguation (checkout). Implementation should proceed from simplest to most complex, building confidence and establishing patterns before tackling the notorious `git checkout` command.

Critical risks center on semantic model differences: Git's staging area vs Sapling's no-staging model, Git branches vs Sapling bookmarks, and most critically, `git checkout`'s overloaded behavior (branch switching, file restoration, and branch creation all in one command). Mitigation requires careful disambiguation logic, respecting the `--` separator, and potentially warning on ambiguous arguments. The `git clean` command also poses data-loss risk if the `-f` safety flag requirement is not enforced.

## Key Findings

### Recommended Stack

The existing stack is fully sufficient. No new dependencies needed.

**Core technologies:**
- **Python >=3.8:** Runtime -- stdlib-only approach is a strength, keeps deps minimal
- **subprocess (stdlib):** Execute sl commands -- existing `run_sl()` pattern works for all new commands
- **dataclasses (stdlib):** ParsedCommand structure -- extends naturally to new commands
- **pytest >=7.0:** Testing -- existing fixtures (`sl_repo`, `sl_repo_with_commit`) support new tests

**Architecture patterns that scale:**
- One file per command (`cmd_*.py`) with consistent `handle(parsed)` interface
- Entry point dispatch in `gitsl.py` (consider registry pattern for 20+ commands)
- Shared utilities in `common.py` for `run_sl()`, argument parsing, debug mode

### Expected Features

**Must have (table stakes):**
- `show <commit>`, `--stat` -- view commit details
- `blame <file>` with `-u`, `-d` flags -- per-line annotations
- `rm <files>`, `mv <src> <dst>` with `-f` flag -- file operations
- `clean -f -d` with dry-run support -- remove untracked files
- `clone <url>` with `-b` branch support -- repository cloning
- `grep <pattern>` with `-i`, `-n` flags -- content search
- `config <key>` with `--global`, `--local` scope -- configuration
- `stash` / `stash pop` / `stash list` / `stash drop` -- temporary saves
- `checkout <ref>`, `checkout -b <name>`, `checkout -- <file>` -- the overloaded classic
- `switch <branch>`, `switch -c <name>` -- modern branch switching
- `restore <file>`, `restore -s <source>` -- modern file restoration
- `branch`, `branch <name>`, `branch -d` -- branch management

**Should have (differentiators):**
- `stash apply` (keep stash after applying)
- `blame -w` (ignore whitespace)
- `grep -A/-B/-C` (context lines)
- `branch -a`, `branch -r` (remote listing)
- `switch/checkout -m` (merge uncommitted changes)

**Defer (v2+):**
- `git blame --porcelain` (machine-readable format transformation)
- `stash@{n}` reference syntax (complex index-to-name translation)
- `checkout --track`, `--orphan` (different tracking model)
- `branch --contains`, `--merged` (commit ancestry analysis)
- Interactive modes (`-i`, `-p` flags requiring terminal control)

### Architecture Approach

The existing handler-per-command pattern extends naturally. New commands integrate by: (1) creating `cmd_*.py`, (2) importing in `gitsl.py`, (3) adding dispatch condition, (4) updating `pyproject.toml` py-modules. Consider introducing a command registry decorator to replace the growing if-chain in `gitsl.py`.

**Major components:**
1. **gitsl.py** -- Entry point, command dispatch (expand with 13 new imports)
2. **common.py** -- Shared utilities (add `translate_flags()` helper, `is_file_path()` for checkout)
3. **cmd_*.py handlers** -- 13 new files following established patterns
4. **conftest.py fixtures** -- Add `sl_repo_with_shelve`, `sl_repo_with_bookmarks` for new commands

**Handler complexity levels discovered in codebase:**
- Level 1: Pass-through (cmd_commit.py pattern)
- Level 2: Flag translation (cmd_log.py pattern)
- Level 3: Output transformation (cmd_status.py pattern)
- Level 4: Multi-step operations (cmd_add.py pattern)

### Critical Pitfalls

1. **Checkout command overloading** -- `git checkout` does three unrelated things (switch branch, restore file, create branch). Incorrect disambiguation causes data loss. **Prevention:** Check for `--` separator first, then file existence, then treat as ref. When truly ambiguous, prefer ref (safer).

2. **Bookmark vs branch model mismatch** -- Git branches are mandatory (always on a branch), Sapling bookmarks are optional (commits exist without bookmarks). **Prevention:** Document behavior difference; consider showing "no active bookmark" state to git users.

3. **Stash/shelve conflict handling** -- Git stash pop keeps the stash on conflict; Sapling unshelve enters merge state requiring `--continue`/`--abort`. **Prevention:** Detect conflict state and preserve shelve; match git's behavior.

4. **Clean command data loss** -- `git clean` requires `-f` for safety; `sl clean` deletes by default. **Prevention:** Enforce `-f` requirement in gitsl wrapper before passing to sl.

5. **Config scope flag differences** -- Git uses `--global`, Sapling uses `--user`. **Prevention:** Flag translation: `--global` -> `--user`, `--system` -> `--system`.

6. **Output format incompatibility** -- `git blame` output format differs from `sl annotate`; tools parse blame output. **Prevention:** Start with pass-through; add format transformation if user feedback indicates need.

## Implications for Roadmap

Based on research, suggested phase structure:

### Phase 1: Direct Pass-through Commands
**Rationale:** Simplest pattern (Level 1 complexity), establishes rhythm, builds confidence
**Delivers:** 6 working commands with minimal risk
**Commands:** show, clone, grep, blame (annotate), rm (remove), mv (move)
**Avoids:** All critical pitfalls -- these are straightforward mappings
**Estimated scope:** ~6 handlers, ~30 lines each

### Phase 2: Flag Translation Commands
**Rationale:** Introduces flag mapping pattern used by later phases
**Delivers:** 3 commands with moderate complexity
**Commands:** config (scope flags), clean (safety enforcement + flag translation), switch (goto with -c create)
**Avoids:** Pitfall #4 (clean data loss) by enforcing -f requirement
**Uses:** New `translate_flags()` utility in common.py
**Estimated scope:** ~3 handlers, ~50 lines each

### Phase 3: Branch and Restore
**Rationale:** Establishes subcommand routing pattern for stash; introduces file restoration pattern for checkout
**Delivers:** 2 commands, prepares patterns for Phase 4
**Commands:** branch (bookmark with subcommand routing), restore (revert with flag translation)
**Avoids:** Pitfall #2 (bookmark model) addressed in branch handler documentation
**Note:** Restore with `--staged` should warn (no staging in Sapling)
**Estimated scope:** ~2 handlers, ~60 lines each

### Phase 4: Stash Operations
**Rationale:** Complex subcommand routing; builds on Phase 3 patterns
**Delivers:** Full stash workflow (save, pop, list, drop, apply)
**Commands:** stash (all subcommands -> shelve/unshelve)
**Avoids:** Pitfall #3 (conflict handling), Pitfall #4 (list format)
**Critical:** Must detect conflict state and preserve shelve on pop
**Estimated scope:** 1 handler with ~5 subcommand functions, ~150 lines

### Phase 5: Checkout (Most Complex)
**Rationale:** Save for last -- benefits from all prior patterns; most critical pitfall area
**Delivers:** The classic overloaded command
**Commands:** checkout (disambiguation between goto, revert, bookmark+goto)
**Avoids:** Pitfall #1 (command overloading) with explicit disambiguation logic
**Uses:** Patterns from switch (Phase 2), restore (Phase 3)
**Implementation approach:** Check `-b` flag first, then `--` separator, then file existence, finally treat as ref
**Estimated scope:** 1 handler, ~100 lines with disambiguation logic

### Phase Ordering Rationale

- **Dependencies:** Checkout builds on patterns from switch (goto), restore (revert), and branch (bookmark). These must come first.
- **Risk mitigation:** Simple commands first builds confidence; complex checkout last allows learning from earlier phases.
- **Pattern establishment:** Flag translation (Phase 2) and subcommand routing (Phase 3) patterns are reused in Phases 4-5.
- **Pitfall avoidance:** Critical pitfalls (#1 checkout, #3 stash conflict, #4 clean safety) each get dedicated focus in their respective phases.

### Research Flags

Phases likely needing deeper research during planning:
- **Phase 4 (Stash):** Verify sl shelve conflict detection; test unshelve error states; validate `--keep` preserves shelve correctly
- **Phase 5 (Checkout):** Edge cases with ambiguous refs/files; behavior with uncommitted changes; `-B` force create semantics

Phases with standard patterns (skip research-phase):
- **Phase 1:** All commands have 1:1 Sapling equivalents documented in official cheat sheet
- **Phase 2:** Flag mappings clearly documented (config, clean, switch)
- **Phase 3:** Branch/bookmark and restore/revert mappings are well-documented

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | No changes needed; existing patterns sufficient |
| Features | HIGH | All commands verified against Sapling docs |
| Architecture | HIGH | Direct codebase analysis; patterns established |
| Pitfalls | HIGH | 25 pitfalls identified from official docs |

**Overall confidence:** HIGH

### Gaps to Address

- **stash@{n} syntax:** Translating index-based references to shelve names adds complexity. Recommend supporting only "most recent" initially.
- **Output format transformation:** Blame and stash list output formats differ. Decide during implementation whether to transform or document.
- **Checkout ambiguity edge cases:** File named same as branch requires testing; may need to prefer explicit `--` usage.
- **Bookmark-less state:** How to represent Sapling's "no active bookmark" to git users expecting to always be on a branch.

## Sources

### Primary (HIGH confidence)
- [Sapling Git Cheat Sheet](https://sapling-scm.com/docs/introduction/git-cheat-sheet/) -- Command mappings
- [Sapling Commands Reference](https://sapling-scm.com/docs/category/commands/) -- All command details
- [Sapling Differences from Git](https://sapling-scm.com/docs/introduction/differences-git/) -- Model differences
- Existing codebase (`gitsl.py`, `common.py`, `cmd_*.py`) -- Established patterns

### Secondary (MEDIUM confidence)
- [Git Documentation](https://git-scm.com/docs) -- Command flag reference
- [Sapling Bookmarks Overview](https://sapling-scm.com/docs/overview/bookmarks/) -- Branch model differences

### Tertiary (LOW confidence)
- Community feedback on git-sapling interop -- Needs validation during implementation

---
*Research completed: 2026-01-19*
*Ready for roadmap: yes*
