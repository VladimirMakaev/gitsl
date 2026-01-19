"""Handler for 'git show' command."""

from common import ParsedCommand, run_sl


def handle(parsed: ParsedCommand) -> int:
    """
    Handle 'git show' command.

    Translations:
    - git show          -> sl show (current commit)
    - git show <commit> -> sl show <commit>

    Common flags pass through: --stat, -U<n>, -w
    """
    return run_sl(["show"] + parsed.args)
