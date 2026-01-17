# Project Research Summary

**Project:** gitsl - Git to Sapling CLI Shim
**Domain:** CLI Command Translation / VCS Wrapper
**Researched:** 2026-01-17
**Confidence:** HIGH

## Executive Summary

The gitsl project is a CLI shim that intercepts git commands and translates them to Sapling (sl) equivalents. This is a well-understood pattern in the CLI wrapper domain. The optimal approach uses Python stdlib exclusively (subprocess, sys, os), with a pipeline architecture: Parse -> Translate -> Execute -> Transform. The key insight is to use `os.execvp()` for simple passthrough commands (zero overhead, natural signal handling) and `subprocess.run()` only when output transformation is needed.

The recommended stack is minimal: direct `sys.argv` access for argument extraction, dictionary dispatch for command routing, and subprocess for execution. Argparse is explicitly rejected because it fights against passthrough semantics and fails on unknown flags. The architecture should support three execution tiers: process replacement (execvp) for 1:1 translations, simple subprocess for argument transformation, and captured subprocess for output transformation.

The primary risk is subprocess handling pitfalls: deadlock from pipe buffering, lost exit codes, and broken Ctrl+C. These must be addressed in Phase 1 or nothing else works. Secondary risks include git reference syntax translation (`HEAD^` vs `.^`) and output format emulation (porcelain mode). The zero-dependency, single-file constraint is well-suited to this problem domain.

## Key Findings

### Recommended Stack

Python stdlib only, with a clear execution hierarchy:

**Core technologies:**
- **sys.argv**: Direct argument access without argparse overhead or unknown-flag errors
- **os.execvp()**: Process replacement for passthrough commands, natural signal/TTY handling
- **subprocess.run()**: For commands needing transformation, with explicit exit code propagation
- **shutil.which()**: Finding sl executable (and optionally real git for fallback)

Argparse was explicitly rejected due to: failing on unknown flags, awkward git-style subcommand handling, and unnecessary validation overhead. The shim should not validate arguments.

### Expected Features

**Must have (table stakes):**
- Command routing with subcommand dispatch
- Core commands: status, add, commit, log, diff, rev-parse, init
- Exit code preservation for CI/CD compatibility
- `--porcelain` emulation for status (CRITICAL for tooling)
- `--oneline` emulation for log via Sapling's `--template`
- Unknown command passthrough to sl

**Should have (competitive):**
- Flag translation tables per command
- Environment variable propagation
- Debug mode (`--debug` to show translated command)
- stderr passthrough for error visibility

**Defer (v2+):**
- Full git compatibility layer (hundreds of commands)
- Git alias support
- Interactive mode emulation (add -i, rebase -i)
- Configuration file system

### Architecture Approach

Pipeline architecture with four stages: Parse, Translate, Execute, Transform. Dictionary dispatch for O(1) command lookup. Single-file organization with clear section boundaries using comment headers. Dataclasses for structured data flow (ParsedCommand, TranslatedCommand, ExecutionResult).

**Major components:**
1. **Translation Tables** - DIRECT_COMMAND_MAP for 1:1 commands, COMPLEX_COMMANDS for handlers
2. **Parser** - Extract command name and args from sys.argv, minimal processing
3. **Executor** - Three-tier: execvp for passthrough, run() for transformations
4. **Output Transformer** - Only when git output format must be matched (porcelain, oneline)

### Critical Pitfalls

1. **Subprocess deadlock** - Using wait() with PIPE causes hangs on large output. Always use communicate() or avoid capturing entirely.

2. **Exit code loss** - Forgetting to propagate returncode breaks CI pipelines. Every path must end with sys.exit(result.returncode).

3. **Infinite recursion** - If shim is named `git` and shells out to `git`, it calls itself. Solution: always delegate to `sl`, never to git.

4. **Signal handling (Ctrl+C)** - SIGINT must cleanly terminate subprocess. Use try/except KeyboardInterrupt with proc.terminate().

