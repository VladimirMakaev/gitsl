"""Handler for 'git diff' command."""

from common import ParsedCommand, run_sl


def handle(parsed: ParsedCommand) -> int:
    """
    Handle 'git diff' command.

    Translates to 'sl diff' and passes through all arguments.
    """
    return run_sl(["diff"] + parsed.args)
