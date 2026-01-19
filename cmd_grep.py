"""Handler for 'git grep' command."""

from common import ParsedCommand, run_sl


def handle(parsed: ParsedCommand) -> int:
    """
    Handle 'git grep' command.

    Translations:
    - git grep <pattern>     -> sl grep <pattern>
    - git grep -n <pattern>  -> sl grep -n <pattern>
    - git grep -i <pattern>  -> sl grep -i <pattern>
    - git grep -l <pattern>  -> sl grep -l <pattern>
    """
    return run_sl(["grep"] + parsed.args)
