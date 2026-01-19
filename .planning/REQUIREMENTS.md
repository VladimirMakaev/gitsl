# Requirements: GitSL v1.2

**Defined:** 2026-01-19
**Core Value:** Git commands execute correctly against Sapling repos without the calling tool knowing the difference

## v1.2 Requirements

Requirements for v1.2 More Commands Support. Each maps to roadmap phases.

### Direct Mappings

- [x] **SHOW-01**: `git show` translates to `sl show` with pass-through flags
- [x] **SHOW-02**: `git show <commit>` shows specified commit
- [x] **BLAME-01**: `git blame <file>` translates to `sl annotate <file>`
- [x] **BLAME-02**: `git blame` passes through common flags (-L, -w)
- [x] **RM-01**: `git rm <files>` translates to `sl remove <files>`
- [x] **RM-02**: `git rm -f` translates to `sl remove -f`
- [x] **RM-03**: `git rm -r` translates to `sl remove` (recursive by default)
- [x] **MV-01**: `git mv <src> <dst>` translates to `sl rename <src> <dst>`
- [x] **MV-02**: `git mv -f` translates to `sl rename -f`
- [ ] **CLEAN-01**: `git clean -f` translates to `sl purge`
- [ ] **CLEAN-02**: `git clean -fd` translates to `sl purge` (dirs included by default)
- [ ] **CLEAN-03**: `git clean -n` translates to `sl purge --print` (dry run)
- [x] **CLONE-01**: `git clone <url>` translates to `sl clone <url>`
- [x] **CLONE-02**: `git clone <url> <dir>` translates to `sl clone <url> <dir>`
- [x] **GREP-01**: `git grep <pattern>` translates to `sl grep <pattern>`
- [x] **GREP-02**: `git grep` passes through common flags (-n, -i, -l)
- [ ] **CONFIG-01**: `git config <key>` translates to `sl config <key>`
- [ ] **CONFIG-02**: `git config <key> <value>` translates to `sl config <key> <value>`
- [ ] **CONFIG-03**: `git config --list` translates to `sl config`

### Stash/Shelve

- [ ] **STASH-01**: `git stash` translates to `sl shelve`
- [ ] **STASH-02**: `git stash push` translates to `sl shelve`
- [ ] **STASH-03**: `git stash -m "msg"` translates to `sl shelve -m "msg"`
- [ ] **STASH-04**: `git stash pop` translates to `sl unshelve`
- [ ] **STASH-05**: `git stash apply` translates to `sl unshelve --keep`
- [ ] **STASH-06**: `git stash list` translates to `sl shelve --list`
- [ ] **STASH-07**: `git stash drop` translates to `sl shelve --delete`

### Checkout/Switch/Restore

- [ ] **CHECKOUT-01**: `git checkout <commit>` translates to `sl goto <commit>`
- [ ] **CHECKOUT-02**: `git checkout <branch>` translates to `sl goto <bookmark>`
- [ ] **CHECKOUT-03**: `git checkout <file>` translates to `sl revert <file>`
- [ ] **CHECKOUT-04**: `git checkout -- <file>` translates to `sl revert <file>`
- [ ] **CHECKOUT-05**: `git checkout -b <name>` creates bookmark and switches to it
- [ ] **CHECKOUT-06**: Checkout disambiguates between commit/branch/file correctly
- [ ] **SWITCH-01**: `git switch <branch>` translates to `sl goto <bookmark>`
- [ ] **SWITCH-02**: `git switch -c <name>` translates to `sl bookmark <name>`
- [ ] **RESTORE-01**: `git restore <file>` translates to `sl revert <file>`
- [ ] **RESTORE-02**: `git restore .` translates to `sl revert --all`

### Branch/Bookmark

