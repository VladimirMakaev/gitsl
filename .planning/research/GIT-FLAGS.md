# Git Command Flags (Official Documentation)

**Researched:** 2026-01-20
**Source:** git-scm.com official documentation
**Confidence:** HIGH

## Summary

| Metric | Value |
|--------|-------|
| Total commands documented | 20 |
| Total unique flags (estimated) | 400+ |
| Commands with most flags | git log (~150+), git diff (~100+), git show (~100+) |
| Commands with fewest flags | git mv (4), git init (8), git clean (8) |

### Flag Categories Across Commands

1. **Output Format** - Control how results are displayed (--porcelain, --short, --oneline)
2. **Verbosity** - Control messaging (-q/--quiet, -v/--verbose, --progress)
3. **Diff Options** - Shared across many commands (--stat, --patch, -U, whitespace handling)
4. **Pathspec** - File selection (--pathspec-from-file, --pathspec-file-nul)
5. **Color** - Terminal coloring (--color, --no-color)
6. **Dry-run** - Preview without action (-n/--dry-run)

---

## Per-Command Flags

---

### git status

**Total flags:** ~20
**Documentation:** https://git-scm.com/docs/git-status

#### Output Format

| Flag | Description | Usage |
|------|-------------|-------|
| `-s`, `--short` | Short format output | Common |
| `--long` | Long format output (default) | Common |
| `--porcelain[=<version>]` | Machine-readable output (v1 or v2) | Common |
| `-v`, `--verbose` | Show textual changes staged; -vv for unstaged too | Common |
| `-z` | NUL-terminate entries; implies --porcelain=v1 | Common |

#### Branch Info

| Flag | Description | Usage |
|------|-------------|-------|
| `-b`, `--branch` | Show branch and tracking info in short-format | Common |
| `--show-stash` | Show number of stash entries | Rare |
| `--ahead-behind` | Display detailed ahead/behind counts (default) | Common |
| `--no-ahead-behind` | Do not display ahead/behind counts | Rare |

#### File Display

| Flag | Description | Usage |
|------|-------------|-------|
| `-u[<mode>]`, `--untracked-files[=<mode>]` | Show untracked files (no/normal/all) | Common |
| `--ignore-submodules[=<when>]` | Ignore submodule changes (none/untracked/dirty/all) | Rare |
| `--ignored[=<mode>]` | Show ignored files (traditional/no/matching) | Rare |

#### Column/Rename

| Flag | Description | Usage |
|------|-------------|-------|
| `--column[=<options>]` | Display untracked files in columns | Rare |
| `--no-column` | Do not display in columns | Rare |
| `--renames` | Turn on rename detection | Rare |
| `--no-renames` | Turn off rename detection | Rare |
| `--find-renames[=<n>]` | Rename detection with similarity threshold | Rare |

---

### git add

**Total flags:** ~20
**Documentation:** https://git-scm.com/docs/git-add

#### Core Operations

| Flag | Description | Usage |
|------|-------------|-------|
| `-A`, `--all` | Add all changes (new, modified, deleted) | Common |
| `-u`, `--update` | Update only already-tracked files | Common |
| `-p`, `--patch` | Interactively choose hunks to stage | Common |
| `-i`, `--interactive` | Interactive mode for staging | Rare |
| `-e`, `--edit` | Open diff in editor for manual editing | Rare |

#### Safety/Preview

| Flag | Description | Usage |
|------|-------------|-------|
| `-n`, `--dry-run` | Show what would be added without adding | Common |
| `-v`, `--verbose` | Be verbose | Common |
| `-f`, `--force` | Allow adding ignored files | Rare |

#### Intent-to-add

| Flag | Description | Usage |
|------|-------------|-------|
| `-N`, `--intent-to-add` | Record path will be added later | Rare |
| `--refresh` | Refresh stat info without adding | Rare |

#### Ignore Handling

| Flag | Description | Usage |
|------|-------------|-------|
| `--ignore-errors` | Continue on errors | Rare |
| `--ignore-missing` | Check if files would be ignored (with --dry-run) | Exotic |
| `--no-all`, `--ignore-removal` | Add new/modified but ignore deleted | Rare |

#### Special

| Flag | Description | Usage |
|------|-------------|-------|
| `--sparse` | Update index entries outside sparse-checkout cone | Exotic |
| `--no-warn-embedded-repo` | Suppress embedded repo warning | Exotic |
| `--renormalize` | Re-apply clean filter to all tracked files | Rare |
| `--chmod=(+\|-)x` | Override executable bit | Rare |

#### Context (for patch mode)

| Flag | Description | Usage |
|------|-------------|-------|
| `-U<n>`, `--unified=<n>` | Lines of context in diff | Rare |
| `--inter-hunk-context=<n>` | Context between hunks | Exotic |

#### Pathspec

| Flag | Description | Usage |
|------|-------------|-------|
| `--pathspec-from-file=<file>` | Read pathspec from file | Rare |
| `--pathspec-file-nul` | NUL-separate pathspec elements | Rare |

---

### git commit

**Total flags:** ~45
**Documentation:** https://git-scm.com/docs/git-commit

#### Staging

| Flag | Description | Usage |
|------|-------------|-------|
| `-a`, `--all` | Auto-stage modified and deleted files | Common |
| `-p`, `--patch` | Interactive patch selection | Rare |
| `-i`, `--include` | Stage paths before committing | Rare |
| `-o`, `--only` | Commit only specified paths | Rare |

#### Message

| Flag | Description | Usage |
|------|-------------|-------|
| `-m`, `--message=<msg>` | Use given commit message | Common |
| `-F`, `--file=<file>` | Read message from file | Common |
| `-t`, `--template=<file>` | Use template for message | Rare |
| `-e`, `--edit` | Edit message in editor | Common |
| `--no-edit` | Use message without editing | Common |
| `-C`, `--reuse-message=<commit>` | Reuse message and authorship | Common |
| `-c`, `--reedit-message=<commit>` | Like -C but open editor | Rare |
| `--cleanup=<mode>` | Message cleanup mode (strip/whitespace/verbatim/scissors/default) | Rare |

#### Amend/Fixup

| Flag | Description | Usage |
|------|-------------|-------|
| `--amend` | Replace tip of current branch | Common |
| `--fixup=[amend\|reword:]<commit>` | Create fixup commit for rebase | Rare |
| `--squash=<commit>` | Create squash commit for rebase | Rare |

#### Author/Date

| Flag | Description | Usage |
|------|-------------|-------|
| `--author=<author>` | Override commit author | Rare |
| `--date=<date>` | Override author date | Rare |
| `--reset-author` | Reset authorship to committer | Rare |

#### Signature

| Flag | Description | Usage |
|------|-------------|-------|
| `-S[<keyid>]`, `--gpg-sign[=<keyid>]` | GPG-sign commit | Common |
| `--no-gpg-sign` | Do not GPG-sign | Common |

#### Trailers

| Flag | Description | Usage |
|------|-------------|-------|
| `-s`, `--signoff` | Add Signed-off-by trailer | Common |
| `--no-signoff` | Remove signoff | Rare |
| `--trailer <token>[=\|:<value>]` | Add trailer to message | Rare |

#### Empty Commits

| Flag | Description | Usage |
|------|-------------|-------|
| `--allow-empty` | Allow commit with same tree as parent | Rare |
| `--allow-empty-message` | Allow empty commit message | Rare |

#### Display

| Flag | Description | Usage |
|------|-------------|-------|
| `-v`, `--verbose` | Show diff in message template | Common |
| `-q`, `--quiet` | Suppress commit summary | Common |
| `--status` | Include status in message template | Common |
| `--no-status` | Exclude status from template | Common |
| `--short` | Short-format for dry-run | Rare |
| `--porcelain` | Porcelain format for dry-run | Rare |
| `--long` | Long-format for dry-run | Rare |
| `--branch` | Show branch info in short-format | Rare |

#### Hooks

| Flag | Description | Usage |
|------|-------------|-------|
| `-n`, `--no-verify` | Bypass pre-commit and commit-msg hooks | Common |
| `--no-post-rewrite` | Bypass post-rewrite hook | Exotic |

