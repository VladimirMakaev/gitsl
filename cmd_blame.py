"""Handler for 'git blame' command."""

from common import ParsedCommand, run_sl


def handle(parsed: ParsedCommand) -> int:
    """
    Handle 'git blame' command.

    Translations:
    - git blame <file>    -> sl annotate <file>
    - git blame -w <file> -> sl annotate -w <file>

    Note: sl has 'blame' as an alias for 'annotate'.
    """
    return run_sl(["annotate"] + parsed.args)
