"""Handler for 'git status' command.

Supported flags:
- STAT-01: --ignored -> -i (show ignored files)
- STAT-02: -b/--branch -> prepend branch header
- STAT-03: -v/--verbose -> warning (different meaning in Sapling)
- STAT-04: --porcelain/--short/-s -> transform output (existing)
- STAT-05: -u/--untracked-files[=<mode>] -> filter untracked files
"""

import subprocess
import sys
from common import ParsedCommand, run_sl

# Status code translation: sl -> git porcelain XY format
# Key insight: sl has no staging area, so:
# - sl M (modified) -> git " M" (working tree change, not staged)
# - sl A (added) -> git "A " (staged addition)
# - sl R (removed) -> git "D " (staged deletion)
SL_TO_GIT_STATUS = {
    'M': ' M',  # Modified in working tree (not staged - sl has no staging)
    'A': 'A ',  # Added (will be committed - equivalent to staged in git)
    'R': 'D ',  # Removed (will be deleted - equivalent to staged deletion)
    '?': '??',  # Unknown/untracked
    '!': ' D',  # Missing (deleted from disk, not via sl rm)
    'I': '!!',  # Ignored (only with --ignored flag)
}


def parse_sl_status_line(line: str) -> tuple:
    """
    Parse a single sl status line.

    Args:
        line: Single line from sl status output, e.g., "M filename.txt"

    Returns:
        Tuple of (status_code, filename) or (None, None) if invalid

    Format: "X filename" where X is single char status
    """
    if not line or len(line) < 3:  # Minimum: "X f"
        return None, None

    if line[1] != ' ':  # Second char must be space
        return None, None

    status_code = line[0]
    filename = line[2:]

    return status_code, filename


def transform_to_porcelain(sl_output: str) -> str:
    """
    Transform sl status output to git porcelain v1 format.

    sl format:  "X filename" (1 char + space + filename)
    git format: "XY filename" (2 chars + space + filename)

    Args:
        sl_output: Complete output from 'sl status' command

    Returns:
        Git-compatible porcelain format output
    """
    lines = []

    for line in sl_output.splitlines():
        status_code, filename = parse_sl_status_line(line)

        if status_code is None:
            continue

        # Map sl status to git XY code
        git_code = SL_TO_GIT_STATUS.get(status_code, '??')

        # Format: XY<space>filename
        lines.append(f"{git_code} {filename}")

    # Return with trailing newline if there's content
    if lines:
        return '\n'.join(lines) + '\n'
    return ''


def get_branch_header() -> str:
    """Get git-style branch header for status output."""
    result = subprocess.run(
        ['sl', 'log', '-r', '.', '--template', '{activebookmark}'],
        capture_output=True,
        text=True
    )
    branch = result.stdout.strip() or '(detached)'
    return f"## {branch}\n"


def handle(parsed: ParsedCommand) -> int:
    """
    Handle 'git status' command.

    Special handling for --porcelain and --short flags to transform
    sl status output into git-compatible format.
    """
    sl_args = []
    needs_transform = False
    show_ignored = False
    show_branch = False
    verbose = False
    untracked_mode = 'normal'  # Default

    i = 0
    while i < len(parsed.args):
        arg = parsed.args[i]

        # Check for porcelain/short flags
        if arg in ('--porcelain', '--short', '-s'):
            needs_transform = True

        # STAT-01: --ignored -> sl status -i
        elif arg == '--ignored':
            show_ignored = True

        # STAT-02: -b/--branch - show branch info
        elif arg in ('-b', '--branch'):
            show_branch = True

        # STAT-03: -v/--verbose
        elif arg in ('-v', '--verbose'):
            verbose = True

        # STAT-05: -u/--untracked-files[=<mode>]
        elif arg.startswith('--untracked-files'):
            if '=' in arg:
                untracked_mode = arg.split('=', 1)[1]
            else:
                untracked_mode = 'all'  # git default when no value
        elif arg == '-u':
            # Check for separate value
            if i + 1 < len(parsed.args) and parsed.args[i + 1] in ('no', 'normal', 'all'):
                i += 1
                untracked_mode = parsed.args[i]
            else:
                untracked_mode = 'all'
        elif arg.startswith('-u') and len(arg) > 2:
            # Attached value: -uno, -unormal, -uall
            untracked_mode = arg[2:]

        else:
            sl_args.append(arg)

        i += 1

    # Build sl status command with appropriate flags
    if show_ignored:
        sl_args.append('-i')

    # Handle untracked mode
    if untracked_mode == 'no':
        # Only tracked file changes: modified, added, removed, deleted
        sl_args.append('-mard')

    # Handle verbose flag (different meaning between git and sl)
    if verbose:
        print("Note: Sapling -v shows repo state info, not staged diffs. "
              "Use 'sl diff' to see all uncommitted changes.",
              file=sys.stderr)

    if needs_transform:
        result = subprocess.run(
            ['sl', 'status'] + sl_args,
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            output = ''
            # Add branch header if requested
            if show_branch:
                output += get_branch_header()
            output += transform_to_porcelain(result.stdout)
            sys.stdout.write(output)
        else:
            sys.stderr.write(result.stderr)

        return result.returncode

    # Non-porcelain mode
    if show_branch:
        # For normal status output with -b, prepend branch info
        branch_header = get_branch_header()
        sys.stdout.write(branch_header)

    return run_sl(['status'] + sl_args)