- [ ] **BRANCH-01**: `git branch` lists bookmarks via `sl bookmark`
- [ ] **BRANCH-02**: `git branch <name>` creates bookmark via `sl bookmark <name>`
- [ ] **BRANCH-03**: `git branch -d <name>` deletes bookmark via `sl bookmark -d <name>`
- [ ] **BRANCH-04**: `git branch -D <name>` force deletes via `sl bookmark -d <name>`

## v2 Requirements

Deferred to future release. Tracked but not in current roadmap.

### Output Format Transformation

- **BLAME-FMT**: Transform blame output to match git format exactly
- **BRANCH-FMT**: Transform branch list output to match git format
- **STASH-FMT**: Transform stash list output to match git format

### Advanced Stash

- **STASH-REF**: Support `stash@{n}` syntax for referencing older stashes
- **STASH-PARTIAL**: Support `git stash -p` for partial stashing

### Advanced Checkout

- **CHECKOUT-DETACH**: Support `git checkout --detach`
- **CHECKOUT-TRACK**: Support `git checkout --track`

## Out of Scope

Explicitly excluded. Documented to prevent scope creep.

| Feature | Reason |
|---------|--------|
| `git revert` | Maps to `sl backout`, not `sl revert` - semantic confusion risk |
| `git merge` | Sapling prefers rebase workflow |
| `git rebase` | Complex flag translation, use sl rebase directly |
| `git push/pull/fetch` | Remote model differs fundamentally |
| `git stash -p` | Interactive, requires terminal control |
| `stash@{n}` syntax | Sapling uses named shelves, different model |
| `--staged` flag | No staging area in Sapling |

## Traceability

Phase mappings for v1.2 requirements.

| Requirement | Phase | Status |
|-------------|-------|--------|
| SHOW-01 | Phase 15 | Complete |
| SHOW-02 | Phase 15 | Complete |
| BLAME-01 | Phase 15 | Complete |
| BLAME-02 | Phase 15 | Complete |
| RM-01 | Phase 15 | Complete |
| RM-02 | Phase 15 | Complete |
| RM-03 | Phase 15 | Complete |
| MV-01 | Phase 15 | Complete |
| MV-02 | Phase 15 | Complete |
| CLONE-01 | Phase 15 | Complete |
| CLONE-02 | Phase 15 | Complete |
| GREP-01 | Phase 15 | Complete |
| GREP-02 | Phase 15 | Complete |
| CLEAN-01 | Phase 16 | Pending |
| CLEAN-02 | Phase 16 | Pending |
| CLEAN-03 | Phase 16 | Pending |
| CONFIG-01 | Phase 16 | Pending |
| CONFIG-02 | Phase 16 | Pending |
| CONFIG-03 | Phase 16 | Pending |
| SWITCH-01 | Phase 16 | Pending |
| SWITCH-02 | Phase 16 | Pending |
| BRANCH-01 | Phase 17 | Pending |
| BRANCH-02 | Phase 17 | Pending |
| BRANCH-03 | Phase 17 | Pending |
| BRANCH-04 | Phase 17 | Pending |
| RESTORE-01 | Phase 17 | Pending |
| RESTORE-02 | Phase 17 | Pending |
| STASH-01 | Phase 18 | Pending |
| STASH-02 | Phase 18 | Pending |
| STASH-03 | Phase 18 | Pending |
| STASH-04 | Phase 18 | Pending |
| STASH-05 | Phase 18 | Pending |
| STASH-06 | Phase 18 | Pending |
| STASH-07 | Phase 18 | Pending |
| CHECKOUT-01 | Phase 19 | Pending |
| CHECKOUT-02 | Phase 19 | Pending |
| CHECKOUT-03 | Phase 19 | Pending |
| CHECKOUT-04 | Phase 19 | Pending |
| CHECKOUT-05 | Phase 19 | Pending |
| CHECKOUT-06 | Phase 19 | Pending |

**Coverage:**
- v1.2 requirements: 40 total
- Mapped to phases: 40
- Unmapped: 0

---
*Requirements defined: 2026-01-19*
*Last updated: 2026-01-19 after roadmap creation*
