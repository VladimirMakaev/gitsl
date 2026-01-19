"""Handler for 'git mv' command."""

from common import ParsedCommand, run_sl


def handle(parsed: ParsedCommand) -> int:
    """
    Handle 'git mv' command.

    Translations:
    - git mv <src> <dst> -> sl rename <src> <dst>
    - git mv -f          -> sl rename -f
    """
    return run_sl(["rename"] + parsed.args)