#### Other

| Flag | Description | Usage |
|------|-------------|-------|
| `--dry-run` | Show what would be committed | Common |
| `-u[<mode>]`, `--untracked-files[=<mode>]` | Show untracked files (no/normal/all) | Rare |
| `-z`, `--null` | NUL-terminate entries in status | Rare |
| `-U<n>`, `--unified=<n>` | Context lines in verbose diff | Rare |
| `--inter-hunk-context=<n>` | Context between hunks | Exotic |
| `--pathspec-from-file=<file>` | Read pathspec from file | Rare |
| `--pathspec-file-nul` | NUL-separate pathspec | Rare |

---

### git log

**Total flags:** ~150+
**Documentation:** https://git-scm.com/docs/git-log

#### Commit Limiting

| Flag | Description | Usage |
|------|-------------|-------|
| `-<number>`, `-n <number>`, `--max-count=<number>` | Limit output count | Common |
| `--skip=<number>` | Skip commits | Rare |
| `--since=<date>`, `--after=<date>` | Commits after date | Common |
| `--until=<date>`, `--before=<date>` | Commits before date | Common |
| `--author=<pattern>` | Filter by author | Common |
| `--committer=<pattern>` | Filter by committer | Rare |
| `--grep=<pattern>` | Filter by message | Common |
| `--all-match` | Match all grep patterns | Rare |
| `--invert-grep` | Invert grep matching | Rare |
| `-i`, `--regexp-ignore-case` | Case-insensitive matching | Rare |
| `-E`, `--extended-regexp` | Extended regex | Rare |
| `-F`, `--fixed-strings` | Fixed string match | Rare |
| `-P`, `--perl-regexp` | Perl regex | Rare |
| `--basic-regexp` | Basic regex (default) | Rare |
| `--grep-reflog=<pattern>` | Filter reflog entries | Exotic |

#### Merge Handling

| Flag | Description | Usage |
|------|-------------|-------|
| `--merges` | Show only merge commits | Rare |
| `--no-merges` | Exclude merge commits | Common |
| `--min-parents=<number>` | Minimum parent count | Exotic |
| `--max-parents=<number>` | Maximum parent count | Exotic |
| `--first-parent` | Follow only first parent | Common |

#### Ref Selection

| Flag | Description | Usage |
|------|-------------|-------|
| `--all` | Include all refs | Common |
| `--branches[=<pattern>]` | Include branches | Common |
| `--tags[=<pattern>]` | Include tags | Common |
| `--remotes[=<pattern>]` | Include remotes | Common |
| `--glob=<pattern>` | Include refs matching glob | Rare |
| `--exclude=<pattern>` | Exclude refs matching pattern | Rare |
| `--reflog` | Include reflog objects | Rare |
| `--not` | Reverse ^ prefix meaning | Rare |
| `--stdin` | Read args from stdin | Exotic |

#### Walk Options

| Flag | Description | Usage |
|------|-------------|-------|
| `-g`, `--walk-reflogs` | Walk reflog instead of ancestry | Rare |
| `--no-walk[=<sorted\|unsorted>]` | Show only given commits | Rare |
| `--do-walk` | Override --no-walk | Exotic |
| `--boundary` | Output boundary commits | Exotic |
| `--merge` | Show commits touching conflicts | Rare |

#### Ordering

| Flag | Description | Usage |
|------|-------------|-------|
| `--date-order` | Commit timestamp order | Rare |
| `--author-date-order` | Author timestamp order | Rare |
| `--topo-order` | Topological order | Rare |
| `--reverse` | Reverse output order | Common |

#### Formatting

| Flag | Description | Usage |
|------|-------------|-------|
| `--pretty[=<format>]`, `--format=<format>` | Output format | Common |
| `--oneline` | Short one-line format | Common |
| `--abbrev-commit` | Abbreviated commit hash | Common |
| `--no-abbrev-commit` | Full commit hash | Rare |
| `--encoding=<encoding>` | Re-encode message | Exotic |
| `--expand-tabs[=<n>]` | Tab expansion | Exotic |
| `--no-expand-tabs` | Disable tab expansion | Exotic |
| `--notes[=<ref>]` | Show notes | Rare |
| `--no-notes` | Hide notes | Rare |
| `--show-signature` | Show GPG signature | Rare |

#### Date Formatting

| Flag | Description | Usage |
|------|-------------|-------|
| `--relative-date` | Relative dates | Common |
| `--date=<format>` | Date format (relative/local/iso/rfc/short/raw/human/unix/format:) | Common |

#### Graph/Decoration

| Flag | Description | Usage |
|------|-------------|-------|
| `--graph` | ASCII graph | Common |
| `--decorate[=<short\|full\|auto\|no>]` | Show ref names | Common |
| `--no-decorate` | Hide ref names | Rare |
| `--decorate-refs=<pattern>` | Filter decorations | Rare |
| `--decorate-refs-exclude=<pattern>` | Exclude decorations | Rare |
| `--source` | Show source ref | Rare |

#### Ancestry Display

| Flag | Description | Usage |
|------|-------------|-------|
| `--parents` | Show parent commits | Rare |
| `--children` | Show child commits | Rare |
| `--left-right` | Mark left/right side | Rare |
| `--cherry-mark` | Mark equivalent commits | Rare |
| `--cherry-pick` | Omit equivalent commits | Rare |
| `--cherry` | Shorthand for cherry options | Rare |

#### History Simplification

| Flag | Description | Usage |
|------|-------------|-------|
| `--follow` | Follow file renames | Common |
| `--full-history` | Do not prune history | Rare |
| `--dense` | Selected commits plus history | Rare |
| `--sparse` | All simplified commits | Rare |
| `--simplify-by-decoration` | Branch/tag commits only | Rare |
| `--simplify-merges` | Remove needless merges | Exotic |
| `--ancestry-path[=<commit>]` | Ancestor/descendant commits | Rare |
| `--show-pulls` | Include merge commits that pulled changes | Rare |

#### Diff Output

| Flag | Description | Usage |
|------|-------------|-------|
| `-p`, `-u`, `--patch` | Show patches | Common |
| `-s`, `--no-patch` | Suppress diff | Common |
| `--stat[=<width>[,<name-width>[,<count>]]]` | Diffstat | Common |
| `--shortstat` | Summary stat only | Rare |
| `--numstat` | Machine-readable stat | Rare |
| `--name-only` | Changed file names only | Common |
| `--name-status` | Names with status | Common |
| `--raw` | Raw diff format | Rare |
| `--compact-summary` | Condensed summary | Rare |
| `--summary` | Extended header info | Rare |
| `-z` | NUL-separate commits | Rare |

#### Merge Diff

| Flag | Description | Usage |
|------|-------------|-------|
| `-m` | Default diff for merges | Rare |
| `-c` | Combined diff for merges | Rare |
| `--cc` | Dense combined diff | Rare |
| `--dd` | Diff vs first parent | Rare |
| `--remerge-diff` | Remerge-diff for merges | Rare |
| `--no-diff-merges` | No diff for merges | Rare |
| `--diff-merges=<format>` | Merge diff format | Rare |
| `--combined-all-paths` | All parent paths in combined | Exotic |

#### Diff Algorithm

| Flag | Description | Usage |
|------|-------------|-------|
| `--diff-algorithm=<algo>` | Algorithm (patience/minimal/histogram/myers) | Rare |
| `--patience` | Patience algorithm | Rare |
| `--histogram` | Histogram algorithm | Rare |
| `--minimal` | Minimal diff | Rare |
| `--anchored=<text>` | Anchored diff | Exotic |
| `--indent-heuristic` | Shift boundaries (default) | Rare |
| `--no-indent-heuristic` | Disable indent heuristic | Exotic |

#### Context

| Flag | Description | Usage |
|------|-------------|-------|
| `-U<n>`, `--unified=<n>` | Context lines | Common |
| `--inter-hunk-context=<n>` | Context between hunks | Rare |
| `-W`, `--function-context` | Whole function context | Rare |

