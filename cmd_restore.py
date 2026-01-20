"""Handler for 'git restore' command."""

from common import ParsedCommand, run_sl


def handle(parsed: ParsedCommand) -> int:
    """
    Handle 'git restore' command.

    Translations:
    - git restore <file>  -> sl revert <file>
    - git restore .       -> sl revert .

    Note: This handles working tree restoration only.
    git restore --staged is out of scope (not in Phase 17 requirements).
    """
    return run_sl(["revert"] + list(parsed.args))
