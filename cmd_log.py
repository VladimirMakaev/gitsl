"""Handler for 'git log' command."""

from common import ParsedCommand, run_sl


def handle(parsed: ParsedCommand) -> int:
    """
    Handle 'git log' command.

    Translates to 'sl log' and passes through all arguments.
    """
    return run_sl(["log"] + parsed.args)