#### Color

| Flag | Description | Usage |
|------|-------------|-------|
| `--color[=<when>]` | Color output (always/never/auto) | Common |
| `--no-color` | Disable color | Common |
| `--color-moved[=<mode>]` | Color moved lines | Rare |
| `--no-color-moved` | Disable move coloring | Rare |
| `--color-moved-ws=<mode>` | Whitespace in move detection | Exotic |
| `--word-diff[=<mode>]` | Word-level diff | Rare |
| `--word-diff-regex=<regex>` | Word boundary regex | Exotic |
| `--color-words[=<regex>]` | Colored word diff | Rare |

#### Rename/Copy Detection

| Flag | Description | Usage |
|------|-------------|-------|
| `-M[<n>]`, `--find-renames[=<n>]` | Detect renames | Common |
| `-C[<n>]`, `--find-copies[=<n>]` | Detect copies | Rare |
| `--find-copies-harder` | Expensive copy detection | Rare |
| `--no-renames` | Disable rename detection | Rare |
| `-D`, `--irreversible-delete` | Omit delete preimage | Exotic |
| `-l<num>` | Rename detection limit | Exotic |
| `-B[<n>][/<m>]`, `--break-rewrites` | Break complete rewrites | Exotic |

#### Filtering

| Flag | Description | Usage |
|------|-------------|-------|
| `--diff-filter=<filter>` | Filter by status (ACDMRTUXB) | Rare |
| `-S<string>` | Pickaxe: find string changes | Rare |
| `-G<regex>` | Pickaxe: find regex in diff | Rare |
| `--find-object=<id>` | Find object changes | Exotic |
| `--pickaxe-all` | Show all when pickaxe matches | Exotic |
| `--pickaxe-regex` | Treat -S as regex | Exotic |

#### Whitespace

| Flag | Description | Usage |
|------|-------------|-------|
| `-a`, `--text` | Treat as text | Rare |
| `-b`, `--ignore-space-change` | Ignore whitespace amount | Rare |
| `-w`, `--ignore-all-space` | Ignore all whitespace | Rare |
| `--ignore-space-at-eol` | Ignore EOL whitespace | Rare |
| `--ignore-cr-at-eol` | Ignore CR at EOL | Rare |
| `--ignore-blank-lines` | Ignore blank line changes | Rare |
| `-I<regex>`, `--ignore-matching-lines=<regex>` | Ignore matching lines | Rare |

#### Binary/External

| Flag | Description | Usage |
|------|-------------|-------|
| `--binary` | Output binary diff | Rare |
| `--full-index` | Full blob names | Rare |
| `--abbrev[=<n>]` | Abbreviation length | Rare |
| `--ext-diff` | Allow external diff | Rare |
| `--no-ext-diff` | Disable external diff | Rare |
| `--textconv` | Allow text conversion | Rare |
| `--no-textconv` | Disable text conversion | Rare |

#### Submodule

| Flag | Description | Usage |
|------|-------------|-------|
| `--submodule[=<format>]` | Submodule diff format (short/log/diff) | Rare |
| `--ignore-submodules[=<when>]` | Ignore submodule changes | Rare |

#### Output

| Flag | Description | Usage |
|------|-------------|-------|
| `--output=<file>` | Output to file | Rare |
| `--relative[=<path>]` | Relative paths | Rare |
| `--no-relative` | Absolute paths | Rare |
| `--src-prefix=<prefix>` | Source prefix | Exotic |
| `--dst-prefix=<prefix>` | Destination prefix | Exotic |
| `--no-prefix` | No prefix | Rare |
| `--line-prefix=<prefix>` | Line prefix | Exotic |
| `-O<orderfile>` | File order | Exotic |
| `-R` | Reverse diff direction | Rare |

#### Line Range

| Flag | Description | Usage |
|------|-------------|-------|
| `-L <start>,<end>:<file>` | Line range history | Rare |
| `-L :<funcname>:<file>` | Function history | Rare |

#### Mailmap

| Flag | Description | Usage |
|------|-------------|-------|
| `--mailmap`, `--use-mailmap` | Use mailmap | Rare |
| `--no-mailmap` | Ignore mailmap | Rare |

---

### git diff

**Total flags:** ~100+
**Documentation:** https://git-scm.com/docs/git-diff

#### Comparison Mode

| Flag | Description | Usage |
|------|-------------|-------|
| `--cached`, `--staged` | Compare staged vs HEAD | Common |
| `--merge-base` | Use merge base for comparison | Rare |
| `-1`, `--base` | Compare with stage #1 (base) | Rare |
| `-2`, `--ours` | Compare with stage #2 (ours) | Rare |
| `-3`, `--theirs` | Compare with stage #3 (theirs) | Rare |
| `-0` | Omit unmerged entries | Rare |

#### Patch Generation

| Flag | Description | Usage |
|------|-------------|-------|
| `-p`, `-u`, `--patch` | Generate patch (default) | Common |
| `-s`, `--no-patch` | Suppress diff output | Common |
| `--raw` | Raw format | Rare |
| `--patch-with-raw` | Patch and raw | Rare |
| `--patch-with-stat` | Patch and stat | Rare |

#### Statistics

| Flag | Description | Usage |
|------|-------------|-------|
| `--stat[=<width>[,<name-width>[,<count>]]]` | Diffstat | Common |
| `--shortstat` | Summary only | Rare |
| `--numstat` | Machine-readable stat | Rare |
| `--compact-summary` | Condensed summary | Rare |
| `--summary` | Extended header info | Rare |
| `--name-only` | File names only | Common |
| `--name-status` | Names with status | Common |
| `-X[<param>,...]`, `--dirstat[=<param>,...]` | Directory statistics | Rare |

#### Context

| Flag | Description | Usage |
|------|-------------|-------|
| `-U<n>`, `--unified=<n>` | Context lines (default: 3) | Common |
| `--inter-hunk-context=<n>` | Context between hunks | Rare |
| `-W`, `--function-context` | Whole function context | Rare |

#### Algorithm

| Flag | Description | Usage |
|------|-------------|-------|
| `--minimal` | Minimal diff | Rare |
| `--patience` | Patience algorithm | Rare |
| `--histogram` | Histogram algorithm | Rare |
| `--anchored=<text>` | Anchored diff | Exotic |
| `--diff-algorithm=<algo>` | Choose algorithm | Rare |
| `--indent-heuristic` | Shift boundaries (default) | Rare |
| `--no-indent-heuristic` | Disable heuristic | Exotic |

#### Color

| Flag | Description | Usage |
|------|-------------|-------|
| `--color[=<when>]` | Color output | Common |
| `--no-color` | Disable color | Common |
| `--color-moved[=<mode>]` | Color moved lines | Rare |
| `--no-color-moved` | Disable move coloring | Rare |
| `--color-moved-ws=<mode>` | Whitespace in move detection | Exotic |
| `--word-diff[=<mode>]` | Word-level diff | Rare |
| `--word-diff-regex=<regex>` | Word boundary regex | Exotic |
| `--color-words[=<regex>]` | Colored word diff | Rare |

#### Whitespace

| Flag | Description | Usage |
|------|-------------|-------|
| `-b`, `--ignore-space-change` | Ignore whitespace amount | Common |
| `-w`, `--ignore-all-space` | Ignore all whitespace | Common |
| `--ignore-space-at-eol` | Ignore EOL whitespace | Rare |
| `--ignore-cr-at-eol` | Ignore CR at EOL | Rare |
| `--ignore-blank-lines` | Ignore blank lines | Rare |
| `-I<regex>`, `--ignore-matching-lines=<regex>` | Ignore matching lines | Rare |
| `--ws-error-highlight=<kind>` | Highlight whitespace errors | Rare |

#### Rename/Copy

