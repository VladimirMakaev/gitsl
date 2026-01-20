"""Handler for 'git commit' command."""

from common import ParsedCommand, run_sl


def handle(parsed: ParsedCommand) -> int:
    """
    Handle 'git commit' command.

    Translates to 'sl commit' and passes through arguments.
    """
    args = list(parsed.args)

    # SAFE-01: Remove -a/--all flags
    # git -a: stages tracked modified/deleted files only
    # sl -A: adds untracked files too (DANGEROUS semantic difference)
    args = [a for a in args if a not in ('-a', '--all')]

    return run_sl(["commit"] + args)
