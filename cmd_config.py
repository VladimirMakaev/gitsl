"""Handler for 'git config' command."""

from common import ParsedCommand, run_sl


def handle(parsed: ParsedCommand) -> int:
    """
    Handle 'git config' command.

    Translations:
    - git config <key>          -> sl config <key>
    - git config <key> <value>  -> sl config --local <key> <value>
    - git config --list         -> sl config
    """
    args = list(parsed.args)

    # git config --list -> sl config (no args)
    if '--list' in args or '-l' in args:
        args = [a for a in args if a not in ('--list', '-l')]
        return run_sl(["config"] + args)

    # Count positional arguments (non-flag args)
    positional = [a for a in args if not a.startswith('-')]

    # If setting a value (key and value present)
    if len(positional) >= 2:
        # Check if scope already specified
        has_scope = any(a in args for a in ('--global', '--local', '--system', '--user'))
        if not has_scope:
            # Default to --local for writes (git's default)
            return run_sl(["config", "--local"] + args)

    return run_sl(["config"] + args)