| Flag | Description | Usage |
|------|-------------|-------|
| `-M[<n>]`, `--find-renames[=<n>]` | Detect renames | Common |
| `-C[<n>]`, `--find-copies[=<n>]` | Detect copies | Rare |
| `--find-copies-harder` | Expensive copy detection | Rare |
| `--no-renames` | Disable rename detection | Rare |
| `-D`, `--irreversible-delete` | Omit delete preimage | Exotic |
| `-l<num>` | Rename detection limit | Exotic |
| `-B[<n>][/<m>]`, `--break-rewrites` | Break complete rewrites | Exotic |
| `--rename-empty` | Use empty blobs as source | Exotic |
| `--no-rename-empty` | Don't use empty blobs | Exotic |

#### Filtering

| Flag | Description | Usage |
|------|-------------|-------|
| `--diff-filter=<filter>` | Filter by status | Rare |
| `-S<string>` | Pickaxe: string changes | Rare |
| `-G<regex>` | Pickaxe: regex in diff | Rare |
| `--find-object=<id>` | Find object changes | Exotic |
| `--pickaxe-all` | Show all on match | Exotic |
| `--pickaxe-regex` | Treat -S as regex | Exotic |

#### Output

| Flag | Description | Usage |
|------|-------------|-------|
| `--output=<file>` | Output to file | Rare |
| `-z` | NUL-terminate output | Rare |
| `-R` | Reverse diff direction | Rare |
| `--relative[=<path>]` | Relative paths | Rare |
| `--no-relative` | Absolute paths | Rare |
| `--src-prefix=<prefix>` | Source prefix | Rare |
| `--dst-prefix=<prefix>` | Destination prefix | Rare |
| `--no-prefix` | No prefix | Common |
| `--default-prefix` | Default prefixes | Rare |
| `--mnemonic-prefix` | Mnemonic prefixes | Exotic |
| `--line-prefix=<prefix>` | Line prefix | Exotic |
| `-O<orderfile>` | File order | Exotic |
| `--skip-to=<file>` | Skip to file | Exotic |
| `--rotate-to=<file>` | Rotate to file | Exotic |
| `--output-indicator-new=<char>` | New line character | Exotic |
| `--output-indicator-old=<char>` | Old line character | Exotic |
| `--output-indicator-context=<char>` | Context character | Exotic |

#### Binary/External

| Flag | Description | Usage |
|------|-------------|-------|
| `-a`, `--text` | Treat as text | Rare |
| `--binary` | Output binary diff | Rare |
| `--full-index` | Full blob names | Rare |
| `--abbrev[=<n>]` | Abbreviation length | Rare |
| `--ext-diff` | Allow external diff | Rare |
| `--no-ext-diff` | Disable external diff | Rare |
| `--textconv` | Allow text conversion | Rare |
| `--no-textconv` | Disable text conversion | Rare |

#### Submodule

| Flag | Description | Usage |
|------|-------------|-------|
| `--submodule[=<format>]` | Submodule format | Rare |
| `--ignore-submodules[=<when>]` | Ignore submodules | Rare |

#### Intent-to-add

| Flag | Description | Usage |
|------|-------------|-------|
| `--ita-invisible-in-index` | ITA entries as new | Rare |
| `--ita-visible-in-index` | Revert ITA visibility | Exotic |

#### Other

| Flag | Description | Usage |
|------|-------------|-------|
| `--check` | Warn about whitespace/conflicts | Rare |
| `--exit-code` | Exit 1 if differences | Common |
| `--quiet` | Disable output (implies --exit-code) | Rare |
| `--max-depth=<depth>` | Directory depth limit | Exotic |

---

### git init

**Total flags:** 8
**Documentation:** https://git-scm.com/docs/git-init

| Flag | Description | Usage |
|------|-------------|-------|
| `-q`, `--quiet` | Only print errors and warnings | Common |
| `--bare` | Create bare repository | Common |
| `--template=<template-directory>` | Template directory | Rare |
| `--separate-git-dir=<git-dir>` | Separate git directory | Rare |
| `--object-format=<format>` | Hash algorithm (sha1/sha256) | Exotic |
| `--ref-format=<format>` | Ref storage (files/reftable) | Exotic |
| `-b`, `--initial-branch=<branch-name>` | Initial branch name | Common |
| `--shared[=<permissions>]` | Shared repository | Rare |

---

### git rev-parse

**Total flags:** ~40
**Documentation:** https://git-scm.com/docs/git-rev-parse

#### Mode

| Flag | Description | Usage |
|------|-------------|-------|
| `--parseopt` | Option parsing mode | Exotic |
| `--sq-quote` | Shell quoting mode | Rare |

#### Parseopt Options

| Flag | Description | Usage |
|------|-------------|-------|
| `--keep-dashdash` | Echo first -- | Exotic |
| `--stop-at-non-option` | Stop at first non-option | Exotic |
| `--stuck-long` | Long form with stuck args | Exotic |

#### Filtering

| Flag | Description | Usage |
|------|-------------|-------|
| `--revs-only` | Only rev-list params | Rare |
| `--no-revs` | No rev-list params | Rare |
| `--flags` | Only flag params | Rare |
| `--no-flags` | No flag params | Rare |

#### Output

| Flag | Description | Usage |
|------|-------------|-------|
| `--default <arg>` | Default if no param | Rare |
| `--prefix <arg>` | Act as if in subdirectory | Rare |
| `--verify` | Verify single SHA-1 | Common |
| `-q`, `--quiet` | Silent verify mode | Common |
| `--sq` | Shell-quoted single line | Rare |
| `--short[=<length>]` | Short object name | Common |
| `--not` | Prefix with ^ | Rare |
| `--abbrev-ref[=<mode>]` | Short ref name | Common |
| `--symbolic` | Original input form | Rare |
| `--symbolic-full-name` | Full refname | Rare |
| `--output-object-format=<fmt>` | Output hash format | Exotic |

#### Ref Selection

| Flag | Description | Usage |
|------|-------------|-------|
| `--all` | All refs | Common |
| `--branches[=<pattern>]` | All branches | Common |
| `--tags[=<pattern>]` | All tags | Common |
| `--remotes[=<pattern>]` | All remotes | Common |
| `--glob=<pattern>` | Refs matching pattern | Rare |
| `--exclude=<pattern>` | Exclude refs | Rare |
| `--disambiguate=<prefix>` | All objects with prefix | Rare |

#### Path Information

| Flag | Description | Usage |
|------|-------------|-------|
| `--local-env-vars` | List local GIT_* vars | Rare |
| `--path-format=<format>` | Absolute or relative | Rare |
| `--git-dir` | Show .git directory | Common |
| `--git-common-dir` | Show common dir | Rare |
| `--resolve-git-dir <path>` | Resolve gitfile | Rare |
| `--git-path <path>` | Resolve repo path | Rare |
| `--show-toplevel` | Working tree root | Common |
| `--show-superproject-working-tree` | Superproject root | Rare |
| `--shared-index-path` | Shared index path | Exotic |
| `--absolute-git-dir` | Absolute .git path | Common |
| `--show-cdup` | Relative to toplevel | Common |
| `--show-prefix` | Prefix from toplevel | Common |

#### State Queries

| Flag | Description | Usage |
|------|-------------|-------|
| `--is-inside-git-dir` | Inside git dir? | Common |
| `--is-inside-work-tree` | Inside work tree? | Common |
| `--is-bare-repository` | Bare repository? | Common |
| `--is-shallow-repository` | Shallow repository? | Rare |
| `--show-object-format[=<scope>]` | Object format | Rare |
| `--show-ref-format` | Ref storage format | Exotic |

#### Date Parsing

| Flag | Description | Usage |
|------|-------------|-------|
| `--since=<datestring>`, `--after=<datestring>` | Parse to --max-age | Rare |
| `--until=<datestring>`, `--before=<datestring>` | Parse to --min-age | Rare |

---

### git show

**Total flags:** ~100+
**Documentation:** https://git-scm.com/docs/git-show

*Note: git show shares most flags with git log for formatting and diff options.*

#### Object Display

