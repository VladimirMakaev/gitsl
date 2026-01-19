# Project Milestones: GitSL

## v1.1 Polish & Documentation (Shipped: 2026-01-19)

**Delivered:** Production-ready package with comprehensive CI/CD, cross-platform testing, PyPI publishing, and documentation.

**Phases completed:** 10-14 (7 plans total)

**Key accomplishments:**

- Cleaned codebase of external tool references for self-contained package
- Built comprehensive test infrastructure with 124 tests and cross-platform parallel runner
- Created pip-installable package with pyproject.toml and proper entry points
- Set up GitHub Actions CI with 9-job matrix (Linux, macOS, Windows × Python 3.9/3.11/3.13)
- Configured PyPI trusted publishing with OIDC (no API tokens)
- Created production-quality README with badges, command matrix, and flag documentation

**Stats:**

- 18 files created/modified
- 3,131 lines of Python
- 124 tests passing
- 5 phases, 7 plans
- 2 days from start to ship

**Git range:** `v1.0.0` → `v1.0.1`

**What's next:** v2.0 - Extended command support based on research and user feedback

---

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
