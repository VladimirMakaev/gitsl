"""Handler for 'git stash' command."""

import re
import subprocess
import sys
from typing import Optional
from common import ParsedCommand, run_sl


def _get_most_recent_shelve() -> Optional[str]:
    """Get the name of the most recent shelve, or None if no shelves exist."""
    result = subprocess.run(
        ["sl", "shelve", "--list"],
        capture_output=True,
        text=True
    )
    if result.returncode != 0 or not result.stdout.strip():
        return None

    # Output format: "name    (age)    message"
    first_line = result.stdout.strip().split('\n')[0]
    # Name is first whitespace-separated token
    shelve_name = first_line.split()[0]
    return shelve_name


def _get_all_shelve_names() -> list:
    """Get list of shelve names in order (most recent first)."""
    result = subprocess.run(
        ["sl", "shelve", "--list"],
        capture_output=True, text=True
    )
    if result.returncode != 0 or not result.stdout.strip():
        return []

    names = []
    for line in result.stdout.strip().split('\n'):
        if line.strip():
            names.append(line.split()[0])
    return names


def _translate_stash_ref(ref: str) -> Optional[str]:
    """Convert git stash@{n} to sl shelve name."""
    match = re.match(r'stash@\{(\d+)\}', ref)
    if not match:
        return ref  # Not stash syntax, pass through

    index = int(match.group(1))
    shelves = _get_all_shelve_names()

    if index < len(shelves):
        return shelves[index]

    print(f"error: stash@{{{index}}} does not exist", file=sys.stderr)
    return None


def _handle_push(args: list) -> int:
    """Handle git stash push with flags."""
    sl_args = ['shelve']
    remaining = []
    quiet = False
    keep_index = False
    all_files = False

    i = 0
    while i < len(args):
        arg = args[i]

        if arg in ('-u', '--include-untracked'):
            sl_args.append('-u')  # STSH-01
            i += 1
            continue

        if arg in ('-m', '--message'):
            if i + 1 < len(args):
                sl_args.extend(['-m', args[i + 1]])  # STSH-02
                i += 2
                continue

        if arg in ('-p', '--patch'):
            sl_args.append('-i')  # STSH-05: translate to interactive
            i += 1
            continue

        if arg in ('-k', '--keep-index'):
            keep_index = True  # STSH-06
            i += 1
            continue

        if arg in ('-a', '--all'):
            all_files = True  # STSH-07
            sl_args.append('-u')  # At minimum include untracked
            i += 1
            continue

        if arg in ('-q', '--quiet'):
            quiet = True  # STSH-08
            i += 1
            continue

        # STSH-09: pathspec support - pass through
        remaining.append(arg)
        i += 1

    # Warnings
    if keep_index:
        print("Warning: -k/--keep-index has no effect. "
              "Sapling has no staging area; all changes are shelved.",
              file=sys.stderr)

    if all_files:
        print("Note: -a/--all includes untracked files. "
              "Ignored files may not be included.",
              file=sys.stderr)

    sl_args.extend(remaining)

    if quiet:
        result = subprocess.run(
            ['sl'] + sl_args,
            capture_output=True
        )
        return result.returncode

    return run_sl(sl_args)


def _handle_pop(args: list) -> int:
    """Handle git stash pop -> sl unshelve."""
    # STSH-04: Translate stash@{n} if present
    translated_args = []
    for arg in args:
        if arg.startswith('stash@{'):
            translated = _translate_stash_ref(arg)
            if translated is None:
                return 1
            translated_args.append(translated)
        else:
            translated_args.append(arg)
    return run_sl(["unshelve"] + translated_args)


def _handle_apply(args: list) -> int:
    """Handle git stash apply -> sl unshelve --keep."""
    # STSH-04: Translate stash@{n} if present
    translated_args = []
    for arg in args:
        if arg.startswith('stash@{'):
            translated = _translate_stash_ref(arg)
            if translated is None:
                return 1
            translated_args.append(translated)
        else:
            translated_args.append(arg)
    return run_sl(["unshelve", "--keep"] + translated_args)