| Flag | Description | Usage |
|------|-------------|-------|
| `--pretty[=<format>]`, `--format=<format>` | Output format | Common |
| `--oneline` | Short one-line format | Common |
| `--abbrev-commit` | Abbreviated hash | Common |
| `--no-abbrev-commit` | Full hash | Rare |
| `--encoding=<encoding>` | Re-encode message | Exotic |
| `--expand-tabs[=<n>]` | Tab expansion | Exotic |
| `--notes[=<ref>]` | Show notes | Rare |
| `--no-notes` | Hide notes | Rare |
| `--show-signature` | Verify signature | Rare |

#### Diff Output

| Flag | Description | Usage |
|------|-------------|-------|
| `-p`, `-u`, `--patch` | Show patch | Common |
| `-s`, `--no-patch` | Suppress diff | Common |
| `--stat[=<options>]` | Diffstat | Common |
| `--shortstat` | Summary stat | Rare |
| `--numstat` | Machine stat | Rare |
| `--name-only` | File names only | Common |
| `--name-status` | Names with status | Common |
| `--raw` | Raw format | Rare |
| `--compact-summary` | Condensed summary | Rare |
| `--summary` | Extended header | Rare |

#### Merge Diff

| Flag | Description | Usage |
|------|-------------|-------|
| `-m` | Diff for merges | Rare |
| `-c` | Combined diff | Rare |
| `--cc` | Dense combined | Common |
| `--dd` | Diff vs first parent | Rare |
| `--remerge-diff` | Remerge-diff | Rare |
| `--no-diff-merges` | No merge diff | Rare |
| `--diff-merges=<format>` | Merge diff format | Rare |
| `--combined-all-paths` | All parent paths | Exotic |

#### Context

| Flag | Description | Usage |
|------|-------------|-------|
| `-U<n>`, `--unified=<n>` | Context lines | Common |
| `--inter-hunk-context=<n>` | Context between hunks | Rare |
| `-W`, `--function-context` | Whole function | Rare |

#### Algorithm

| Flag | Description | Usage |
|------|-------------|-------|
| `--diff-algorithm=<algo>` | Choose algorithm | Rare |
| `--patience` | Patience diff | Rare |
| `--histogram` | Histogram diff | Rare |
| `--minimal` | Minimal diff | Rare |
| `--anchored=<text>` | Anchored diff | Exotic |
| `--indent-heuristic` | Shift boundaries | Rare |
| `--no-indent-heuristic` | Disable heuristic | Exotic |

#### Rename/Copy

| Flag | Description | Usage |
|------|-------------|-------|
| `-M[<n>]`, `--find-renames[=<n>]` | Detect renames | Common |
| `-C[<n>]`, `--find-copies[=<n>]` | Detect copies | Rare |
| `--find-copies-harder` | Expensive detection | Rare |
| `-D`, `--irreversible-delete` | Omit preimage | Exotic |
| `-l<num>` | Detection limit | Exotic |
| `-B[<n>][/<m>]`, `--break-rewrites` | Break rewrites | Exotic |

#### Whitespace

| Flag | Description | Usage |
|------|-------------|-------|
| `-b`, `--ignore-space-change` | Ignore amount | Rare |
| `-w`, `--ignore-all-space` | Ignore all | Rare |
| `--ignore-space-at-eol` | Ignore EOL | Rare |
| `--ignore-cr-at-eol` | Ignore CR | Rare |
| `--ignore-blank-lines` | Ignore blank | Rare |
| `-I<regex>`, `--ignore-matching-lines=<regex>` | Ignore matching | Rare |

#### Color

| Flag | Description | Usage |
|------|-------------|-------|
| `--color[=<when>]` | Color output | Common |
| `--no-color` | Disable color | Common |
| `--color-moved[=<mode>]` | Color moved | Rare |
| `--word-diff[=<mode>]` | Word diff | Rare |
| `--color-words[=<regex>]` | Colored words | Rare |

#### Filtering

| Flag | Description | Usage |
|------|-------------|-------|
| `--diff-filter=<filter>` | Filter by status | Rare |
| `-S<string>` | Pickaxe string | Rare |
| `-G<regex>` | Pickaxe regex | Rare |
| `--find-object=<id>` | Find object | Exotic |

#### Output

| Flag | Description | Usage |
|------|-------------|-------|
| `--output=<file>` | Output to file | Rare |
| `-z` | NUL-terminate | Rare |
| `-R` | Reverse diff | Rare |
| `--relative[=<path>]` | Relative paths | Rare |
| `--src-prefix=<prefix>` | Source prefix | Rare |
| `--dst-prefix=<prefix>` | Dest prefix | Rare |
| `--no-prefix` | No prefix | Rare |
| `--line-prefix=<prefix>` | Line prefix | Exotic |
| `-O<orderfile>` | File order | Exotic |

#### Binary

| Flag | Description | Usage |
|------|-------------|-------|
| `-a`, `--text` | Treat as text | Rare |
| `--binary` | Binary diff | Rare |
| `--full-index` | Full blob names | Rare |
| `--abbrev[=<n>]` | Abbreviation | Rare |

#### Tree Display

| Flag | Description | Usage |
|------|-------------|-------|
| `-t` | Show tree objects | Rare |

---

### git blame

**Total flags:** ~25
**Documentation:** https://git-scm.com/docs/git-blame

#### Output Format

| Flag | Description | Usage |
|------|-------------|-------|
| `-b`, `--blank-boundary` | Blank SHA for boundary | Rare |
| `-c` | git-annotate output mode | Rare |
| `-l` | Show long rev | Rare |
| `-t` | Show raw timestamp | Rare |
| `-f`, `--show-name` | Show filename in original | Rare |
| `-n`, `--show-number` | Show line number in original | Rare |
| `-s` | Suppress author/timestamp | Common |
| `-e`, `--show-email` | Show author email | Rare |
| `-p`, `--porcelain` | Machine-readable format | Common |
| `--line-porcelain` | Porcelain per line | Rare |
| `--incremental` | Incremental machine format | Rare |

#### Range/Revision

| Flag | Description | Usage |
|------|-------------|-------|
| `-L <start>,<end>` | Line range | Common |
| `-L :<funcname>` | Function range | Rare |
| `--root` | Don't treat root as boundary | Rare |
| `-S <revs-file>` | Use revs from file | Exotic |
| `--reverse <rev>..<rev>` | Walk forward | Rare |
| `--first-parent` | Only first parent | Rare |
| `--since=<date>` | Ignore older changes | Rare |

#### Movement Detection

| Flag | Description | Usage |
|------|-------------|-------|
| `-M[<num>]` | Detect moved lines in file | Common |
| `-C[<num>]` | Detect copied lines | Common |
| `-w` | Ignore whitespace | Common |
| `--score-debug` | Movement detection debug | Exotic |

#### Ignore

| Flag | Description | Usage |
|------|-------------|-------|
| `--ignore-rev <rev>` | Ignore specific revision | Rare |
| `--ignore-revs-file <file>` | Ignore revs from file | Rare |

#### Display

| Flag | Description | Usage |
|------|-------------|-------|
| `--show-stats` | Additional statistics | Rare |
| `--color-lines` | Color by commit | Rare |
| `--color-by-age` | Color by age | Rare |
| `--encoding=<encoding>` | Author name encoding | Exotic |
| `--date <format>` | Date format | Common |
| `--abbrev=<n>` | Abbreviation length | Rare |

#### Progress

| Flag | Description | Usage |
|------|-------------|-------|
| `--progress` | Enable progress | Rare |
| `--no-progress` | Disable progress | Rare |
| `--contents <file>` | Annotate from file | Rare |

---

### git rm

**Total flags:** 10
**Documentation:** https://git-scm.com/docs/git-rm

| Flag | Description | Usage |
|------|-------------|-------|
| `-f`, `--force` | Override up-to-date check | Common |
| `-n`, `--dry-run` | Show what would be removed | Common |
| `-r` | Recursive removal | Common |
| `-q`, `--quiet` | Suppress output | Common |
| `--cached` | Remove from index only | Common |
| `--ignore-unmatch` | Exit zero if no match | Rare |
| `--sparse` | Allow outside sparse-checkout | Exotic |
| `--pathspec-from-file=<file>` | Read paths from file | Rare |
| `--pathspec-file-nul` | NUL-separate paths | Rare |

