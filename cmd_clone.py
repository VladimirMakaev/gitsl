"""Handler for 'git clone' command."""

from common import ParsedCommand, run_sl


def handle(parsed: ParsedCommand) -> int:
    """
    Handle 'git clone' command.

    Translations:
    - git clone <url>       -> sl clone <url>
    - git clone <url> <dir> -> sl clone <url> <dir>
    """
    return run_sl(["clone"] + parsed.args)