def _handle_list(args: list) -> int:
    """Handle git stash list -> sl shelve --list."""
    return run_sl(["shelve", "--list"] + args)


def _handle_show(args: list) -> int:
    """Handle git stash show [--stat] [-p] [stash@{n}]."""
    show_stat = '--stat' in args
    show_patch = '-p' in args or '--patch' in args
    stash_ref = None

    for arg in args:
        if arg.startswith('stash@{'):
            stash_ref = _translate_stash_ref(arg)
            if stash_ref is None:
                return 1

    if stash_ref is None:
        stash_ref = _get_most_recent_shelve()

    if stash_ref is None:
        print("No stash entries found.", file=sys.stderr)
        return 1

    if show_patch:
        return run_sl(['shelve', '-p', stash_ref])
    elif show_stat:
        return run_sl(['shelve', '--stat', stash_ref])
    else:
        # Default: show stat (git's default)
        return run_sl(['shelve', '--stat', stash_ref])


def _handle_branch(args: list) -> int:
    """Handle git stash branch <name> [stash@{n}]."""
    if not args:
        print("error: stash branch requires a branch name", file=sys.stderr)
        return 1

    branch_name = args[0]
    stash_ref = args[1] if len(args) > 1 else None

    # Translate stash reference if provided
    shelve_name = None
    if stash_ref:
        shelve_name = _translate_stash_ref(stash_ref)
        if shelve_name is None:
            return 1
    else:
        shelve_name = _get_most_recent_shelve()
        if shelve_name is None:
            print("No stash entries found.", file=sys.stderr)
            return 1

    # Create bookmark at current commit
    result = run_sl(['bookmark', branch_name])
    if result != 0:
        return result

    # Unshelve (apply and delete)
    return run_sl(['unshelve', shelve_name])


def _handle_drop(args: list) -> int:
    """
    Handle git stash drop -> sl shelve --delete.

    git stash drop without args deletes most recent.
    sl shelve --delete requires a name.
    """
    if args:
        # STSH-04: Translate stash@{n} if present
        translated_args = []
        for arg in args:
            if arg.startswith('stash@{'):
                translated = _translate_stash_ref(arg)
                if translated is None:
                    return 1
                translated_args.append(translated)
            else:
                translated_args.append(arg)
        return run_sl(["shelve", "--delete"] + translated_args)

    # No args: delete most recent
    shelve_name = _get_most_recent_shelve()
    if shelve_name is None:
        print("No stash entries found.", file=sys.stderr)
        return 1

    return run_sl(["shelve", "--delete", shelve_name])


def handle(parsed: ParsedCommand) -> int:
    """
    Handle 'git stash' command.

    Translations:
    - git stash           -> sl shelve
    - git stash push      -> sl shelve
    - git stash -m "msg"  -> sl shelve -m "msg"
    - git stash pop       -> sl unshelve
    - git stash apply     -> sl unshelve --keep
    - git stash list      -> sl shelve --list
    - git stash drop      -> sl shelve --delete <most-recent>
    - git stash show      -> sl shelve --stat <most-recent>
    - git stash branch    -> sl bookmark + sl unshelve
    """
    args = list(parsed.args)

    # No subcommand = stash (same as push)
    if not args:
        return run_sl(["shelve"])

    subcommand = args[0]
    subargs = args[1:]

    if subcommand == "push":
        return _handle_push(subargs)

    if subcommand == "pop":
        return _handle_pop(subargs)

    if subcommand == "apply":
        return _handle_apply(subargs)

    if subcommand == "list":
        return _handle_list(subargs)

    if subcommand == "drop":
        return _handle_drop(subargs)

    if subcommand == "show":
        return _handle_show(subargs)

    if subcommand == "branch":
        return _handle_branch(subargs)

    # Check if first arg is a flag (e.g., -m) - treat as push
    if subcommand.startswith("-"):
        return _handle_push(args)

    # Unknown subcommand - pass through to shelve
    return run_sl(["shelve"] + args)