---

### git mv

**Total flags:** 4
**Documentation:** https://git-scm.com/docs/git-mv

| Flag | Description | Usage |
|------|-------------|-------|
| `-f`, `--force` | Force rename/move | Common |
| `-k` | Skip error conditions | Rare |
| `-n`, `--dry-run` | Show what would happen | Common |
| `-v`, `--verbose` | Report files as moved | Common |

---

### git clean

**Total flags:** 8
**Documentation:** https://git-scm.com/docs/git-clean

| Flag | Description | Usage |
|------|-------------|-------|
| `-d` | Recurse into untracked directories | Common |
| `-f`, `--force` | Force deletion | Common |
| `-i`, `--interactive` | Interactive mode | Common |
| `-n`, `--dry-run` | Show what would be removed | Common |
| `-q`, `--quiet` | Only report errors | Rare |
| `-e <pattern>`, `--exclude=<pattern>` | Add exclude pattern | Common |
| `-x` | Ignore .gitignore, use only -e | Common |
| `-X` | Remove only ignored files | Common |

---

### git clone

**Total flags:** ~35
**Documentation:** https://git-scm.com/docs/git-clone

#### Local/Template

| Flag | Description | Usage |
|------|-------------|-------|
| `--template=<template-directory>` | Template directory | Rare |
| `-l`, `--local` | Local clone optimization | Rare |
| `-s`, `--shared` | Share objects with source | Rare |
| `--no-hardlinks` | Copy instead of hardlink | Rare |
| `--no-local` | Disable local optimization | Rare |

#### Reference

| Flag | Description | Usage |
|------|-------------|-------|
| `--reference[if-able] <repo>` | Reference repository | Rare |
| `--dissociate` | Disconnect from reference | Rare |

#### Output

| Flag | Description | Usage |
|------|-------------|-------|
| `-q`, `--quiet` | Quiet operation | Common |
| `-v`, `--verbose` | Verbose output | Rare |
| `--progress` | Force progress output | Rare |

#### Server

| Flag | Description | Usage |
|------|-------------|-------|
| `--server-option=<option>` | Server option (v2) | Exotic |

#### Checkout/Bare

| Flag | Description | Usage |
|------|-------------|-------|
| `-n`, `--no-checkout` | No checkout after clone | Common |
| `--bare` | Bare repository | Common |
| `--mirror` | Mirror repository | Rare |
| `--sparse` | Sparse checkout | Rare |

#### Remote/Branch

| Flag | Description | Usage |
|------|-------------|-------|
| `-o <name>`, `--origin <name>` | Remote name | Rare |
| `-b <name>`, `--branch <name>` | Branch to checkout | Common |
| `--revision=<rev>` | Specific revision | Rare |
| `-u <upload-pack>`, `--upload-pack <upload-pack>` | Upload-pack path | Exotic |

#### Configuration

| Flag | Description | Usage |
|------|-------------|-------|
| `-c <key>=<value>`, `--config <key>=<value>` | Set config | Common |

#### Shallow

| Flag | Description | Usage |
|------|-------------|-------|
| `--depth <depth>` | Shallow clone depth | Common |
| `--shallow-since=<date>` | Shallow since date | Rare |
| `--shallow-exclude=<ref>` | Exclude ref from shallow | Rare |
| `--[no-]single-branch` | Single branch only | Common |
| `--[no-]reject-shallow` | Reject shallow source | Rare |

#### Tags/Filter

| Flag | Description | Usage |
|------|-------------|-------|
| `--tags` | Clone all tags | Rare |
| `--no-tags` | Don't clone tags | Rare |
| `--filter=<filter-spec>` | Partial clone filter | Common |
| `--also-filter-submodules` | Filter submodules too | Rare |

#### Submodules

| Flag | Description | Usage |
|------|-------------|-------|
| `--recurse-submodules[=<pathspec>]` | Clone submodules | Common |
| `--[no-]shallow-submodules` | Shallow submodules | Rare |
| `--[no-]remote-submodules` | Remote submodule state | Rare |
| `-j <n>`, `--jobs <n>` | Parallel submodule fetch | Rare |

#### Directory

| Flag | Description | Usage |
|------|-------------|-------|
| `--separate-git-dir=<git-dir>` | Separate git directory | Rare |
| `--ref-format=<ref-format>` | Ref storage format | Exotic |
| `--bundle-uri=<uri>` | Bundle URI | Exotic |

---

### git grep

**Total flags:** ~45
**Documentation:** https://git-scm.com/docs/git-grep

#### Search Scope

| Flag | Description | Usage |
|------|-------------|-------|
| `--cached` | Search index blobs | Rare |
| `--untracked` | Include untracked files | Rare |
| `--no-index` | Search non-git files | Rare |
| `--no-exclude-standard` | Include ignored files | Rare |
| `--exclude-standard` | Exclude ignored | Rare |
| `--recurse-submodules` | Search submodules | Rare |

#### Pattern Matching

| Flag | Description | Usage |
|------|-------------|-------|
| `-a`, `--text` | Process binary as text | Rare |
| `--textconv` | Honor textconv | Rare |
| `--no-textconv` | Ignore textconv | Rare |
| `-i`, `--ignore-case` | Case insensitive | Common |
| `-I` | Skip binary files | Rare |
| `-w`, `--word-regexp` | Word boundary match | Common |
| `-v`, `--invert-match` | Invert match | Common |
| `-E`, `--extended-regexp` | Extended regex | Common |
| `-G`, `--basic-regexp` | Basic regex (default) | Rare |
| `-P`, `--perl-regexp` | Perl regex | Rare |
| `-F`, `--fixed-strings` | Fixed strings | Common |
| `-e` | Pattern follows | Common |
| `-f <file>` | Patterns from file | Rare |

#### Output Format

| Flag | Description | Usage |
|------|-------------|-------|
| `-h` | Suppress filename | Rare |
| `-H` | Show filename (default) | Rare |
| `--full-name` | Paths from project root | Rare |
| `-n`, `--line-number` | Show line numbers | Common |
| `--column` | Show byte offset | Rare |
| `-l`, `--files-with-matches`, `--name-only` | File names only | Common |
| `-L`, `--files-without-match` | Files without match | Rare |
| `-o`, `--only-matching` | Only matching parts | Rare |
| `-c`, `--count` | Match counts | Common |
| `--color[=<when>]` | Color output | Common |
| `--no-color` | Disable color | Rare |
| `--break` | Empty line between files | Rare |
| `--heading` | Filename above matches | Rare |

#### Context

| Flag | Description | Usage |
|------|-------------|-------|
| `-p`, `--show-function` | Show function name | Rare |
| `-<num>`, `-C <num>` | Context lines | Common |
| `-A <num>`, `--after-context <num>` | After context | Common |
| `-B <num>`, `--before-context <num>` | Before context | Common |
| `-W`, `--function-context` | Whole function | Rare |

#### Limiting

| Flag | Description | Usage |
|------|-------------|-------|
| `--max-depth <depth>` | Directory depth | Rare |
| `-r`, `--recursive` | Recursive (default) | Common |
| `--no-recursive` | Non-recursive | Rare |
| `-m <num>`, `--max-count <num>` | Max matches per file | Rare |
| `--threads <num>` | Worker threads | Exotic |
| `-O[<pager>]`, `--open-files-in-pager[=<pager>]` | Open in pager | Rare |

#### Boolean

| Flag | Description | Usage |
|------|-------------|-------|
| `--and` | AND patterns | Rare |
| `--or` | OR patterns (default) | Rare |
| `--not` | Negate pattern | Rare |
| `--all-match` | All patterns in file | Rare |

#### Other

| Flag | Description | Usage |
|------|-------------|-------|
| `-q`, `--quiet` | Exit status only | Rare |
| `-z`, `--null` | NUL-terminate paths | Rare |

---

### git config

**Total flags:** ~30
**Documentation:** https://git-scm.com/docs/git-config

#### Subcommands

