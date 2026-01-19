"""Handler for 'git rm' command."""

from common import ParsedCommand, run_sl


def handle(parsed: ParsedCommand) -> int:
    """
    Handle 'git rm' command.

    Translations:
    - git rm <files>   -> sl remove <files>
    - git rm -f        -> sl remove -f
    - git rm -r        -> sl remove (recursive by default)
    """
    # Filter out -r/--recursive - sl remove is recursive by default
    filtered_args = [a for a in parsed.args if a not in ('-r', '--recursive')]
    return run_sl(["remove"] + filtered_args)
