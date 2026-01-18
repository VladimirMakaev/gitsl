"""Handler for 'git init' command."""

from common import ParsedCommand, run_sl


def handle(parsed: ParsedCommand) -> int:
    """
    Handle 'git init' command.

    Translates to 'sl init' and passes through all arguments.
    """
    return run_sl(["init"] + parsed.args)