| Subcommand | Description | Usage |
|------------|-------------|-------|
| `list` | List all variables | Common |
| `get` | Get value of key | Common |
| `set` | Set value | Common |
| `unset` | Remove value | Common |
| `rename-section` | Rename section | Rare |
| `remove-section` | Remove section | Rare |
| `edit` | Open editor | Common |

#### File Location

| Flag | Description | Usage |
|------|-------------|-------|
| `-f`, `--file <config-file>` | Use specific file | Common |
| `--blob <blob>` | Use blob | Exotic |
| `--system` | System-wide config | Common |
| `--global` | User config | Common |
| `--local` | Repository config (default) | Common |
| `--worktree` | Worktree config | Rare |

#### Output

| Flag | Description | Usage |
|------|-------------|-------|
| `-z`, `--null` | NUL-terminate values | Rare |
| `--name-only` | Output names only | Rare |
| `--show-names` | Show keys with values | Rare |
| `--show-origin` | Show origin of values | Rare |
| `--show-scope` | Show scope of values | Rare |

#### Query

| Flag | Description | Usage |
|------|-------------|-------|
| `--all` | All values for multi-valued | Common |
| `--regexp` | Name as regex | Rare |
| `--value=<pattern>` | Match value pattern | Rare |
| `--fixed-value` | Exact string match | Rare |
| `--url=<URL>` | Match URL config | Rare |
| `--default=<value>` | Default if not found | Rare |

#### Type

| Flag | Description | Usage |
|------|-------------|-------|
| `--type=<type>` | Canonicalize type | Common |
| `--bool` | Boolean type | Common |
| `--int` | Integer type | Common |
| `--bool-or-int` | Bool or int | Rare |
| `--path` | Path type | Rare |
| `--expiry-date` | Expiry date type | Exotic |
| `--no-type` | Unset type | Rare |

#### Modification

| Flag | Description | Usage |
|------|-------------|-------|
| `--replace-all` | Replace all matching | Rare |
| `--append` | Add new line | Rare |
| `--comment <message>` | Add comment | Rare |

#### Include

| Flag | Description | Usage |
|------|-------------|-------|
| `--includes` | Follow includes (default) | Rare |
| `--no-includes` | Ignore includes | Rare |

#### Legacy (deprecated)

| Flag | Description | Usage |
|------|-------------|-------|
| `-l`, `--list` | List (use subcommand) | Common |
| `--get` | Get (use subcommand) | Common |
| `--get-all` | Get all (use subcommand) | Rare |
| `--get-regexp` | Get by regex (use subcommand) | Rare |
| `--add` | Add (use set --append) | Rare |
| `-e`, `--edit` | Edit (use subcommand) | Common |

---

### git stash

**Total flags:** ~25 (varies by subcommand)
**Documentation:** https://git-scm.com/docs/git-stash

#### Subcommands

| Subcommand | Description | Usage |
|------------|-------------|-------|
| `push` | Save changes to stash | Common |
| `pop` | Apply and remove stash | Common |
| `apply` | Apply stash | Common |
| `list` | List stashes | Common |
| `show` | Show stash diff | Common |
| `drop` | Remove stash | Common |
| `clear` | Remove all stashes | Rare |
| `branch <name>` | Create branch from stash | Rare |
| `create` | Create stash object | Exotic |
| `store` | Store stash object | Exotic |
| `export` | Export stash | Exotic |
| `import` | Import stash | Exotic |

#### push Flags

| Flag | Description | Usage |
|------|-------------|-------|
| `-p`, `--patch` | Interactive hunk selection | Rare |
| `-S`, `--staged` | Stash only staged changes | Common |
| `-k`, `--keep-index` | Keep staged in working tree | Common |
| `--no-keep-index` | Override keep-index | Rare |
| `-u`, `--include-untracked` | Include untracked files | Common |
| `-a`, `--all` | Include ignored and untracked | Rare |
| `-q`, `--quiet` | Suppress messages | Common |
| `-m`, `--message <message>` | Stash description | Common |
| `-U<n>`, `--unified=<n>` | Context lines for patch | Rare |
| `--inter-hunk-context=<n>` | Context between hunks | Exotic |
| `--pathspec-from-file=<file>` | Read paths from file | Rare |
| `--pathspec-file-nul` | NUL-separate paths | Rare |

#### pop/apply Flags

| Flag | Description | Usage |
|------|-------------|-------|
| `--index` | Restore index state | Common |
| `-q`, `--quiet` | Suppress messages | Common |

#### show Flags

| Flag | Description | Usage |
|------|-------------|-------|
| `-u`, `--include-untracked` | Show untracked in diff | Rare |
| `--only-untracked` | Only untracked files | Rare |
| `-p` | Patch form | Common |
| *(diff options)* | Standard diff options | Various |

#### drop Flags

| Flag | Description | Usage |
|------|-------------|-------|
| `-q`, `--quiet` | Suppress messages | Common |

#### store Flags

| Flag | Description | Usage |
|------|-------------|-------|
| `-m`, `--message <message>` | Stash description | Rare |
| `-q`, `--quiet` | Suppress messages | Rare |

#### export Flags

| Flag | Description | Usage |
|------|-------------|-------|
| `--print` | Print object ID | Exotic |
| `--to-ref <ref>` | Store to ref | Exotic |

---

### git checkout

**Total flags:** ~25
**Documentation:** https://git-scm.com/docs/git-checkout

#### Branch Creation

| Flag | Description | Usage |
|------|-------------|-------|
| `-b` | Create new branch | Common |
| `-B` | Create/reset branch | Common |
| `-t`, `--track` | Set upstream tracking | Common |
| `--no-track` | No upstream tracking | Rare |
| `--guess` | Auto-create tracking (default) | Rare |
| `--no-guess` | Disable auto-tracking | Rare |
| `-l` | Create reflog | Rare |
| `--orphan` | Create orphan branch | Rare |

#### Checkout Mode

| Flag | Description | Usage |
|------|-------------|-------|
| `-d`, `--detach` | Detached HEAD | Common |
| `--ours` | Checkout stage #2 | Common |
| `--theirs` | Checkout stage #3 | Common |

#### Behavior

| Flag | Description | Usage |
|------|-------------|-------|
| `-q`, `--quiet` | Suppress messages | Common |
| `--progress` | Enable progress | Rare |
| `--no-progress` | Disable progress | Rare |
| `-f`, `--force` | Force checkout | Common |
| `-m`, `--merge` | Three-way merge | Rare |
| `--conflict=<style>` | Conflict style (merge/diff3/zdiff3) | Rare |

#### Interactive

| Flag | Description | Usage |
|------|-------------|-------|
| `-p`, `--patch` | Interactive hunk selection | Rare |
| `-U<n>`, `--unified=<n>` | Context lines | Rare |
| `--inter-hunk-context=<n>` | Context between hunks | Exotic |

#### Overlay

| Flag | Description | Usage |
|------|-------------|-------|
| `--overlay` | Never remove files (default) | Rare |
| `--no-overlay` | Remove files not in tree | Rare |

#### Worktree

| Flag | Description | Usage |
|------|-------------|-------|
| `--ignore-other-worktrees` | Allow branch in other worktree | Rare |
| `--ignore-skip-worktree-bits` | Ignore sparse patterns | Rare |
| `--overwrite-ignore` | Overwrite ignored files (default) | Rare |
| `--no-overwrite-ignore` | Abort on ignored files | Rare |
| `--recurse-submodules` | Update submodules | Rare |
| `--no-recurse-submodules` | Don't update submodules (default) | Rare |

#### Pathspec

| Flag | Description | Usage |
|------|-------------|-------|
| `--pathspec-from-file=<file>` | Read paths from file | Rare |
| `--pathspec-file-nul` | NUL-separate paths | Rare |

---

### git switch

**Total flags:** ~18
**Documentation:** https://git-scm.com/docs/git-switch

*Note: git switch is focused on branch switching, split from git checkout.*

#### Branch Creation

