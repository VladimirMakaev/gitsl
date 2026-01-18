"""Handler for 'git status' command."""

from common import ParsedCommand, run_sl


def handle(parsed: ParsedCommand) -> int:
    """
    Handle 'git status' command.

    Translates to 'sl status' and passes through all arguments.
    """
    return run_sl(["status"] + parsed.args)