5. **shell=True injection** - Never use shell=True with user input. Pass args as list to subprocess.

## Implications for Roadmap

Based on research, suggested phase structure:

### Phase 1: Core Execution Pipeline
**Rationale:** Subprocess handling and exit codes must be correct from the start; all other features depend on this foundation.
**Delivers:** Working shim that can route commands to sl and preserve exit codes.
**Addresses:** Command routing, exit code preservation, unknown command passthrough
**Avoids:** Deadlock, exit code loss, infinite recursion, Ctrl+C issues

### Phase 2: Command Translation Tables
**Rationale:** Once execution works, add the translation layer for direct command mappings.
**Delivers:** Direct 1:1 translations (status, diff, log, add, commit, etc.)
**Uses:** Dictionary dispatch from STACK.md
**Implements:** Translation Tables component from architecture

### Phase 3: Flag Translation
**Rationale:** Commands work but flags need translation (git -a vs Sapling default behavior, --oneline emulation).
**Delivers:** Flag handling for complex commands, --oneline via --template
**Addresses:** Flag translation tables, per-command handlers
**Avoids:** Flag differences pitfall

### Phase 4: Output Transformation
**Rationale:** Some tools depend on git's exact output format (porcelain mode).
**Delivers:** --porcelain emulation for status, output format matching
**Addresses:** Table stakes output format features
**Avoids:** Porcelain vs human output confusion

### Phase 5: Edge Cases and Polish
**Rationale:** Handle remaining edge cases, improve error messages, add debug mode.
**Delivers:** Environment variable handling, debug output, better error messages
**Addresses:** Nice-to-have features
**Avoids:** Encoding mismatches, empty argument handling

### Phase Ordering Rationale

- Phase 1 first because all other phases depend on correct subprocess handling
- Phases 2-3 build the translation layer incrementally (simple commands first, then flags)
- Phase 4 separated because output transformation is optional for many commands
- Phase 5 last because edge cases are polish, not core functionality

### Research Flags

Phases likely needing deeper research during planning:
- **Phase 4:** Output transformation for --porcelain requires mapping Sapling status codes to git's 2-character format
- **Phase 3:** Flag translation for checkout (maps to goto OR revert depending on context)

Phases with standard patterns (skip research-phase):
- **Phase 1:** subprocess.run/execvp patterns well-documented
- **Phase 2:** Dictionary dispatch is a standard Python pattern
- **Phase 5:** Standard error handling patterns

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | Python subprocess and stdlib well-documented, patterns verified |
| Features | MEDIUM-HIGH | Based on Sapling official docs, some flag behaviors need validation |
| Architecture | HIGH | Pipeline pattern well-established for CLI translation |
| Pitfalls | HIGH | All verified against Python official docs and issue trackers |

**Overall confidence:** HIGH

### Gaps to Address

- **rev-parse --show-toplevel**: No direct Sapling equivalent documented; may need custom implementation
- **Status code mapping**: Exact translation from Sapling single-char to git two-char format needs testing
- **Reference syntax**: Translation of complex ref ranges (Y..X to X % Y) needs comprehensive testing
- **Interactive commands**: histedit vs rebase -i may have workflow differences

## Sources

### Primary (HIGH confidence)
- [Python subprocess documentation](https://docs.python.org/3/library/subprocess.html) - Execution patterns
- [Sapling Git Cheat Sheet](https://sapling-scm.com/docs/introduction/git-cheat-sheet/) - Command mappings
- [Python argparse issues](https://bugs.python.org/issue9334) - Known limitations

### Secondary (MEDIUM confidence)
- [Sapling command docs](https://sapling-scm.com/docs/commands/) - Individual command flags
- [Git status porcelain format](https://git-scm.com/docs/git-status) - Output format requirements

### Tertiary (LOW confidence)
- Community wrapper patterns - General architecture inspiration

---
*Research completed: 2026-01-17*
*Ready for roadmap: yes*