| Flag | Description | Usage |
|------|-------------|-------|
| `-c`, `--create <branch>` | Create new branch | Common |
| `-C`, `--force-create <branch>` | Create/reset branch | Common |
| `-t`, `--track [direct\|inherit]` | Set upstream | Common |
| `--no-track` | No upstream | Rare |
| `--orphan <branch>` | Create orphan branch | Rare |

#### Switch Mode

| Flag | Description | Usage |
|------|-------------|-------|
| `-d`, `--detach` | Detached HEAD | Common |
| `--guess` | Auto-create tracking (default) | Rare |
| `--no-guess` | Disable auto-tracking | Rare |

#### Behavior

| Flag | Description | Usage |
|------|-------------|-------|
| `-f`, `--force`, `--discard-changes` | Force switch | Common |
| `-m`, `--merge` | Three-way merge | Rare |
| `--conflict=<style>` | Conflict style | Rare |
| `-q`, `--quiet` | Suppress messages | Common |
| `--progress` | Enable progress | Rare |
| `--no-progress` | Disable progress | Rare |

#### Worktree

| Flag | Description | Usage |
|------|-------------|-------|
| `--ignore-other-worktrees` | Allow branch in other worktree | Rare |
| `--recurse-submodules` | Update submodules | Rare |
| `--no-recurse-submodules` | Don't update submodules (default) | Rare |

---

### git restore

**Total flags:** ~20
**Documentation:** https://git-scm.com/docs/git-restore

*Note: git restore is focused on file restoration, split from git checkout.*

#### Source

| Flag | Description | Usage |
|------|-------------|-------|
| `-s`, `--source=<tree>` | Restore from tree | Common |

#### Target

| Flag | Description | Usage |
|------|-------------|-------|
| `-W`, `--worktree` | Restore working tree (default) | Common |
| `-S`, `--staged` | Restore index | Common |

#### Interactive

| Flag | Description | Usage |
|------|-------------|-------|
| `-p`, `--patch` | Interactive hunk selection | Rare |
| `-U`, `--unified=<n>` | Context lines | Rare |
| `--inter-hunk-context=<n>` | Context between hunks | Exotic |

#### Unmerged

| Flag | Description | Usage |
|------|-------------|-------|
| `--ours` | Use stage #2 | Common |
| `--theirs` | Use stage #3 | Common |
| `-m`, `--merge` | Recreate merge conflict | Rare |
| `--conflict=<style>` | Conflict style | Rare |
| `--ignore-unmerged` | Don't abort on unmerged | Rare |

#### Behavior

| Flag | Description | Usage |
|------|-------------|-------|
| `-q`, `--quiet` | Suppress messages | Common |
| `--progress` | Enable progress | Rare |
| `--no-progress` | Disable progress | Rare |
| `--overlay` | Never remove files | Rare |
| `--no-overlay` | Remove missing files (default) | Rare |
| `--ignore-skip-worktree-bits` | Ignore sparse patterns | Rare |
| `--recurse-submodules` | Update submodules | Rare |
| `--no-recurse-submodules` | Don't update submodules (default) | Rare |

#### Pathspec

| Flag | Description | Usage |
|------|-------------|-------|
| `--pathspec-from-file=<file>` | Read paths from file | Rare |
| `--pathspec-file-nul` | NUL-separate paths | Rare |

---

### git branch

**Total flags:** ~30
**Documentation:** https://git-scm.com/docs/git-branch

#### Display

| Flag | Description | Usage |
|------|-------------|-------|
| `-v`, `--verbose` | Show sha1 and subject; -vv for more | Common |
| `--color[=<when>]` | Color output | Common |
| `--no-color` | Disable color | Rare |
| `-i`, `--ignore-case` | Case insensitive | Rare |
| `--omit-empty` | Omit empty format results | Exotic |
| `--column[=<options>]` | Column display | Rare |
| `--no-column` | Disable columns | Rare |
| `--sort=<key>` | Sort by key | Common |
| `-q`, `--quiet` | Suppress messages | Common |
| `--abbrev=<n>` | Abbreviation length | Rare |
| `--no-abbrev` | Full sha1 | Rare |
| `--format=<format>` | Output format | Rare |

#### Listing

| Flag | Description | Usage |
|------|-------------|-------|
| `-l`, `--list` | List mode | Common |
| `-r`, `--remotes` | Remote branches | Common |
| `-a`, `--all` | All branches | Common |
| `--show-current` | Current branch name | Common |
| `--contains [<commit>]` | Branches containing commit | Rare |
| `--no-contains [<commit>]` | Branches not containing | Rare |
| `--merged [<commit>]` | Merged branches | Common |
| `--no-merged [<commit>]` | Unmerged branches | Common |
| `--points-at <object>` | Branches at object | Rare |

#### Creation

| Flag | Description | Usage |
|------|-------------|-------|
| `-t`, `--track[=<mode>]` | Set upstream (direct/inherit) | Common |
| `--no-track` | No upstream | Rare |
| `-f`, `--force` | Force create/delete | Common |
| `--create-reflog` | Create reflog | Rare |
| `--no-create-reflog` | No reflog | Rare |
| `--recurse-submodules` | Recurse submodules | Rare |

#### Modification

| Flag | Description | Usage |
|------|-------------|-------|
| `-d`, `--delete` | Delete branch | Common |
| `-D` | Force delete | Common |
| `-m`, `--move` | Rename branch | Common |
| `-M` | Force rename | Common |
| `-c`, `--copy` | Copy branch | Rare |
| `-C` | Force copy | Rare |
| `-u <upstream>`, `--set-upstream-to=<upstream>` | Set upstream | Common |
| `--unset-upstream` | Remove upstream | Rare |
| `--edit-description` | Edit description | Rare |

---

## Cross-Command Flag Patterns

### Universal Flags

These flags appear across many commands with consistent meaning:

| Flag | Meaning | Commands |
|------|---------|----------|
| `-q`, `--quiet` | Suppress output | Most commands |
| `-v`, `--verbose` | Verbose output | Most commands |
| `-n`, `--dry-run` | Preview without action | add, rm, mv, clean, commit, checkout |
| `-f`, `--force` | Force operation | add, rm, mv, clean, checkout, branch, clone |
| `--progress` | Show progress | checkout, switch, clone |
| `--no-progress` | Hide progress | checkout, switch, clone |

### Diff-Related Flags

These flags are shared across diff-producing commands (diff, log, show, blame):

| Flag | Meaning |
|------|---------|
| `-p`, `--patch` | Generate patch |
| `--stat` | Diffstat |
| `--name-only` | File names only |
| `--name-status` | Names with status |
| `-U<n>`, `--unified=<n>` | Context lines |
| `--color[=<when>]` | Color output |
| `--no-color` | Disable color |
| `-w`, `--ignore-all-space` | Ignore whitespace |
| `-b`, `--ignore-space-change` | Ignore whitespace amount |
| `-M`, `--find-renames` | Rename detection |
| `-C`, `--find-copies` | Copy detection |

### Pathspec Flags

Commands accepting pathspec often support:

| Flag | Meaning |
|------|---------|
| `--pathspec-from-file=<file>` | Read paths from file |
| `--pathspec-file-nul` | NUL-separate paths |

Commands: add, rm, commit, checkout, restore, stash push

---

## Sources

- https://git-scm.com/docs/git-status
- https://git-scm.com/docs/git-add
- https://git-scm.com/docs/git-commit
- https://git-scm.com/docs/git-log
- https://git-scm.com/docs/git-diff
- https://git-scm.com/docs/git-init
- https://git-scm.com/docs/git-rev-parse
- https://git-scm.com/docs/git-show
- https://git-scm.com/docs/git-blame
- https://git-scm.com/docs/git-rm
- https://git-scm.com/docs/git-mv
- https://git-scm.com/docs/git-clean
- https://git-scm.com/docs/git-clone
- https://git-scm.com/docs/git-grep
- https://git-scm.com/docs/git-config
- https://git-scm.com/docs/git-stash
- https://git-scm.com/docs/git-checkout
- https://git-scm.com/docs/git-switch
- https://git-scm.com/docs/git-restore
- https://git-scm.com/docs/git-branch
