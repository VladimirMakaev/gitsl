"""Handler for 'git checkout' command."""

import os
import subprocess
import sys
from typing import List, Optional, Tuple

from common import ParsedCommand, run_sl


def _is_valid_revision(arg: str, cwd: Optional[str] = None) -> bool:
    """
    Check if arg is a valid revision (bookmark, commit hash, or tag).

    Uses sl log -r to verify, which handles:
    - Full commit hashes
    - Partial commit hashes (if unique)
    - Bookmark names
    - Revset expressions
    """
    result = subprocess.run(
        ["sl", "log", "-r", arg, "-T", "{node}", "-l", "1"],
        capture_output=True,
        text=True,
        cwd=cwd
    )
    return result.returncode == 0


def _translate_goto_flags(args: List[str]) -> List[str]:
    """Translate git checkout flags to sl goto flags."""
    result = []
    for arg in args:
        if arg in ('-f', '--force'):
            # SAFE-02: git checkout -f -> sl goto -C (clean)
            result.append('-C')
        elif arg in ('-m', '--merge'):
            # SAFE-03: git checkout -m -> sl goto -m (same semantics)
            result.append('-m')
        else:
            result.append(arg)
    return result


def _split_at_separator(args: List[str]) -> Tuple[List[str], List[str]]:
    """
    Split args at -- separator.

    Returns (before, after) where:
    - before: args before -- (could be commit or flags)
    - after: args after -- (file paths)

    If no -- present, returns (args, []).
    """
    if "--" in args:
        idx = args.index("--")
        return args[:idx], args[idx + 1:]
    return args, []


def _handle_create_branch(args: List[str]) -> int:
    """
    Handle git checkout -b/-B <name> [<start-point>].

    Creates bookmark and switches to it.
    -B resets existing bookmark (sl bookmark updates by default).
    """
    branch_name = None
    start_point = None

    # Find -b or -B and extract branch name (next arg)
    i = 0
    while i < len(args):
        if args[i] in ("-b", "-B"):
            if i + 1 < len(args):
                branch_name = args[i + 1]
                # Check for start point (arg after branch name)
                if i + 2 < len(args) and not args[i + 2].startswith("-"):
                    start_point = args[i + 2]
            break
        i += 1

    if branch_name is None:
        print("error: switch `-b' requires a value", file=sys.stderr)
        return 128

    # If start point provided, goto it first
    if start_point:
        result = run_sl(["goto", start_point])
        if result != 0:
            return result

    # Create bookmark
    result = run_sl(["bookmark", branch_name])
    if result != 0:
        return result

    # Goto activates the bookmark
    return run_sl(["goto", branch_name])


def handle(parsed: ParsedCommand) -> int:
    """
    Handle 'git checkout' command.

    Translations:
    - git checkout <commit>        -> sl goto <commit>     (CHECKOUT-01)
    - git checkout <branch>        -> sl goto <bookmark>   (CHECKOUT-02)
    - git checkout <file>          -> sl revert <file>     (CHECKOUT-03)
    - git checkout -- <file>       -> sl revert <file>     (CHECKOUT-04)
    - git checkout -b <name>       -> sl bookmark + goto   (CHECKOUT-05)

    Disambiguation (CHECKOUT-06):
    1. If -- present: after is files
    2. If -b/-B present: create branch
    3. Otherwise: try as revision first, then file
    4. If both match: error, require --
    """
    args = list(parsed.args)

    # Handle no arguments
    if not args:
        print("error: you must specify a branch, commit, or file to checkout",
              file=sys.stderr)
        return 1

    # 1. Handle -b/-B flag first (CHECKOUT-05)
    if "-b" in args or "-B" in args:
        return _handle_create_branch(args)

    # 2. Split at -- separator
    before_sep, after_sep = _split_at_separator(args)

    # 3. If -- present, after_sep are file paths
    if after_sep:
        # Check if before_sep has a commit reference
        if before_sep and _is_valid_revision(before_sep[0]):
            # git checkout <commit> -- <file> -> sl revert -r <commit> <file>
            return run_sl(["revert", "-r", before_sep[0]] + after_sep)
        # Just restore files from working parent
        return run_sl(["revert"] + after_sep)

    # 4. No --, no -b - need to disambiguate
    target = args[0]
    remaining = args[1:]

    # Check if valid revision
    is_revision = _is_valid_revision(target)
    # Check if file/directory exists
    is_file = os.path.exists(target)

    # Ambiguous case: both branch/commit and file exist
    if is_revision and is_file:
        print(f"error: '{target}' could be both a ref and a file.",
              file=sys.stderr)
        print("Use -- to separate paths from revisions:", file=sys.stderr)
        print(f"  git checkout -- {target}", file=sys.stderr)
        return 1

    # Valid revision - switch to it (CHECKOUT-01, CHECKOUT-02)
    if is_revision:
        return run_sl(["goto"] + _translate_goto_flags(args))

    # File exists - restore it (CHECKOUT-03)
    if is_file:
        return run_sl(["revert"] + args)

    # Neither valid revision nor existing file
    # Let sl goto handle the error (better error message about what's wrong)
    return run_sl(["goto"] + _translate_goto_flags(args))
