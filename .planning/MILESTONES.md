# Project Milestones: GitSL

## v1.0 MVP (Shipped: 2026-01-18)

**Delivered:** Git-to-Sapling CLI shim enabling git workflow tools to work transparently with Sapling repositories.

**Phases completed:** 1-9 (12 plans total)

**Key accomplishments:**

- Created git-to-Sapling CLI shim with complete argument parsing (ParsedCommand dataclass, GITSL_DEBUG mode)
- Built golden-master E2E test infrastructure for git vs gitsl output comparison
- Implemented subprocess execution pipeline with proper exit code and I/O passthrough
- Translated core git commands (status, log, diff, init, add, commit, rev-parse) to Sapling equivalents
- Emulated git's porcelain/short status format with sl-to-git status code mapping
- Implemented log --oneline and -N flag translation with sl template syntax
- Added git add -u emulation to stage only modified tracked files
- Graceful unsupported command handling with informative stderr messages

**Stats:**

- 80 files created/modified
- 1,984 lines of Python
- 9 phases, 12 plans
- 1 day from start to ship

**Git range:** `c1c5ed3` (feat(v1.0): init) → `35ca12d` (docs(v1): complete milestone audit)

**What's next:** v1.1 Polish - improvements and additional features based on usage

---
