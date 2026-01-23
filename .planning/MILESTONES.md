# Project Milestones: GitSL

## v1.3 Flag Compatibility (Shipped: 2026-01-23)

**Delivered:** Comprehensive flag compatibility for all 19 supported git commands with 191 flags translated, warnings for semantic differences, and complete documentation.

**Phases completed:** 20-29 (18 plans total)

**Key accomplishments:**

- Critical safety fixes: commit -a flag removal (prevents untracked file addition), checkout -f/-m translation
- Rev-parse expansion: 7 new flag handlers for --show-toplevel, --git-dir, --is-inside-work-tree, --abbrev-ref HEAD
- Log flags: 20 flags including --graph, --stat, --author, --since/--until, --pretty/--format templates
- Diff/show flags: 20 flags including --name-only, --name-status, warnings for --staged/--cached (no staging area)
- Stash/checkout/switch/restore: 21 flags including stash@{n} syntax translation to shelve names
- Grep/blame: 21 flags with critical translations (grep -v to -V, blame -b to --ignore-space-change)
- Clone/rm/mv/clean/config: 30 flags including --branch, --depth, --unset, --show-origin
- Complete README flag documentation with staging area limitations section and common translations table

**Stats:**

- 21 source files modified
- 3,247 lines of Python (source), 7,169 lines of tests
- 480 tests passing
- 10 phases, 18 plans, 100 commits
- 3 days from start to ship

**Git range:** `160860c` (docs: complete v1.3 flag compatibility research) → `10d3524` (docs(29): complete phase 29 documentation)

**What's next:** User feedback and v1.4 planning (potential: worktree support, remote operations)

---

## v1.2 More Commands Support (Shipped: 2026-01-20)

**Delivered:** Extended command support with 13 additional git commands translated to Sapling equivalents, including checkout disambiguation.

**Phases completed:** 15-19 (10 plans total)

**Key accomplishments:**

- Added 6 direct pass-through commands (show, blame, rm, mv, clone, grep) with flag filtering
- Implemented 3 flag translation commands (clean, config, switch) with safety validation
- Created branch/bookmark management with critical -D to -d safety translation
- Built stash/shelve operations with subcommand dispatch for full workflow support
- Implemented checkout disambiguation to correctly handle branches, files, and commits

**Stats:**

- 59 files created/modified
- 4,282 lines of Python
- 191 tests passing
- 5 phases, 10 plans, 47 commits
- 2 days from start to ship

**Git range:** `feat(15-01)` → `docs(19-02)`

**What's next:** User feedback and usage-driven improvements

---

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
