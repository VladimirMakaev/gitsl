"""Handler for 'git status' command."""

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


def handle(parsed: ParsedCommand) -> int:
    """
    Handle 'git status' command.

    Special handling for --porcelain and --short flags to transform
    sl status output into git-compatible format.
    """
    # Check for porcelain/short flags
    needs_transform = '--porcelain' in parsed.args or '--short' in parsed.args or '-s' in parsed.args

    if needs_transform:
        # Remove git-specific flags before calling sl
        sl_args = [a for a in parsed.args
                   if a not in ('--porcelain', '--short', '-s')]

        result = subprocess.run(
            ['sl', 'status'] + sl_args,
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            transformed = transform_to_porcelain(result.stdout)
            sys.stdout.write(transformed)
        else:
            sys.stderr.write(result.stderr)

        return result.returncode

    # Default: passthrough to sl status
    return run_sl(['status'] + parsed.args)
