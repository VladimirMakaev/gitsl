"""Handler for 'git commit' command."""

from common import ParsedCommand, run_sl


def handle(parsed: ParsedCommand) -> int:
    """
    Handle 'git commit' command.

    Translates to 'sl commit' and passes through all arguments.
    """
    return run_sl(["commit"] + parsed.args)
